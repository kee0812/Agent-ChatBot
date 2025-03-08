"""
聊天機器人圖形構建器
負責創建和配置聊天機器人的狀態圖
"""

from langgraph.graph import StateGraph, MessagesState, START, END
from typing import Dict
from handlers.base_handler import ResponseHandler
from router.query_router import QueryRouter
from logger import get_logger

class ChatbotGraphBuilder:
    """聊天機器人圖形構建器 - 創建和配置狀態圖"""
    
    def __init__(self):
        """初始化圖形構建器"""
        self.graph_builder = StateGraph(MessagesState)
        self.graph = None
        self.logger = get_logger(f"{__name__}.ChatbotGraphBuilder")
        self.logger.info("初始化聊天機器人圖形構建器")
    
    def build_graph(self, router: QueryRouter, handlers: Dict[str, ResponseHandler]) -> None:
        """
        構建聊天機器人狀態圖
        
        Args:
            router: 用於路由查詢的路由器
            handlers: 處理不同類型查詢的處理器字典
        """
        self.logger.info(f"開始構建圖形，處理器類型: {list(handlers.keys())}")
        
        # 添加條件邊，根據路由函數的返回值分流
        self.logger.debug("添加條件邊...")
        self.graph_builder.add_conditional_edges(
            START, 
            router.route, 
            {key: key for key in handlers.keys()}
        )
        
        # 添加節點和邊
        self.logger.debug("添加處理節點和邊...")
        for node_name, handler in handlers.items():
            self.logger.debug(f"添加節點: {node_name}")
            self.graph_builder.add_node(node_name, handler.generate_response)
            self.graph_builder.add_edge(node_name, END)
        
        # 編譯圖
        self.logger.info("編譯圖形...")
        self.graph = self.graph_builder.compile()
        self.logger.info("圖形構建完成")
    
    def get_graph(self):
        """
        獲取已編譯的圖
        
        Returns:
            編譯好的狀態圖
        """
        if not self.graph:
            error_msg = "圖尚未構建，請先調用 build_graph 方法"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
            
        self.logger.debug("獲取編譯好的圖形")
        return self.graph 