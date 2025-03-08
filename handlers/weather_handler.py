"""
天氣回應處理器
用於處理與天氣相關的查詢請求
"""

from langchain_core.messages import AIMessage
from langgraph.graph import MessagesState
from typing import Dict, List
from handlers.base_handler import ResponseHandler
from logger import get_logger

class WeatherResponseHandler(ResponseHandler):
    """處理天氣相關查詢的回應生成器"""
    
    def __init__(self):
        """初始化天氣回應處理器"""
        self.logger = get_logger(f"{__name__}.WeatherResponseHandler")
        self.logger.info("初始化天氣回應處理器")
    
    def generate_response(self, state: MessagesState) -> Dict[str, List[AIMessage]]:
        """
        生成天氣相關的固定回應
        
        Args:
            state: 當前消息狀態 (此處未使用)
            
        Returns:
            包含天氣資訊的回應
        """
        last_message = state["messages"][-1].content if state["messages"] else ""
        self.logger.debug(f"處理天氣查詢: {last_message}")
        
        weather_response = "今天晴天，氣溫25度。"
        self.logger.info(f"生成天氣回應: {weather_response}")
        
        return {"messages": [AIMessage(content=weather_response)]} 