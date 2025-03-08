"""
回應處理器抽象基類
定義了所有回應處理器必須實現的介面
"""

from abc import ABC, abstractmethod
from langgraph.graph import MessagesState
from langchain_core.messages import AIMessage
from typing import Dict, List

class ResponseHandler(ABC):
    """
    回應處理器抽象基類
    所有特定類型的回應處理器都應繼承此類
    """
    
    @abstractmethod
    def generate_response(self, state: MessagesState) -> Dict[str, List[AIMessage]]:
        """
        根據當前狀態生成回應
        
        Args:
            state: 包含消息歷史的狀態
            
        Returns:
            包含新AI消息的字典
        """
        pass 