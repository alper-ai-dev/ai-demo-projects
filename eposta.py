import streamlit as st
import requests
import os

API_KEY = os.environ.get("OPENROUTER_API_KEY")

st.title("📧 AI Email Writer")
st.write("Enter a topic and let AI write a professional email!")

subject = st.text_input("📝 Email subject:")
recipient = st.text_input("👤 Recipient (e.g. customer, manager, supplier):")
tone = st.selectbox("🎯 Tone:", ["Professional", "Friendly", "Formal", "Apologetic", "Sales-focused"])
length = st.selectbox("📏 Length:", ["Short", "Medium", "Long"])

if st.button("✉️ Write Email"):
    if subject:
        with st.spinner("AI is writing..."):
            prompt = f"You are a professional business writing expert. Write an email to {recipient} in a {tone} tone and {length} length about: {subject}. Include subject line, greeting, body and closing."
            
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": "Bearer " + API_KEY},
                json={
                    "model": "openai/gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            result = response.json()
            st.markdown(result["choices"][0]["message"]["content"])
    else:
        st.warning("Please enter the email subject!")