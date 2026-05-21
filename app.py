import streamlit as st
import requests

API_KEY = "YOUR_API_KEY"

st.title("🤖 AI Destekli CV Analiz Aracı")
st.write("CV'nizi aşağıya yapıştırın, AI analiz etsin!")

cv_metni = st.text_area("CV Metniniz:", height=300)

if st.button("🚀 Analiz Et"):
    if cv_metni:
        with st.spinner("AI analiz yapıyor..."):
            prompt = f"""
Sen bir kariyer uzmanısın. Aşağıdaki CV'yi analiz et:

1. 💪 GÜÇLÜ YÖNLER (3-5 madde)
2. ⚠️ GELİŞTİRİLMESİ GEREKEN YÖNLER (3-5 madde)
3. 🎯 UYGUN POZİSYONLAR (5 pozisyon)
4. 📈 TAVSİYELER

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
            st.markdown(sonuc["choices"][0]["message"]["content"])
    else:
        st.warning("Lütfen CV metninizi girin!")