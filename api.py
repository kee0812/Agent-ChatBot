"""
聊天機器人 API 服務
提供 RESTful API 接口來訪問聊天機器人功能
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app import ChatbotApp
import logging
from logger import get_logger
from enum import Enum
import uuid
import time
from datetime import datetime

# 創建 FastAPI 應用
app = FastAPI(
    title="聊天機器人 API",
    description="提供聊天機器人的 RESTful API 接口",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生產環境中應該設置具體的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化聊天機器人
chatbot = ChatbotApp()
logger = get_logger("api")

# 保存對話記錄的簡單內存存儲
conversation_store = {}

class ModelType(str, Enum):
    """支持的模型類型"""
    GPT4_MINI = "gpt-4o-mini"
    GPT4 = "gpt-4"
    GPT35_TURBO = "gpt-3.5-turbo"

class ResponseType(str, Enum):
    """回應類型"""
    WEATHER = "weather"
    TRANSLATION = "translation"
    MODEL = "model"

class ChatRequest(BaseModel):
    """聊天請求模型"""
    message: str = Field(..., description="用戶輸入的消息")
    model: ModelType = Field(default=ModelType.GPT4_MINI, description="要使用的模型")
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="模型溫度參數，控制輸出的隨機性"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=lambda: {},
        description="用於記錄對話歷史的元數據，應包含user_id和session_id"
    )

class ChatResponse(BaseModel):
    """聊天回應模型"""
    message: str = Field(..., description="機器人的回應內容")
    type: ResponseType = Field(..., description="回應類型")
    model_used: str = Field(..., description="實際使用的模型")
    processing_time: float = Field(..., description="處理時間（秒）")
    timestamp: str = Field(..., description="回應時間戳")
    conversation_id: str = Field(..., description="對話ID")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="回應相關的元數據，包含用戶ID和會話ID"
    )

def get_or_create_session_id(metadata: Dict[str, Any]) -> str:
    """獲取或創建會話ID"""
    if metadata and "session_id" in metadata:
        return metadata["session_id"]
    return str(uuid.uuid4())

def get_or_create_user_id(metadata: Dict[str, Any]) -> str:
    """獲取或創建用戶ID"""
    if metadata and "user_id" in metadata:
        return metadata["user_id"]
    return f"anonymous_{str(uuid.uuid4())[:8]}"

def log_conversation(user_id: str, session_id: str, request_message: str, response_message: str):
    """記錄對話歷史"""
    if session_id not in conversation_store:
        conversation_store[session_id] = []
    
    conversation_store[session_id].append({
        "user_id": user_id,
        "timestamp": datetime.now().isoformat(),
        "request": request_message,
        "response": response_message
    })
    
    # 只保留最近100條記錄
    if len(conversation_store[session_id]) > 100:
        conversation_store[session_id] = conversation_store[session_id][-100:]

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    處理聊天請求
    
    Args:
        request: 包含用戶消息和配置參數的請求對象
        
    Returns:
        包含機器人回應和元數據的響應對象
    """
    try:
        start_time = time.time()
        
        # 獲取或創建會話ID和用戶ID
        session_id = get_or_create_session_id(request.metadata)
        user_id = get_or_create_user_id(request.metadata)
        
        logger.info(f"收到聊天請求: 用戶ID={user_id}, 會話ID={session_id}, 消息={request.message}")
        
        # 獲取對話歷史
        conversation_history = get_conversation_history_for_model(session_id)
        logger.debug(f"已獲取對話歷史，共 {len(conversation_history)} 條")
        
        # 處理聊天請求
        response = chatbot.process_query(
            request.message,
            model_name=request.model.value,
            temperature=request.temperature,
            conversation_history=conversation_history
        )
        
        # 獲取回應類型
        response_type = ResponseType.MODEL  # 默認為一般模型回應
        if "天氣" in request.message or "weather" in request.message.lower():
            response_type = ResponseType.WEATHER
        elif "翻譯" in request.message or "translate" in request.message.lower():
            response_type = ResponseType.TRANSLATION
            
        processing_time = time.time() - start_time
        timestamp = datetime.now().isoformat()
        
        # 記錄對話
        log_conversation(user_id, session_id, request.message, response.content)
        
        logger.info(f"生成回應，用戶ID={user_id}, 會話ID={session_id}, 類型={response_type}，處理時間={processing_time:.2f}秒")
        
        return ChatResponse(
            message=response.content,
            type=response_type,
            model_used=request.model.value,
            processing_time=processing_time,
            timestamp=timestamp,
            conversation_id=session_id,
            metadata={
                "user_id": user_id,
                "session_id": session_id,
                "temperature": request.temperature,
                "message_count": len(conversation_store.get(session_id, []))
            }
        )
        
    except Exception as e:
        logger.error(f"處理請求時發生錯誤: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

def get_conversation_history_for_model(session_id: str, max_history: int = 10) -> list:
    """
    獲取格式化的對話歷史以供模型使用
    
    Args:
        session_id: 會話ID
        max_history: 最大歷史消息數量
        
    Returns:
        格式化的對話歷史列表
    """
    if session_id not in conversation_store:
        return []
    
    # 獲取最近的歷史記錄（限制數量以避免超過上下文限制）
    recent_history = conversation_store[session_id][-max_history:] if len(conversation_store[session_id]) > max_history else conversation_store[session_id]
    
    # 轉換為模型可用的格式
    formatted_history = []
    for msg in recent_history:
        formatted_history.append({"role": "user", "content": msg["request"]})
        formatted_history.append({"role": "assistant", "content": msg["response"]})
    
    return formatted_history

@app.get("/conversations/{session_id}")
async def get_conversation_history(session_id: str):
    """獲取特定會話的對話歷史"""
    if session_id not in conversation_store:
        raise HTTPException(status_code=404, detail=f"找不到會話ID: {session_id}")
    
    return {
        "session_id": session_id,
        "messages": conversation_store[session_id],
        "message_count": len(conversation_store[session_id])
    }

@app.get("/models")
async def list_models():
    """獲取支持的模型列表"""
    return {
        "models": [model.value for model in ModelType],
        "default_model": ModelType.GPT4_MINI.value
    }

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 