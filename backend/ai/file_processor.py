import fitz  # PyMuPDF
from typing import Dict, Any
from google.genai import types

class FileProcessor:
    def __init__(self):
        pass

    async def process(self, file_bytes: bytes, file_type: str, query: str, client: Any) -> Dict[str, Any]:
        """
        Routes the file based on mime type to the appropriate extractor.
        Returns { "type": str, "content": str, "metadata": dict }
        """
        if not file_bytes:
            return None

        # 1. Images
        if file_type and file_type.startswith("image/"):
            return self._process_image(file_bytes, file_type, query, client)
        
        # 2. PDF Documents
        elif file_type == "application/pdf":
            return self._process_pdf(file_bytes)
        
        # 3. Plain Text / Markdown / CSV
        elif file_type and (file_type.startswith("text/") or file_type in ["application/json", "application/csv"]):
            return self._process_text(file_bytes)
            
        # 4. Audio
        elif file_type and file_type.startswith("audio/"):
            return self._process_audio(file_bytes, file_type, query, client)
        
        # Fallback
        return {
            "type": "unknown",
            "content": "[Unsupported file type provided.]",
            "metadata": {}
        }

    def _process_image(self, file_bytes: bytes, mime_type: str, query: str, client: Any) -> Dict[str, Any]:
        """ Uses Gemini Vision to understand the image dynamically based on the user's query. """
        if not client:
            return {"type": "image", "content": "[Image provided but no AI client configured to read it.]", "metadata": {}}
            
        try:
            # Prepare instructions for Vision Model
            image_prompt = (
                f"Analyze this image carefully. The user asked: '{query}'. "
                "Provide a highly detailed extraction or description of the image content that explicitly answers or aids in answering their query. "
                "If it's code, extract the code. If it's a diagram, explain the flow."
            )
            
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=[
                    types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                    image_prompt
                ]
            )
            return {
                "type": "image",
                "content": response.text,
                "metadata": {"source": "gemini_vision", "mime": mime_type}
            }
        except Exception as e:
            print(f"[FileProcessor] Image processing error: {e}")
            return {"type": "image", "content": f"[Error processing image: {e}]", "metadata": {}}

    def _process_pdf(self, file_bytes: bytes) -> Dict[str, Any]:
        """ Extracts text from a PDF document using PyMuPDF. """
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            extracted_text = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                if text:
                    extracted_text.append(f"--- Page {page_num + 1} ---\n{text}")
            
            doc.close()
            full_text = "\n".join(extracted_text)
            
            return {
                "type": "pdf",
                "content": full_text if full_text.strip() else "[No extractable text found in PDF]",
                "metadata": {"pages": len(doc)}
            }
        except Exception as e:
            print(f"[FileProcessor] PDF processing error: {e}")
            return {"type": "pdf", "content": f"[Error processing PDF: {e}]", "metadata": {}}

    def _process_text(self, file_bytes: bytes) -> Dict[str, Any]:
        try:
            text = file_bytes.decode('utf-8')
            return {
                "type": "text",
                "content": text,
                "metadata": {"length": len(text)}
            }
        except Exception as e:
            return {"type": "text", "content": "[Error decoding text file. Ensure it is UTF-8.]", "metadata": {}}

    def _process_audio(self, file_bytes: bytes, mime_type: str, query: str, client: Any) -> Dict[str, Any]:
        """ Uses Gemini to transcribe and understand the audio dynamically. """
        if not client:
            return {"type": "audio", "content": "[Audio provided but no AI client configured to read it.]", "metadata": {}}
            
        try:
            audio_prompt = (
                f"Analyze this audio explicitly. The user might be speaking to you or asking a question via a voice note. The query provided along with it is: '{query}'. "
                "Provide a precise transcription or extract the intent and generate a response that specifically addresses it."
            )
            
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=[
                    types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                    audio_prompt
                ]
            )
            return {
                "type": "audio",
                "content": response.text,
                "metadata": {"source": "gemini_audio", "mime": mime_type}
            }
        except Exception as e:
            print(f"[FileProcessor] Audio processing error: {e}")
            return {"type": "audio", "content": f"[Error processing audio: {e}]", "metadata": {}}

file_processor = FileProcessor()
