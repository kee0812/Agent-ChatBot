"""
日誌模組
為整個應用提供統一的日誌功能
"""

import logging
import os
from datetime import datetime
from typing import Optional

# 日誌級別映射
LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}

# 確保日誌目錄存在
def ensure_log_dir(log_dir: str = "logs") -> str:
    """
    確保日誌目錄存在
    
    Args:
        log_dir: 日誌目錄路徑
        
    Returns:
        日誌目錄的完整路徑
    """
    # 使用絕對路徑，確保在任何工作目錄下都能正確創建
    log_dir_path = os.path.abspath(log_dir)
    if not os.path.exists(log_dir_path):
        try:
            os.makedirs(log_dir_path)
            print(f"創建日誌目錄: {log_dir_path}")
        except Exception as e:
            print(f"創建日誌目錄失敗: {str(e)}")
    return log_dir_path

# 獲取日誌處理器
def get_handlers(log_file: Optional[str] = None, log_level: str = "info") -> list:
    """
    獲取日誌處理器列表
    
    Args:
        log_file: 日誌文件名，如果為None則僅輸出到控制台
        log_level: 日誌級別
        
    Returns:
        日誌處理器列表
    """
    handlers = []
    
    # 創建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台處理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(LOG_LEVELS.get(log_level, logging.INFO))
    handlers.append(console_handler)
    
    # 文件處理器 (如果指定了日誌文件)
    if log_file:
        try:
            # 獲取日誌目錄的絕對路徑
            log_dir_path = ensure_log_dir()
            log_file_path = os.path.join(log_dir_path, log_file)
            
            # 打印日誌文件路徑，便於調試
            print(f"日誌將保存到: {log_file_path}")
            
            # 創建文件處理器
            file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
            file_handler.setFormatter(formatter)
            file_handler.setLevel(LOG_LEVELS.get(log_level, logging.INFO))
            handlers.append(file_handler)
            
            # 確認文件處理器是否創建成功
            if os.path.exists(log_file_path):
                print(f"日誌文件已創建: {log_file_path}")
            else:
                print(f"警告: 日誌文件未創建: {log_file_path}")
                
        except Exception as e:
            print(f"創建日誌文件處理器時出錯: {str(e)}")
    
    return handlers

# 獲取配置好的日誌器
def get_logger(name: str, log_file: Optional[str] = None, log_level: str = "info") -> logging.Logger:
    """
    獲取已配置的日誌器
    
    Args:
        name: 日誌器名稱
        log_file: 日誌文件名，如果為None則僅輸出到控制台
        log_level: 日誌級別
        
    Returns:
        配置好的日誌器
    """
    # 如果未指定日誌文件，但需要寫入文件，則使用默認文件名
    if log_file is None and os.getenv("LOG_TO_FILE", "true").lower() == "true":
        log_file = f"chatbot_{datetime.now().strftime('%Y%m%d')}.log"
    
    logger = logging.getLogger(name)
    
    # 清除現有的處理器，以避免重複
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # 設置日誌級別
    logger.setLevel(LOG_LEVELS.get(log_level, logging.INFO))
    
    # 添加處理器
    for handler in get_handlers(log_file, log_level):
        logger.addHandler(handler)
    
    # 測試日誌器是否正常工作
    logger.info(f"日誌器 {name} 初始化完成，級別: {log_level}, 文件: {log_file if log_file else '僅控制台'}")
    
    return logger

# 默認日誌器
default_logger = get_logger(
    "chatbot", 
    f"chatbot_{datetime.now().strftime('%Y%m%d')}.log", 
    "info"
) 