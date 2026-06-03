<<<<<<< HEAD
import streamlit as st
import requests

API_KEY = "YOUR_API_KEY"

st.title("🤖 AI Müşteri Hizmetleri Chatbotu")

sirket_bilgisi = st.text_area("Şirket bilgisi girin:", 
    value="Biz Pizza House restoranıyız. Menümüzde Margherita, Pepperoni ve Vejetaryen pizza var. Fiyatlar 150-250 TL arası. Teslimat 30-45 dakika sürer. Çalışma saatimiz 10:00-23:00.",
    height=150)

if "mesajlar" not in st.session_state:
    st.session_state.mesajlar = []

for mesaj in st.session_state.mesajlar:
    if mesaj["rol"] == "kullanici":
        st.chat_message("user").write(mesaj["icerik"])
    else:
        st.chat_message("assistant").write(mesaj["icerik"])

soru = st.chat_input("Sorunuzu yazın...")

if soru:
    st.session_state.mesajlar.append({"rol": "kullanici", "icerik": soru})
    st.chat_message("user").write(soru)
    
    with st.spinner("Yanıtlanıyor..."):
        prompt = f"Sen bir müşteri hizmetleri asistanısın. Şirket bilgisi: {sirket_bilgisi}. Müşteri sorusu: {soru}. Kısa ve nazik cevap ver."
        
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": "Bearer " + API_KEY},
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        cevap = response.json()["choices"][0]["message"]["content"]
    
    st.session_state.mesajlar.append({"rol": "asistan", "icerik": cevap})
=======
import streamlit as st
import requests

API_KEY = "YOUR_API_KEY"

st.title("🤖 AI Müşteri Hizmetleri Chatbotu")

sirket_bilgisi = st.text_area("Şirket bilgisi girin:", 
    value="Biz Pizza House restoranıyız. Menümüzde Margherita, Pepperoni ve Vejetaryen pizza var. Fiyatlar 150-250 TL arası. Teslimat 30-45 dakika sürer. Çalışma saatimiz 10:00-23:00.",
    height=150)

if "mesajlar" not in st.session_state:
    st.session_state.mesajlar = []

for mesaj in st.session_state.mesajlar:
    if mesaj["rol"] == "kullanici":
        st.chat_message("user").write(mesaj["icerik"])
    else:
        st.chat_message("assistant").write(mesaj["icerik"])

soru = st.chat_input("Sorunuzu yazın...")

if soru:
    st.session_state.mesajlar.append({"rol": "kullanici", "icerik": soru})
    st.chat_message("user").write(soru)
    
    with st.spinner("Yanıtlanıyor..."):
        prompt = f"Sen bir müşteri hizmetleri asistanısın. Şirket bilgisi: {sirket_bilgisi}. Müşteri sorusu: {soru}. Kısa ve nazik cevap ver."
        
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": "Bearer " + API_KEY},
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        cevap = response.json()["choices"][0]["message"]["content"]
    
    st.session_state.mesajlar.append({"rol": "asistan", "icerik": cevap})
>>>>>>> a9015c626a0b2211867df7ebbfd7a2d28c94a0fd
    st.chat_message("assistant").write(cevap)