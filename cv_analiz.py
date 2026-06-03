import requests

API_KEY = "OPENROUTER_KEY_BURAYA"

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
print("\n⏳ AI analiz yapıyor...\n")
print(sonuc["choices"][0]["message"]["content"])
