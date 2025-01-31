from flask import Flask, request, jsonify
import requests
import feedparser
import json
import re
from config import *
import os

# Логирование переменных окружения
print(f"OPENROUTER_API_KEY: {os.getenv('OPENROUTER_API_KEY')}")
print(f"GOOGLE_API_KEY: {os.getenv('GOOGLE_API_KEY')}")
print(f"GOOGLE_CX: {os.getenv('GOOGLE_CX')}")



app = Flask(__name__)

def get_openai_answer(query):
    """Запрос к OpenChat 3.5 API через OpenRouter"""
    print(f"Query sent to OpenChat 3.5: {query}")  # для логирования
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "openchat/openchat-7b:free",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": f"{query}\nОтветь только номером правильного варианта (1-10). Если вопрос не требует выбора, напиши 'null'."}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"OpenChat 3.5 Response Status Code: {response.status_code}")  # для логирования
        response_data = response.json()
        print(f"OpenChat 3.5 Response: {response_data}")  # для логирования
        
        if 'choices' in response_data and len(response_data['choices']) > 0:
            content = response_data['choices'][0]['message']['content']
            if content:
                print(f"Answer from OpenChat 3.5: {content}")  # для логирования
                return content.strip()
            else:
                print("No valid answer from OpenChat 3.5")  # для логирования
                return None
        else:
            print("No valid choices from OpenChat 3.5")  # для логирования
            return None
    except Exception as e:
        print(f"OpenChat 3.5 Error: {e}")
        return None

def google_search(query):
    """Поиск ссылок через Google API"""
    print(f"Query sent to Google Search: {query}")  # для логирования
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX,
        "q": f"ИТМО {query}",
        "num": 3
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"Google Search Response Status Code: {response.status_code}")  # для логирования
        response.raise_for_status()
        items = response.json().get("items", [])
        print(f"Google Search Items: {items}")  # для логирования
        return [item["link"] for item in items[:3]]
    except Exception as e:
        print(f"Google Search Error: {e}")
        return []

def get_itmo_news():
    """Получение последних новостей ИТМО"""
    print("Fetching ITMO news")  # для логирования
    try:
        feed = feedparser.parse(ITMO_NEWS_RSS)
        print(f"ITMO News Feed: {feed}")  # для логирования
        return [entry.link for entry in feed.entries[:3]]
    except Exception as e:
        print(f"News Error: {e}")
        return []

def parse_answer(answer_text):
    """Извлечение номера ответа из текста"""
    print(f"Parsing answer: {answer_text}")  # для логов
    match = re.search(r'(?i)\b(null|10|\d)\b', answer_text)
    if match:
        value = int(match.group(0))
        if 1 <= value <= 10:
            print(f"Parsed answer: {value}")  # для логов
            return value
    print("No valid answer found")  # для логов
    return None

@app.route('/')
def index():
    return "Welcome to the ITMO bot API! Please send a POST request to /api/request."

@app.route('/api/request', methods=['POST'])
def handle_request():
    print("Handling request")  # для логирования
    # Валидация входных данных
    data = request.get_json()
    if not data or "query" not in data or "id" not in data:
        print("Invalid request data")  # для логирования
        return jsonify({"error": "Invalid request"}), 400
    
    query = data["query"]
    req_id = data["id"]
    print(f"Received query: {query}, id: {req_id}")  # для логирования
    
    # Получение ответа от OpenChat 3.5
    llm_answer = get_openai_answer(query)
    print(f"LLM answer: {llm_answer}")  # для логов
    answer_number = parse_answer(llm_answer) if llm_answer else None
    
    # Определение типа вопроса
    is_multiple_choice = re.search(r'\n1\.', query) is not None
    print(f"Is multiple choice: {is_multiple_choice}")  # для логов
    
    # Поиск ссылок и новостей
    sources = []
    if is_multiple_choice:
        sources.extend(google_search(query))
    else:
        sources.extend(get_itmo_news())
    print(f"Sources: {sources}")  # для логирования
    
    # Формирование ответа
    reasoning_message = "Не удалось получить ответ" if not llm_answer else f"Ответ сгенерирован моделью OpenChat 3.5. {llm_answer}"
    response = {
        "id": req_id,
        "answer": answer_number if is_multiple_choice else None,
        "reasoning": reasoning_message,
        "sources": sources[:3]  # Не более 3 ссылок
    }
    print(f"Final response: {response}")  # для логирования
    
    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)