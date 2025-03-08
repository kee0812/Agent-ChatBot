"""
查詢路由器
負責判斷用戶查詢屬於哪種類型，並將其路由到相應的處理器
"""

from langchain_core.messages import HumanMessage
from langgraph.graph import MessagesState
from langchain_openai import ChatOpenAI
from logger import get_logger

class QueryRouter:
    """查詢路由器 - 決定如何處理用戶輸入"""
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        初始化查詢路由器
        
        Args:
            model_name: 用於分類的LLM模型名稱
        """
        self.llm = ChatOpenAI(model=model_name)
        self.logger = get_logger(f"{__name__}.QueryRouter")
        self.logger.info(f"初始化查詢路由器，使用模型: {model_name}")
    
    def route(self, state: MessagesState) -> str:
        """
        路由用戶查詢到適當的處理器
        
        Args:
            state: 包含消息歷史的狀態
            
        Returns:
            路由目標的字符串標識符 ("weather", "translation" 或 "model")
        """
        # 取得用戶最後一條消息的內容
        last_content = state["messages"][-1].content if state["messages"] else ""
        self.logger.debug(f"用戶查詢: {last_content}")
        
        # 簡單的規則判斷 - 檢查是否包含翻譯關鍵詞
        if "翻譯" in last_content or "translate" in last_content.lower():
            self.logger.info("檢測到翻譯請求，路由至翻譯處理器")
            return "translation"
            
        # 如果不是翻譯請求，則使用LLM進行天氣或一般查詢分類
        # 定義提示詞，要求模型判斷問題是否與天氣相關
        prompt = (
            f"請判斷以下問題類型，回覆對應的標籤：\n"
            f"- 如果是天氣相關問題，回覆 'weather'\n"
            f"- 如果是翻譯相關問題，回覆 'translation'\n"
            f"- 如果是其他一般問題，回覆 'model'\n\n"
            f"問題：{last_content}"
        )
        
        # 調用 llm 進行分類
        self.logger.debug("正在進行查詢分類...")
        classification = self.llm.invoke([HumanMessage(content=prompt)])
        classification = classification.content.strip().lower()
        
        # 根據分類結果返回相應的路由
        if "weather" in classification:
            route_target = "weather"
        elif "translation" in classification:
            route_target = "translation"
        else:
            route_target = "model"
            
        self.logger.info(f"查詢已路由至: {route_target}")
        return route_target 