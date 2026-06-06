"""
Text Sentiment & Analysis Tool
Analyze any text for sentiment, emotions, keywords, and insights using AI.
"""

import streamlit as st
import openai
import json

st.set_page_config(
    page_title="Text Sentiment Analyzer",
    page_icon="🧠",
    layout="wide"
)

st.markdown("""
<style>
    .metric-card { background: white; border-radius: 12px; padding: 20px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center; }
    .positive { border-top: 4px solid #22c55e; }
    .negative { border-top: 4px solid #ef4444; }
    .neutral  { border-top: 4px solid #f59e0b; }
    .mixed    { border-top: 4px solid #8b5cf6; }
    .emotion-tag { display: inline-block; padding: 4px 12px; border-radius: 20px;
                   margin: 4px; font-size: 0.85em; font-weight: 500; }
    .keyword-tag { display: inline-block; padding: 4px 10px; border-radius: 6px;
                   margin: 3px; font-size: 0.85em; background: #f0f4ff; color: #1e40af; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## ⚙️ Settings")
    api_key = st.text_input("OpenRouter API Key", type="password")
    st.markdown("---")
    st.markdown("## 🌍 Language")
    lang = st.selectbox("Output Language", ["English", "Turkish"])
    st.markdown("---")
    st.markdown("## 📊 Analysis Options")
    do_sentiment  = st.checkbox("Sentiment Analysis", value=True)
    do_emotions   = st.checkbox("Emotion Detection", value=True)
    do_keywords   = st.checkbox("Keyword Extraction", value=True)
    do_summary    = st.checkbox("Text Summary", value=True)
    do_intent     = st.checkbox("Intent Detection", value=True)

st.title("🧠 Text Sentiment & Analysis Tool")
st.caption("Analyze any text for sentiment, emotions, keywords, and deeper insights")

col1, col2, col3 = st.columns(3)
with col1: st.markdown("**😊 Sentiment** — Positive, Negative, Neutral")
with col2: st.markdown("**❤️ Emotions** — Joy, Anger, Fear, Surprise...")
with col3: st.markdown("**🔑 Keywords** — Most important terms")

st.markdown("---")

if not api_key:
    st.warning("⚠️ Please enter your OpenRouter API Key in the sidebar.")
else:
    # Sample texts
    st.markdown("### 💬 Try a sample or enter your own text:")
    samples = {
        "Customer Review (Positive)": "I absolutely love this product! It exceeded all my expectations. The quality is outstanding and delivery was super fast. Will definitely order again!",
        "Customer Review (Negative)": "Terrible experience. The product arrived broken and customer service was unhelpful. Complete waste of money. Never buying from this company again.",
        "News Article": "The stock market showed mixed signals today as tech companies reported strong earnings while energy sector faced headwinds due to falling oil prices.",
        "Social Media Post": "Just got promoted at work! Can't believe it finally happened after years of hard work. My team is amazing and I'm so grateful for this opportunity! 🎉"
    }
    
    selected = st.selectbox("Load sample text", ["— Enter your own —"] + list(samples.keys()))
    
    default_text = samples.get(selected, "") if selected != "— Enter your own —" else ""
    
    text_input = st.text_area(
        "Enter text to analyze:",
        value=default_text,
        height=150,
        placeholder="Paste any text here — customer reviews, social media posts, news articles, emails..."
    )
    
    analyze_btn = st.button("🔍 Analyze Text", type="primary", use_container_width=True)
    
    if analyze_btn and text_input.strip():
        with st.spinner("Analyzing text..."):
            client = openai.OpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1"
            )
            
            lang_note = "Respond in Turkish." if lang == "Turkish" else "Respond in English."
            
            prompt = f"""Analyze this text and return ONLY a JSON object. {lang_note}

Text: "{text_input}"

Return this exact JSON structure:
{{
  "sentiment": "positive" or "negative" or "neutral" or "mixed",
  "sentiment_score": number from -100 to 100,
  "sentiment_explanation": "one sentence explanation",
  "emotions": [
    {{"name": "emotion name", "score": 0-100, "color": "hex color"}}
  ],
  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
  "summary": "2-3 sentence summary of the text",
  "intent": "what is the author trying to communicate or achieve",
  "tone": "formal/informal/aggressive/friendly/etc",
  "language_quality": "simple/moderate/advanced",
  "word_count": {len(text_input.split())}
}}

For emotions use these with colors:
Joy #22c55e, Anger #ef4444, Fear #8b5cf6, Sadness #3b82f6, 
Surprise #f59e0b, Disgust #f97316, Trust #06b6d4, Anticipation #ec4899"""

            try:
                resp = client.chat.completions.create(
                    model="openai/gpt-4o-mini",
                    max_tokens=800,
                    messages=[
                        {"role": "system", "content": "You are a text analysis expert. Return only valid JSON."},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                raw = resp.choices[0].message.content.strip()
                raw = raw.replace("```json", "").replace("```", "").strip()
                result = json.loads(raw)
                
            except Exception as e:
                st.error(f"Analysis failed: {e}")
                st.stop()
        
        # ── RESULTS ────────────────────────────────────────────
        st.markdown("## 📊 Analysis Results")
        
        # Sentiment score
        sentiment = result.get("sentiment", "neutral")
        score = result.get("sentiment_score", 0)
        color_class = sentiment if sentiment in ["positive", "negative", "neutral", "mixed"] else "neutral"
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="metric-card {color_class}"><h2>{"😊" if sentiment=="positive" else "😞" if sentiment=="negative" else "😐" if sentiment=="neutral" else "🤔"}</h2><h3>{sentiment.upper()}</h3><p>Score: {score:+d}</p></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card neutral"><h2>🎯</h2><h3>{result.get("tone","").upper()}</h3><p>Tone</p></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card neutral"><h2>📚</h2><h3>{result.get("language_quality","").upper()}</h3><p>Complexity</p></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-card neutral"><h2>📝</h2><h3>{result.get("word_count",0)}</h3><p>Words</p></div>', unsafe_allow_html=True)
        
        st.markdown(f"**Sentiment:** {result.get('sentiment_explanation','')}")
        
        st.markdown("---")
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            # Emotions
            if do_emotions and result.get("emotions"):
                st.markdown("### ❤️ Emotions Detected")
                for em in result["emotions"]:
                    name  = em.get("name", "")
                    score = em.get("score", 0)
                    color = em.get("color", "#888")
                    st.markdown(
                        f'<span class="emotion-tag" style="background:{color}22; color:{color}; border: 1px solid {color}">'
                        f'{name} {score}%</span>',
                        unsafe_allow_html=True
                    )
                    st.progress(score / 100)
            
            # Keywords
            if do_keywords and result.get("keywords"):
                st.markdown("### 🔑 Keywords")
                kw_html = " ".join([f'<span class="keyword-tag">{kw}</span>' for kw in result["keywords"]])
                st.markdown(kw_html, unsafe_allow_html=True)
        
        with col_right:
            # Summary
            if do_summary and result.get("summary"):
                st.markdown("### 📋 Summary")
                st.info(result["summary"])
            
            # Intent
            if do_intent and result.get("intent"):
                st.markdown("### 🎯 Intent")
                st.success(result["intent"])
        
        # Raw JSON
        with st.expander("🔧 Raw JSON Output"):
            st.json(result)
