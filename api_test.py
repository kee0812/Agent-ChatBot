import requests

# 發送聊天請求
response = requests.post(
    "http://localhost:8000/chat",
    json={
        "message": "請幫我翻譯這句話：今天天氣如何？",
        "model": "gpt-4",
        "temperature": 0.8,
        "metadata": {
            "user_id": "user123",
            "session_id": "session456"
        }
    }
)

# 解析回應
result = response.json()
print(f"回應: {result['message']}")
print(f"類型: {result['type']}")
print(f"對話ID: {result['conversation_id']}")

# 獲取對話歷史
history = requests.get(f"http://localhost:8000/conversations/{result['conversation_id']}")
print(f"對話歷史消息數: {history.json()['message_count']}") 