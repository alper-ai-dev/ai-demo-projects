import streamlit as st
import requests

API_KEY = "YOUR_API_KEY"

st.title("🛍️ AI Ürün Açıklama Yazıcı")
st.write("Ürün bilgilerini gir, AI satış artıran açıklama yazsın!")

urun_adi = st.text_input("📦 Ürün adı:")
kategori = st.selectbox("🏷️ Kategori:", ["Elektronik", "Giyim", "Ev & Yaşam", "Kozmetik", "Spor", "Gıda", "Diğer"])
ozellikler = st.text_area("✨ Ürün özellikleri:", placeholder="Renk, boyut, malzeme, özellikler...")
fiyat = st.text_input("💰 Fiyat (TL):")
platform = st.selectbox("🛒 Platform:", ["Trendyol", "Hepsiburada", "Amazon", "Kendi Web Sitesi"])

if st.button("✍️ Açıklama Yaz"):
    if urun_adi:
        with st.spinner("AI yazıyor..."):
            prompt = f"""Sen bir e-ticaret uzmanısın. {platform} için {kategori} kategorisinde şu ürünün satış artıran açıklamasını yaz:

Ürün: {urun_adi}
Özellikler: {ozellikler}
Fiyat: {fiyat} TL

Şunları yaz:
1. Dikkat çekici başlık
2. Kısa ve etkileyici ürün açıklaması
3. Madde madde özellikler
4. Müşteriyi satın almaya teşvik eden kapanış cümlesi

Türkçe yaz, doğal ve akıcı ol."""

            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": "Bearer " + API_KEY},
                json={
                    "model": "openai/gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            sonuc = response.json()
            st.markdown(sonuc["choices"][0]["message"]["content"])
    else:
        st.warning("Lütfen ürün adını girin!")