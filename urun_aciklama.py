import streamlit as st
import requests
import os

API_KEY = os.environ.get("OPENROUTER_API_KEY")

st.title("🛍️ AI Product Description Writer")
st.write("Enter product details and let AI write a sales-boosting description!")

product_name = st.text_input("📦 Product name:")
category = st.selectbox("🏷️ Category:", ["Electronics", "Clothing", "Home & Living", "Cosmetics", "Sports", "Food", "Other"])
features = st.text_area("✨ Product features:", placeholder="Color, size, material, specifications...")
price = st.text_input("💰 Price ($):")
platform = st.selectbox("🛒 Platform:", ["Amazon", "eBay", "Shopify", "Own Website", "Other"])

if st.button("✍️ Write Description"):
    if product_name:
        with st.spinner("AI is writing..."):
            prompt = f"""You are an e-commerce expert. Write a sales-boosting product description for {platform} in the {category} category:

Product: {product_name}
Features: {features}
Price: {price}$

Include:
1. Attention-grabbing title
2. Short and compelling product description
3. Bullet point features
4. Closing sentence that encourages purchase

Write naturally and persuasively."""

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
        st.warning("Please enter the product name!")