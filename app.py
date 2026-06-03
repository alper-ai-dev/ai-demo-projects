<<<<<<< HEAD
import streamlit as st
import requests
import os

API_KEY = os.environ.get("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")

st.title("🤖 AI-Powered CV Analyzer")
st.write("Paste your CV below and let AI analyze it instantly!")

cv_text = st.text_area("Your CV:", height=300)

if st.button("🚀 Analyze"):
    if cv_text:
        with st.spinner("AI is analyzing your CV..."):
            prompt = f"""
You are a professional career consultant. Analyze the CV below and provide:

1. 💪 STRENGTHS (3-5 points)
2. ⚠️ AREAS FOR IMPROVEMENT (3-5 points)
3. 🎯 SUITABLE JOB POSITIONS (5 positions)
4. 📈 RECOMMENDATIONS

CV:
{cv_text}
"""
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={
                    "model": "openai/gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            result = response.json()
            st.markdown(result["choices"][0]["message"]["content"])
    else:
        st.warning("Please enter your CV text!")
=======
import streamlit as st
import requests
import os
API_KEY = os.environ.get("OPENROUTER_API_KEY")

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
>>>>>>> a9015c626a0b2211867df7ebbfd7a2d28c94a0fd
