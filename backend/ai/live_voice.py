import os
import json
import asyncio
import websockets
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Any

from .memory import memory_manager

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Using the experimental model which supports the Multimodal Live API
GEMINI_LIVE_URL = f"wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key={GEMINI_API_KEY}"

async def stream_live_voice(websocket: WebSocket, user_id: str):
    """
    Handles a full-duplex live voice session.
    Proxies audio between the FastAPI WebSocket (Frontend) and the Gemini Live API.
    """
    await websocket.accept()

    if not GEMINI_API_KEY:
        await websocket.send_json({"type": "error", "message": "Gemini API Key missing."})
        await websocket.close()
        return

    try:
        # Connect to Gemini Live API
        async with websockets.connect(GEMINI_LIVE_URL) as gemini_ws:
            
            # 1. Send Initial Setup
            setup_msg = {
                "setup": {
                    "model": "models/gemini-2.0-flash-exp",
                    "systemInstruction": {
                        "parts": [{"text": "You are ThinkLIE, a highly responsive, conversational AI assistant. Keep responses extremely concise and natural for voice conversation. If the user interrupts, stop talking immediately. If you need knowledge, you have access to a RAG retrieval tool."}]
                    },
                    "tools": [{
                        "functionDeclarations": [{
                            "name": "retrieve_knowledge",
                            "description": "Searches the user's Long-Term Memory (ChromaDB) for relevant context.",
                            "parameters": {
                                "type": "OBJECT",
                                "properties": {
                                    "query": {
                                        "type": "STRING",
                                        "description": "The search query"
                                    }
                                },
                                "required": ["query"]
                            }
                        }]
                    }]
                }
            }
            await gemini_ws.send(json.dumps(setup_msg))
            
            # Wait for Setup Complete
            setup_response = await gemini_ws.recv()
            print("[Live Voice] Gemini Setup Response:", setup_response)

            # Inform frontend we are ready
            await websocket.send_json({"type": "status", "state": "Listening"})

            # Tasks
            async def receive_from_frontend():
                try:
                    while True:
                        msg = await websocket.receive()
                        if "bytes" in msg:
                            # Forward PCM Audio chunk to Gemini
                            import base64
                            b64_audio = base64.b64encode(msg["bytes"]).decode("utf-8")
                            realtime_input = {
                                "realtimeInput": {
                                    "mediaChunks": [{
                                        "mimeType": "audio/pcm;rate=16000",
                                        "data": b64_audio
                                    }]
                                }
                            }
                            await gemini_ws.send(json.dumps(realtime_input))
                        elif "text" in msg:
                            data = json.loads(msg["text"])
                            if data.get("type") == "clientContent":
                                await gemini_ws.send(json.dumps({
                                    "clientContent": {
                                        "turns": [{"role": "user", "parts": [{"text": data["text"]}]}],
                                        "turnComplete": True
                                    }
                                }))
                except WebSocketDisconnect:
                    print("[Live Voice] Frontend disconnected.")
                except Exception as e:
                    print(f"[Live Voice] Frontend Error: {e}")

            async def receive_from_gemini():
                try:
                    while True:
                        response = await gemini_ws.recv()
                        data = json.loads(response)

                        if "serverContent" in data:
                            model_turn = data["serverContent"].get("modelTurn", {})
                            parts = model_turn.get("parts", [])
                            
                            for part in parts:
                                # Relay Audio back to Frontend
                                if "inlineData" in part:
                                    mime = part["inlineData"].get("mimeType", "")
                                    if mime.startswith("audio/pcm"):
                                        b64_out = part["inlineData"]["data"]
                                        await websocket.send_json({"type": "audio", "data": b64_out})
                                
                                # Relay Text Transcript (Optional)
                                if "text" in part:
                                    await websocket.send_json({"type": "text", "text": part["text"]})
                            
                            # Handle Interruption (Turn Complete)
                            if data["serverContent"].get("turnComplete"):
                                await websocket.send_json({"type": "turnComplete"})

                        # Handle Function Calling (RAG)
                        elif "toolCall" in data:
                            tool_calls = data["toolCall"]["functionCalls"]
                            responses = []
                            for call in tool_calls:
                                name = call["name"]
                                call_id = call["id"]
                                args = call.get("args", {})
                                
                                if name == "retrieve_knowledge":
                                    query = args.get("query", "")
                                    print(f"[Live Voice] RAG Query triggered: {query}")
                                    results = memory_manager.retrieve_long_term_memory(user_id, query)
                                    context = "\n".join(results) if results else "No relevant memories found."
                                    
                                    responses.append({
                                        "id": call_id,
                                        "name": name,
                                        "response": {"result": context}
                                    })
                            
                            # Send tool response back to Gemini
                            tool_response_msg = {
                                "toolResponse": {
                                    "functionResponses": responses
                                }
                            }
                            await gemini_ws.send(json.dumps(tool_response_msg))

                except websockets.exceptions.ConnectionClosed:
                    print("[Live Voice] Gemini closed connection.")
                except Exception as e:
                    print(f"[Live Voice] Gemini Error: {e}")

            # Run both bidirectional streams concurrently
            await asyncio.gather(receive_from_frontend(), receive_from_gemini())

    except Exception as e:
        print(f"[Live Voice] Initialization failed: {e}")
        try:
            await websocket.close()
        except:
            pass
