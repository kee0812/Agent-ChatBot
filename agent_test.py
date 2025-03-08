"""
聊天機器人應用程式 - 使用 LangGraph 實現的簡單路由機制
可以處理一般問題和天氣相關問題的智能聊天機器人

作者：[您的名字]
日期：[日期]
"""

# 匯入必要模組和類型
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from typing import Dict, List, Union, Any
from abc import ABC, abstractmethod

# 載入環境變數
load_dotenv()


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


class WeatherResponseHandler(ResponseHandler):
    """處理天氣相關查詢的回應生成器"""
    
    def generate_response(self, state: MessagesState) -> Dict[str, List[AIMessage]]:
        """
        生成天氣相關的固定回應
        
        Args:
            state: 當前消息狀態 (此處未使用)
            
        Returns:
            包含天氣資訊的回應
        """
        return {"messages": [AIMessage(content="今天晴天，氣溫25度。")]}


class ModelResponseHandler(ResponseHandler):
    """使用LLM模型回應一般查詢的處理器"""
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        初始化模型回應處理器
        
        Args:
            model_name: 要使用的LLM模型名稱
        """
        self.llm = ChatOpenAI(model=model_name)
    
    def generate_response(self, state: MessagesState) -> Dict[str, List[AIMessage]]:
        """
        使用LLM模型生成回應
        
        Args:
            state: 包含消息歷史的狀態
            
        Returns:
            模型生成的回應
        """
        return {"messages": [self.llm.invoke(state["messages"])]}


class QueryRouter:
    """查詢路由器 - 決定如何處理用戶輸入"""
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        初始化查詢路由器
        
        Args:
            model_name: 用於分類的LLM模型名稱
        """
        self.llm = ChatOpenAI(model=model_name)
    
    def route(self, state: MessagesState) -> str:
        """
        路由用戶查詢到適當的處理器
        
        Args:
            state: 包含消息歷史的狀態
            
        Returns:
            路由目標的字符串標識符 ("weather" 或 "model")
        """
        # 取得用戶最後一條消息的內容
        last_content = state["messages"][-1].content if state["messages"] else ""
        
        # 定義提示詞，要求模型判斷問題是否與天氣相關
        prompt = (
            f"請判斷以下問題是否與天氣相關。如果是請僅回覆 'weather'，否則回覆 'model'。\n"
            f"問題：{last_content}"
        )
        
        # 調用 llm 進行分類
        classification = self.llm.invoke([HumanMessage(content=prompt)])
        classification = classification.content.strip().lower()
        
        # 根據分類結果返回相應的路由
        if "weather" in classification:
            return "weather"
        else:
            return "model"


class ChatbotGraphBuilder:
    """聊天機器人圖形構建器 - 創建和配置狀態圖"""
    
    def __init__(self):
        """初始化圖形構建器"""
        self.graph_builder = StateGraph(MessagesState)
        self.graph = None
    
    def build_graph(self, router: QueryRouter, handlers: Dict[str, ResponseHandler]) -> None:
        """
        構建聊天機器人狀態圖
        
        Args:
            router: 用於路由查詢的路由器
            handlers: 處理不同類型查詢的處理器字典
        """
        # 添加條件邊，根據路由函數的返回值分流
        self.graph_builder.add_conditional_edges(
            START, 
            router.route, 
            {key: key for key in handlers.keys()}
        )
        
        # 添加節點和邊
        for node_name, handler in handlers.items():
            self.graph_builder.add_node(node_name, handler.generate_response)
            self.graph_builder.add_edge(node_name, END)
        
        # 編譯圖
        self.graph = self.graph_builder.compile()
    
    def get_graph(self):
        """
        獲取已編譯的圖
        
        Returns:
            編譯好的狀態圖
        """
        if not self.graph:
            raise ValueError("圖尚未構建，請先調用 build_graph 方法")
        return self.graph


class ChatbotApp:
    """聊天機器人應用程式 - 整合所有組件並處理用戶交互"""
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        初始化聊天機器人應用
        
        Args:
            model_name: 用於路由和回應的LLM模型名稱
        """
        # 初始化路由器
        self.router = QueryRouter(model_name)
        
        # 初始化回應處理器
        self.handlers = {
            "weather": WeatherResponseHandler(),
            "model": ModelResponseHandler(model_name)
        }
        
        # 構建圖
        self.graph_builder = ChatbotGraphBuilder()
        self.graph_builder.build_graph(self.router, self.handlers)
        self.graph = self.graph_builder.get_graph()
    
    def process_query(self, query: str) -> AIMessage:
        """
        處理單個用戶查詢
        
        Args:
            query: 用戶輸入的查詢文本
            
        Returns:
            AI的回應消息
        """
        # 構造輸入狀態
        input_state = {"messages": [HumanMessage(content=query)]}
        
        # 執行圖
        response = self.graph.invoke(input_state)
        
        # 返回最後一條AI消息
        return response["messages"][-1]
    
    def run_interactive(self) -> None:
        """啟動交互式聊天會話"""
        print("=== 聊天機器人已啟動 ===")
        print("可以詢問天氣或任何其他問題")
        print("輸入 'exit' 結束對話")
        
        while True:
            user_input = input("\n請輸入查詢內容: ")
            if user_input.strip().lower() == "exit":
                print("程式結束。")
                break
                
            # 處理查詢並輸出回應
            response = self.process_query(user_input)
            response.pretty_print()


# 主程式入口點
if __name__ == "__main__":
    # 創建並啟動聊天機器人
    chatbot = ChatbotApp()
    chatbot.run_interactive()
