"""
聊天機器人應用程式 - 使用 LangGraph 實現的簡單路由機制
可以處理一般問題和天氣相關問題的智能聊天機器人

主程式入口點
"""

import os
import argparse
import sys
from app import ChatbotApp
from dotenv import load_dotenv
from logger import get_logger, default_logger, ensure_log_dir
import requests

# 檢查日誌系統
def check_logging_system():
    """檢查日誌系統是否正確初始化"""
    print("檢查日誌系統...")
    log_dir = ensure_log_dir()
    print(f"日誌目錄: {log_dir}")
    print(f"目錄存在: {os.path.exists(log_dir)}")
    print(f"目錄可寫: {os.access(log_dir, os.W_OK)}")
    
    # 創建測試日誌文件
    test_file = os.path.join(log_dir, "test_log.txt")
    try:
        with open(test_file, 'w') as f:
            f.write("測試寫入")
        print(f"測試文件創建成功: {test_file}")
        os.remove(test_file)
        print("測試文件已刪除")
        return True
    except Exception as e:
        print(f"日誌系統檢查失敗: {str(e)}")
        return False

# 設置命令行參數
def setup_args():
    """設置並解析命令行參數"""
    parser = argparse.ArgumentParser(description="啟動智能聊天機器人")
    parser.add_argument(
        "--model", 
        type=str, 
        default="gpt-4o-mini", 
        help="要使用的OpenAI模型名稱"
    )
    parser.add_argument(
        "--log-level", 
        type=str, 
        choices=["debug", "info", "warning", "error", "critical"],
        default="info", 
        help="日誌級別"
    )
    parser.add_argument(
        "--log-to-file",
        action="store_true",
        default=True,
        help="是否將日誌寫入文件"
    )
    return parser.parse_args()

# 載入環境變數
def load_environment():
    """載入環境變數"""
    load_dotenv()
    # 確認API密鑰存在
    if not os.getenv("OPENAI_API_KEY"):
        default_logger.warning("未找到 OPENAI_API_KEY 環境變數，請確保已正確設置")

# 主程式入口點
if __name__ == "__main__":
    print("啟動聊天機器人應用...")
    
    # 檢查日誌系統
    if not check_logging_system():
        print("日誌系統初始化失敗，應用將繼續運行但可能無法記錄日誌")
    
    # 解析命令行參數
    args = setup_args()
    
    # 設置是否寫入日誌文件
    os.environ["LOG_TO_FILE"] = "true" if args.log_to_file else "false"
    
    # 配置日誌級別
    logger = get_logger("main", log_level=args.log_level)
    logger.info(f"啟動應用，日誌級別: {args.log_level}")
    
    # 載入環境變數
    load_environment()
    logger.info(f"將使用模型: {args.model}")
    
    # 創建並啟動聊天機器人
    try:
        logger.info("初始化聊天機器人...")
        chatbot = ChatbotApp(model_name=args.model)
        
        logger.info("啟動交互式會話...")
        chatbot.run_interactive()
    except Exception as e:
        logger.critical(f"應用啟動失敗: {str(e)}", exc_info=True)
        print(f"啟動失敗: {str(e)}")
    finally:
        logger.info("應用結束") 