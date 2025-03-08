"""
聊天機器人應用程式
整合各個組件並提供用戶界面
"""

from langchain_core.messages import HumanMessage, AIMessage
from typing import Dict
from handlers.base_handler import ResponseHandler
from handlers.weather_handler import WeatherResponseHandler
from handlers.model_handler import ModelResponseHandler
from handlers.translation_handler import TranslationResponseHandler
from router.query_router import QueryRouter
from graph.graph_builder import ChatbotGraphBuilder
from logger import get_logger, default_logger

class ChatbotApp:
    """聊天機器人應用程式 - 整合所有組件並處理用戶交互"""
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        初始化聊天機器人應用
        
        Args:
            model_name: 用於路由和回應的LLM模型名稱
        """
        self.logger = get_logger(f"{__name__}.ChatbotApp")
        self.logger.info(f"初始化聊天機器人應用，使用模型: {model_name}")
        
        # 初始化路由器
        self.logger.debug("初始化查詢路由器...")
        self.router = QueryRouter(model_name)
        
        # 初始化回應處理器
        self.logger.debug("初始化回應處理器...")
        self.handlers = {
            "weather": WeatherResponseHandler(),
            "model": ModelResponseHandler(model_name),
            "translation": TranslationResponseHandler(model_name)
        }
        
        # 構建圖
        self.logger.debug("構建聊天流程圖...")
        self.graph_builder = ChatbotGraphBuilder()
        self.graph_builder.build_graph(self.router, self.handlers)
        self.graph = self.graph_builder.get_graph()
        self.logger.info("聊天機器人初始化完成")
    
    def process_query(self, query: str, model_name: str = None, temperature: float = 0.7, conversation_history: list = None) -> AIMessage:
        """
        處理單個用戶查詢
        
        Args:
            query: 用戶輸入的查詢文本
            model_name: 要使用的模型名稱
            temperature: 模型溫度參數
            conversation_history: 對話歷史記錄列表，格式為[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
            
        Returns:
            AI的回應消息
        """
        self.logger.info(f"處理用戶查詢: {query}, 模型: {model_name or '默認'}, 溫度: {temperature}")
        self.logger.debug(f"對話歷史長度: {len(conversation_history) if conversation_history else 0}")
        
        # 如果指定了模型，則更新處理器的模型
        if model_name:
            self.logger.debug(f"使用指定模型: {model_name}")
            for handler_name, handler in self.handlers.items():
                if hasattr(handler, 'llm') and hasattr(handler.llm, 'model_name'):
                    original_model = handler.llm.model_name
                    handler.llm.model_name = model_name
                    handler.llm.temperature = temperature
                    self.logger.debug(f"更新{handler_name}處理器模型: {original_model} -> {model_name}, 溫度: {temperature}")
        
        # 構造輸入狀態，包含對話歷史
        self.logger.debug("創建輸入狀態...")
        messages = []
        
        # 如果有對話歷史，則添加到消息中
        if conversation_history:
            for msg in conversation_history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))
        
        # 添加當前用戶消息
        messages.append(HumanMessage(content=query))
        input_state = {"messages": messages}
        
        # 執行圖
        self.logger.debug("開始執行查詢處理...")
        try:
            response = self.graph.invoke(input_state)
            self.logger.info("查詢處理完成")
            # 返回最後一條AI消息
            return response["messages"][-1]
        except Exception as e:
            self.logger.error(f"處理查詢時發生錯誤: {str(e)}", exc_info=True)
            # 返回錯誤消息
            return AIMessage(content=f"很抱歉，處理您的請求時出現了錯誤: {str(e)}")
    
    def run_interactive(self) -> None:
        """啟動交互式聊天會話"""
        self.logger.info("啟動交互式聊天會話")
        print("=== 聊天機器人已啟動 ===")
        print("可以詢問天氣或任何其他問題")
        print("輸入 'exit' 結束對話")
        
        session_query_count = 0
        
        while True:
            try:
                user_input = input("\n請輸入查詢內容: ")
                
                if user_input.strip().lower() == "exit":
                    self.logger.info("用戶請求結束對話")
                    print("程式結束。")
                    break
                    
                session_query_count += 1
                self.logger.info(f"收到第 {session_query_count} 個查詢")
                
                # 處理查詢並輸出回應
                response = self.process_query(user_input)
                response.pretty_print()
                
            except KeyboardInterrupt:
                self.logger.info("用戶通過鍵盤中斷結束對話")
                print("\n程式被中斷，結束對話。")
                break
            except Exception as e:
                self.logger.error(f"交互式會話中發生未處理的錯誤: {str(e)}", exc_info=True)
                print(f"發生錯誤: {str(e)}")
                
        self.logger.info(f"交互式會話結束，共處理了 {session_query_count} 個查詢") 