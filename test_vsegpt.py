# test_vsegpt.py

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    print("Testing vsegpt.ru connection...")
    
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.vsegpt.ru/v1")
    )
    
    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini"),
            messages=[{"role": "user", "content": "Привет! Ты работаешь? Ответь 'Да, я работаю'"}],
            temperature=0.7
        )
        
        print("✅ Подключение успешно!")
        print(f"Ответ: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        print("\nПроверьте:")
        print("1. API ключ в файле .env")
        print("2. BASE_URL = https://api.vsegpt.ru/v1")
        print("3. Наличие средств на балансе vsegpt.ru")
        return False

if __name__ == "__main__":
    test_connection()