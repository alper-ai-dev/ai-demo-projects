import streamlit as st
import requests
import os

API_KEY = os.environ.get("OPENROUTER_API_KEY")

st.title("🤖 AI Customer Service Chatbot")

company_info = st.text_area("Enter company information:", 
    value="We are Pizza House restaurant. Our menu includes Margherita, Pepperoni and Vegetarian pizza. Prices range from $10-20. Delivery takes 30-45 minutes. Working hours: 10:00-23:00.",
    height=150)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    if message["role"] == "user":
        st.chat_message("user").write(message["content"])
    else:
        st.chat_message("assistant").write(message["content"])

question = st.chat_input("Type your question...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    st.chat_message("user").write(question)
    
    with st.spinner("Responding..."):
        prompt = f"You are a customer service assistant. Company info: {company_info}. Customer question: {question}. Give a short and polite answer."
        
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": "Bearer " + API_KEY},
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        answer = response.json()["choices"][0]["message"]["content"]
    
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)