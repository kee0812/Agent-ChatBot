"""
翻譯回應處理器
用於處理需要翻譯的查詢請求
"""

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import MessagesState
from langchain_openai import ChatOpenAI
from typing import Dict, List
from handlers.base_handler import ResponseHandler
from logger import get_logger

class TranslationResponseHandler(ResponseHandler):
    """處理翻譯相關查詢的回應生成器"""
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        初始化翻譯回應處理器
        
        Args:
            model_name: 要使用的LLM模型名稱
        """
        self.llm = ChatOpenAI(model=model_name)
        self.logger = get_logger(f"{__name__}.TranslationResponseHandler")
        self.logger.info(f"初始化翻譯處理器，使用模型: {model_name}")
    
    def generate_response(self, state: MessagesState) -> Dict[str, List[AIMessage]]:
        """
        使用LLM模型生成翻譯回應
        
        Args:
            state: 包含消息歷史的狀態
            
        Returns:
            包含翻譯結果的回應
        """
        last_content = state["messages"][-1].content if state["messages"] else ""
        self.logger.debug(f"處理翻譯請求: {last_content}")
        
        # 提取要翻譯的文本，去除可能的指令部分
        text_to_translate = last_content
        if "翻譯" in last_content and ":" in last_content:
            text_to_translate = last_content.split(":", 1)[1].strip()
        
        # 翻譯提示詞
        prompt = f"請將以下文本翻譯成英文（只需要返回翻譯結果，不需要解釋）：\n\n{text_to_translate}"
        
        # 調用翻譯模型
        self.logger.debug("調用翻譯模型...")
        result = self.llm.invoke([HumanMessage(content=prompt)])
        
        translation_result = result.content
        self.logger.info(f"生成翻譯結果，長度: {len(translation_result)} 字符")
        self.logger.debug(f"翻譯結果: {translation_result}")
        
        return {"messages": [AIMessage(content=translation_result)]} 