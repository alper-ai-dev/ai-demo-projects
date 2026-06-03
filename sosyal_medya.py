import streamlit as st
import requests
import os

API_KEY = os.environ.get("OPENROUTER_API_KEY")

st.title("📱 AI Social Media Content Generator")
st.write("Enter your topic and let AI create engaging social media posts!")

topic = st.text_input("📝 Topic:")
platform = st.selectbox("📱 Platform:", ["Instagram", "Twitter/X", "LinkedIn", "Facebook", "TikTok"])
tone = st.selectbox("🎯 Tone:", ["Professional", "Casual", "Funny", "Inspirational", "Promotional"])
language = st.selectbox("🌍 Language:", ["English", "Turkish"])

if st.button("✨ Generate Post"):
    if topic:
        with st.spinner("AI is creating your post..."):
            prompt = f"You are a social media expert. Create an engaging {platform} post about '{topic}' in a {tone} tone in {language}. Include relevant hashtags and emojis."
            
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
        st.warning("Please enter a topic!")