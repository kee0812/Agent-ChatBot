# 智能聊天機器人 API

基於 LangGraph 和 LangChain 實現的智能聊天機器人 API 服務，可自動判斷問題類型並提供相應的回答。適合作為 Agent 集成到其他應用中。

## 功能特點

- **自動問題分類**：自動識別天氣、翻譯或一般問題
- **多模型支持**：支持多種 OpenAI 模型（gpt-4o-mini, gpt-4, gpt-3.5-turbo 等）
- **對話歷史記憶**：模型會考慮之前的對話內容，提供更連貫的回應
- **參數可調整**：可以調整溫度等參數
- **RESTful API**：提供完整的 RESTful API 接口
- **完整日誌系統**：詳細記錄所有操作
- **Docker 支持**：支持 Docker 部署和容器化
- **會話管理**：通過 session_id 管理對話上下文
- **健康檢查**：提供 API 健康檢查端點

## 安裝與設置

### 必要條件

- Python 3.9 或更高版本
- Docker（如需容器化部署）
- OpenAI API 密鑰

### 從源碼安裝

1. 克隆倉庫

```bash
git clone https://github.com/yourusername/chatbot-api.git
cd chatbot-api
```

2. 安裝依賴

```bash
pip install -r requirements.txt
```

3. 設置環境變數
   創建`.env`文件並添加必要的 API 密鑰：

```
OPENAI_API_KEY=your_api_key_here
```

### 使用 Docker 運行

1. 使用 docker-compose 運行服務

```bash
docker-compose up -d
```

這將在後台啟動服務，並在 8000 端口上運行 API。

## 使用方法

### API 端點

#### POST /chat

處理聊天請求，支持對話歷史記憶。

**請求格式**：

```json
{
  "message": "你的問題",
  "model": "gpt-4o-mini",
  "temperature": 0.7,
  "metadata": {
    "user_id": "user123",
    "session_id": "session456"
  }
}
```

**響應格式**：

```json
{
  "message": "機器人的回答",
  "type": "model",
  "model_used": "gpt-4o-mini",
  "processing_time": 0.85,
  "timestamp": "2023-03-08T14:30:15.123456",
  "conversation_id": "session456",
  "metadata": {
    "user_id": "user123",
    "session_id": "session456",
    "temperature": 0.7,
    "message_count": 5
  }
}
```

#### GET /conversations/{session_id}

獲取特定會話的對話歷史。

#### GET /models

獲取支持的模型列表。

#### GET /health

健康檢查端點。

### 使用 Postman 測試

請參閱[Postman 測試指南](#使用-postman-測試對話歷史)部分以了解如何使用 Postman 測試 API，特別是對話歷史功能。

## 項目結構

```
project/
├── handlers/              # 回應處理器
│   ├── __init__.py
│   ├── base_handler.py    # ResponseHandler 抽象基類
│   ├── weather_handler.py # 天氣相關回應處理器
│   ├── model_handler.py   # 一般問題回應處理器
│   └── translation_handler.py # 翻譯處理器
├── router/                # 路由組件
│   ├── __init__.py
│   └── query_router.py    # 查詢路由器
├── graph/                 # 圖形組件
│   ├── __init__.py
│   └── graph_builder.py   # 聊天機器人圖形構建器
├── logs/                  # 日誌文件目錄 (運行時自動創建)
├── logger.py              # 日誌模組
├── app.py                 # 聊天機器人應用類
├── api.py                 # API服務
├── main.py                # 命令行應用入口點
├── requirements.txt       # 項目依賴
├── Dockerfile             # Docker配置
├── docker-compose.yml     # Docker Compose配置
└── README.md              # 項目說明
```

## 擴展指南

要添加新的回應類型，請遵循以下步驟：

1. 在`handlers/`目錄中創建新的處理器類，繼承`ResponseHandler`
2. 在`app.py`中的`ChatbotApp.__init__`方法中注冊新的處理器
3. 修改`router/query_router.py`中的路由邏輯
4. 更新 API 中的回應類型枚舉

## 使用 Postman 測試對話歷史

要測試聊天機器人是否能夠記住對話歷史，請按照以下步驟使用 Postman：

1. **第一次對話請求**：

   - 方法：POST
   - URL：`http://localhost:8000/chat`
   - Headers：`Content-Type: application/json`
   - Body:

   ```json
   {
     "message": "我叫小明",
     "metadata": {
       "user_id": "test_user",
       "session_id": "test_session"
     }
   }
   ```

2. **第二次對話請求**（使用相同的 session_id）：
   - 方法：POST
   - URL：`http://localhost:8000/chat`
   - Headers：`Content-Type: application/json`
   - Body:
   ```json
   {
     "message": "我剛才說我叫什麼名字？",
     "metadata": {
       "user_id": "test_user",
       "session_id": "test_session"
     }
   }
   ```

這個測試展示了模型如何使用對話歷史來回答依賴於之前對話內容的問題。

## 作為 Agent 集成

要將此 API 作為 Agent 集成到其他應用中：

1. 使用 HTTP 客戶端連接到 API 服務
2. 在 metadata 中提供一致的 user_id 和 session_id 以維持對話上下文
3. 根據回應類型(type)處理不同的回答邏輯
4. 使用/conversations 端點獲取歷史對話以進行分析

## 許可證

[MIT License](LICENSE)

## 致謝

- 本項目使用了[LangChain](https://github.com/langchain-ai/langchain)和[LangGraph](https://github.com/langchain-ai/langgraph)
- 感謝 OpenAI 提供的強大語言模型 API
