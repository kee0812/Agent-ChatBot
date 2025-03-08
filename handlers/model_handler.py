"""
模型回應處理器
用於處理需要LLM模型生成回應的一般查詢
"""

from langchain_core.messages import AIMessage
from langgraph.graph import MessagesState
from langchain_openai import ChatOpenAI
from typing import Dict, List
from handlers.base_handler import ResponseHandler
from logger import get_logger

class ModelResponseHandler(ResponseHandler):
    """使用LLM模型回應一般查詢的處理器"""
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        初始化模型回應處理器
        
        Args:
            model_name: 要使用的LLM模型名稱
        """
        self.llm = ChatOpenAI(model=model_name)
        self.logger = get_logger(f"{__name__}.ModelResponseHandler")
        self.logger.info(f"初始化模型回應處理器，使用模型: {model_name}")
    
    def generate_response(self, state: MessagesState) -> Dict[str, List[AIMessage]]:
        """
        使用LLM模型生成回應
        
        Args:
            state: 包含消息歷史的狀態
            
        Returns:
            模型生成的回應
        """
        last_message = state["messages"][-1].content if state["messages"] else ""
        self.logger.debug(f"處理一般查詢: {last_message}")
        
        self.logger.debug("調用LLM模型生成回應...")
        response = self.llm.invoke(state["messages"])
        
        response_content = response.content
        self.logger.info(f"模型生成回應，長度: {len(response_content)} 字符")
        self.logger.debug(f"模型回應內容: {response_content}")
        
        return {"messages": [response]} 