import os
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime, timedelta, timezone
from typing import Optional, List

from fastapi import FastAPI, Depends, HTTPException, status, Form, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from jose import JWTError, jwt
import bcrypt
from google import genai
import uuid

from sqlalchemy import create_engine, Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship

# =================================================
# ENV & CONFIG
# =================================================
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# =================================================
# Persistent Directories Setup
# =================================================
os.makedirs("data", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

# =================================================
# DATABASE
# =================================================
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./think_alie.db")

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # Handle older 'postgres://' schema prefix if needed
    if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    profile = relationship("UserProfile", back_populates="user", uselist=False)

class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    skills = Column(Text, default="")
    goals = Column(Text, default="")
    preferences = Column(Text, default="")
    user = relationship("User", back_populates="profile")

class Chat(Base):
    __tablename__ = "chats"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False, default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    chat_id = Column(String, ForeignKey("chats.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=False) # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class MessageIndex(Base):
    __tablename__ = "message_index"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    token = Column(String, index=True, nullable=False)
    chat_id = Column(String, ForeignKey("chats.id"), nullable=False)
    message_id = Column(String, ForeignKey("messages.id"), nullable=False)
    positions = Column(String, nullable=False) # JSON encoded list of integers

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =================================================
# AUTHENTICATION
# =================================================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

# =================================================
# FASTAPI APP
# =================================================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex="https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =================================================
# SCHEMAS
# =================================================
class UserCreate(BaseModel):
    email: str
    password: str

class ChatRequest(BaseModel):
    message: str

# =================================================
# AUTH ENDPOINTS
# =================================================
@app.post("/auth/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

@app.post("/auth/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.id, "email": db_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user": {"id": db_user.id, "email": db_user.email}}

@app.post("/auth/token")
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Standard OAuth2 endpoint for Swagger UI
    db_user = db.query(User).filter(User.email == form_data.username).first()
    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.id, "email": db_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email}

import re
import json

def index_message(db: Session, message_id: str, chat_id: str, content: str):
    if not content: return
    # Find all words (alphanumeric sequences)
    words = re.findall(r'\b\w+\b', content.lower())
    idx = {}
    for pos, word in enumerate(words):
        if word not in idx:
            idx[word] = []
        idx[word].append(pos)
    
    for word, positions in idx.items():
        mi = MessageIndex(token=word, chat_id=chat_id, message_id=message_id, positions=json.dumps(positions))
        db.add(mi)
    db.commit()

# =================================================
# CHAT ENDPOINTS
# =================================================
from sqlalchemy import func

@app.get("/api/search")
def search_chats(q: str = Query(""), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not q.strip():
        return {"results": []}
    
    words = re.findall(r'\b\w+\b', q.lower())
    if not words:
        return {"results": []}
    
    # Simple ranking: chats that have the most occurrences of any search token
    # Get user's chats
    user_chat_ids = [c.id for c in db.query(Chat.id).filter(Chat.user_id == current_user.id).all()]
    if not user_chat_ids:
        return {"results": []}

    # Query index for matching tokens
    matches = db.query(
        MessageIndex.chat_id,
        func.count(MessageIndex.id).label('hit_count')
    ).filter(
        MessageIndex.chat_id.in_(user_chat_ids),
        MessageIndex.token.in_(words)
    ).group_by(MessageIndex.chat_id).order_by(func.count(MessageIndex.id).desc()).limit(10).all()
    
    results = []
    for chat_id, hit_count in matches:
        chat = db.query(Chat).filter(Chat.id == chat_id).first()
        if chat:
            results.append({
                "chat_id": chat.id,
                "title": chat.title,
                "hits": hit_count
            })
            
    return {"results": results}

@app.post("/api/chats")
def create_chat(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_chat = Chat(user_id=current_user.id, title="New Chat")
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return {"chat": {"id": new_chat.id, "title": new_chat.title, "created_at": new_chat.created_at}}

@app.get("/api/chats")
def list_chats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    chats = db.query(Chat).filter(Chat.user_id == current_user.id).order_by(Chat.created_at.desc()).all()
    return {"chats": [{"id": c.id, "title": c.title, "created_at": c.created_at} for c in chats]}

@app.get("/api/chats/{chat_id}/messages")
def get_messages(chat_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    messages = db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at.asc()).all()
    return [{"id": m.id, "role": m.role, "content": m.content, "created_at": m.created_at} for m in messages]

@app.post("/api/chats/{chat_id}/message")
async def send_message(
    chat_id: str,
    message: str = Form(""),
    file: UploadFile = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    if chat.title == "New Chat":
        try:
            if client and message:
                title_prompt = f"Generate a short, concise title (3 to 5 words max) for a chat that starts with this message. Respond with JUST the title, no quotes or intro: '{message}'"
                title_response = client.models.generate_content(
                    model="gemini-2.5-flash-lite", 
                    contents=title_prompt
                )
                chat.title = title_response.text.strip().replace('"', '')
            else:
                chat.title = str(message)[:30] + ("..." if len(message) > 30 else "")
        except Exception:
            chat.title = str(message)[:30] + ("..." if len(message) > 30 else "")
        db.commit()

    # Save user message
    user_msg = Message(chat_id=chat_id, user_id=current_user.id, role="user", content=message)
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)
    index_message(db, user_msg.id, chat_id, message)

    # Fetch history for context
    history_records = db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at.asc()).all()
    history = [{"role": m.role, "content": m.content} for m in history_records]

    async def event_stream():
        import json
        yield f"data: {json.dumps({'type': 'title', 'title': chat.title})}\n\n"
        
        full_ai_response = ""
        if not client:
            full_ai_response = "Gemini API not configured. Check your .env file."
            yield f"data: {json.dumps({'type': 'chunk', 'text': full_ai_response})}\n\n"
        else:
            try:
                from ai.orchestrator import orchestrator
                file_bytes = await file.read() if file else None
                file_type = file.content_type if file else None
                
                async for text_chunk in orchestrator.generate_response_stream(
                    query=message, 
                    history=history, 
                    client=client,
                    user_id=current_user.id,
                    session_id=chat_id,
                    file_bytes=file_bytes,
                    file_type=file_type
                ):
                    full_ai_response += text_chunk
                    yield f"data: {json.dumps({'type': 'chunk', 'text': text_chunk})}\n\n"
            except Exception as e:
                err = f"RAG Pipeline Error: {str(e)}"
                full_ai_response += err
                yield f"data: {json.dumps({'type': 'chunk', 'text': err})}\n\n"
        
        # Save assistant message to DB after stream completes
        try:
            # Need a new session because generator runs outside the request context
            from app import SessionLocal, Message
            with SessionLocal() as stream_db:
                ai_msg = Message(chat_id=chat_id, user_id=current_user.id, role="assistant", content=full_ai_response)
                stream_db.add(ai_msg)
                stream_db.commit()
                stream_db.refresh(ai_msg)
                index_message(stream_db, ai_msg.id, chat_id, full_ai_response)
        except Exception as e:
            print(f"Error saving AI message: {e}")

    from fastapi.responses import StreamingResponse
    return StreamingResponse(event_stream(), media_type="text/event-stream")

# =================================================
# LIVE VOICE WEBSOCKET
# =================================================
from fastapi import WebSocket, WebSocketDisconnect, Query
from ai.live_voice import stream_live_voice

@app.websocket("/api/live-voice")
async def websocket_live_voice(websocket: WebSocket, token: str = Query(None), db: Session = Depends(get_db)):
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
        
    try:
        user = get_current_user(token=token, db=db)
    except HTTPException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Pass connection to the Live Voice handler
    await stream_live_voice(websocket, user.id)

# =================================================
# API ENDPOINTS ONLY - FRONTEND IS DECOUPLED
# =================================================
