import os
import json
import asyncio
import base64
import websockets
from fastapi import WebSocket, WebSocketDisconnect

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_LIVE_URL = (
    f"wss://generativelanguage.googleapis.com/ws/"
    f"google.ai.generativelanguage.v1alpha.GenerativeService"
    f".BidiGenerateContent?key={GEMINI_API_KEY}"
)

SYSTEM_INSTRUCTION = (
    "You are ThinkLIE, a highly responsive conversational AI. "
    "Keep responses concise and natural for voice conversation. "
    "If the user interrupts, stop immediately. "
    "Be helpful, smart, and human-like."
)


async def stream_live_voice(websocket: WebSocket, user_id: str):
    """
    Full-duplex live voice session.
    Proxies audio between the browser WebSocket and the Gemini Live API.
    """
    await websocket.accept()

    if not GEMINI_API_KEY:
        await websocket.send_json({"type": "error", "message": "Gemini API Key not configured."})
        await websocket.close()
        return

    # ── State ──────────────────────────────────────────────────────────────────
    interrupted = asyncio.Event()   # set when user speaks over AI
    stop_event  = asyncio.Event()   # set when frontend disconnects

    try:
        async with websockets.connect(
            GEMINI_LIVE_URL,
            ping_interval=20,
            ping_timeout=10,
        ) as gemini_ws:

            # 1 ── Send setup ─────────────────────────────────────────────────
            setup = {
                "setup": {
                    "model": "models/gemini-2.0-flash-exp",
                    "generationConfig": {
                        "responseModalities": ["AUDIO"],
                        "speechConfig": {
                            "voiceConfig": {
                                "prebuiltVoiceConfig": {"voiceName": "Aoede"}
                            }
                        }
                    },
                    "systemInstruction": {
                        "parts": [{"text": SYSTEM_INSTRUCTION}]
                    },
                }
            }
            await gemini_ws.send(json.dumps(setup))

            # Wait for setupComplete
            setup_resp = await asyncio.wait_for(gemini_ws.recv(), timeout=10)
            print("[LiveVoice] Setup response:", setup_resp[:120])

            # Notify frontend that we are ready
            await websocket.send_json({"type": "status", "state": "listening"})

            # ── Task: Frontend → Gemini ───────────────────────────────────────
            async def from_frontend():
                try:
                    while not stop_event.is_set():
                        msg = await websocket.receive()

                        if "bytes" in msg and msg["bytes"]:
                            # Raw PCM audio from browser microphone
                            b64 = base64.b64encode(msg["bytes"]).decode()
                            await gemini_ws.send(json.dumps({
                                "realtimeInput": {
                                    "mediaChunks": [{
                                        "mimeType": "audio/pcm;rate=16000",
                                        "data": b64
                                    }]
                                }
                            }))

                        elif "text" in msg:
                            try:
                                data = json.loads(msg["text"])
                            except Exception:
                                continue

                            action = data.get("type", "")

                            if action == "interrupt":
                                # User spoke while AI was speaking → force turn end
                                interrupted.set()
                                await gemini_ws.send(json.dumps({
                                    "clientContent": {
                                        "turns": [{
                                            "role": "user",
                                            "parts": [{"text": "[interrupted]"}]
                                        }],
                                        "turnComplete": True
                                    }
                                }))
                                await websocket.send_json({"type": "status", "state": "listening"})

                            elif action == "text":
                                # Text message sent via live voice
                                await gemini_ws.send(json.dumps({
                                    "clientContent": {
                                        "turns": [{
                                            "role": "user",
                                            "parts": [{"text": data.get("text", "")}]
                                        }],
                                        "turnComplete": True
                                    }
                                }))

                        elif msg.get("type") == "websocket.disconnect":
                            break

                except WebSocketDisconnect:
                    print("[LiveVoice] Frontend disconnected.")
                except Exception as e:
                    print(f"[LiveVoice] from_frontend error: {e}")
                finally:
                    stop_event.set()

            # ── Task: Gemini → Frontend ───────────────────────────────────────
            async def from_gemini():
                try:
                    while not stop_event.is_set():
                        try:
                            raw = await asyncio.wait_for(gemini_ws.recv(), timeout=30)
                        except asyncio.TimeoutError:
                            # Send heartbeat to keep connection alive
                            await websocket.send_json({"type": "ping"})
                            continue

                        data = json.loads(raw)

                        if "serverContent" in data:
                            sc = data["serverContent"]
                            model_turn = sc.get("modelTurn", {})

                            # Notify frontend: AI is now speaking
                            if model_turn.get("parts"):
                                await websocket.send_json({"type": "status", "state": "speaking"})

                            for part in model_turn.get("parts", []):
                                # Relay audio chunk to browser
                                if "inlineData" in part:
                                    mime = part["inlineData"].get("mimeType", "")
                                    if "audio" in mime:
                                        await websocket.send_json({
                                            "type": "audio",
                                            "data": part["inlineData"]["data"]
                                        })
                                # Relay transcript text (optional display)
                                if "text" in part:
                                    await websocket.send_json({
                                        "type": "transcript",
                                        "text": part["text"]
                                    })

                            if sc.get("turnComplete"):
                                interrupted.clear()
                                await websocket.send_json({"type": "turnComplete"})
                                await websocket.send_json({"type": "status", "state": "listening"})

                        elif "toolCall" in data:
                            # Simple fallback — acknowledge tool calls we don't support
                            calls = data["toolCall"].get("functionCalls", [])
                            responses = [
                                {"id": c["id"], "name": c["name"],
                                 "response": {"result": "Not available in voice mode."}}
                                for c in calls
                            ]
                            await gemini_ws.send(json.dumps({
                                "toolResponse": {"functionResponses": responses}
                            }))

                        elif "error" in data:
                            msg = data["error"].get("message", "Unknown error from Gemini.")
                            await websocket.send_json({"type": "error", "message": msg})

                except websockets.exceptions.ConnectionClosed as e:
                    print(f"[LiveVoice] Gemini connection closed: {e}")
                except Exception as e:
                    print(f"[LiveVoice] from_gemini error: {e}")
                finally:
                    stop_event.set()

            # Run both directions concurrently
            await asyncio.gather(from_frontend(), from_gemini())

    except Exception as e:
        print(f"[LiveVoice] Initialization failed: {e}")
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
            await websocket.close()
        except Exception:
            pass
