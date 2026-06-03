import requests
import json

API_KEY = "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"

print("=== AI Destekli CV Analiz Aracı ===")
print("CV'nizi aşağıya yapıştırın, bitince Enter'a basın:")

cv_metni = input()

prompt = f"""
Sen bir kariyer uzmanısın. Aşağıdaki CV'yi analiz et ve şunları söyle:

1. 💪 GÜÇLÜ YÖNLER (3-5 madde)
2. ⚠️ GELİŞTİRİLMESİ GEREKEN YÖNLER (3-5 madde)
3. 🎯 UYGUN POZİSYONLAR (5 pozisyon öner)
4. 📈 TAVSİYELER (somut adımlar)

CV:
{cv_metni}
"""

response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "model": "openai/gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}]
    }
)

sonuc = response.json()
print("\n")
print(sonuc["choices"][0]["message"]["content"])