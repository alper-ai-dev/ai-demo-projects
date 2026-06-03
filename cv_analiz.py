import streamlit as st
import requests
import os

API_KEY = os.environ.get("OPENROUTER_API_KEY")

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