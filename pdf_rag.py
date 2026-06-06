import streamlit as st
import requests
import json
import os

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

st.set_page_config(
    page_title="PDF Q&A Assistant",
    page_icon="📄",
    layout="wide"
)

st.title("📄 PDF Q&A Assistant")
st.markdown("Upload a PDF and ask questions about its content using AI.")

# ─── SIDEBAR ────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("OpenRouter API Key", type="password",
                             value=os.environ.get("OPENROUTER_API_KEY", ""))
    st.markdown("---")
    st.markdown("**How it works:**")
    st.markdown("1. Upload a PDF file")
    st.markdown("2. AI reads the content")
    st.markdown("3. Ask any question")
    st.markdown("4. Get instant answers")

# ─── SESSION STATE ──────────────────────────────────────────────
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = ""

# ─── PDF UPLOAD ─────────────────────────────────────────────────
uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file and uploaded_file.name != st.session_state.pdf_name:
    if not PDF_AVAILABLE:
        st.error("PyPDF2 not installed. Run: pip install PyPDF2")
    else:
        with st.spinner("Reading PDF..."):
            try:
                reader = PyPDF2.PdfReader(uploaded_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                
                if text.strip():
                    st.session_state.pdf_text = text[:15000]  # limit context
                    st.session_state.pdf_name = uploaded_file.name
                    st.session_state.chat_history = []
                    st.success(f"✅ PDF loaded: {uploaded_file.name} ({len(reader.pages)} pages)")
                else:
                    st.error("Could not extract text from this PDF. It may be scanned/image-based.")
            except Exception as e:
                st.error(f"Error reading PDF: {e}")

# ─── CHAT INTERFACE ─────────────────────────────────────────────
if st.session_state.pdf_text:
    st.markdown("---")
    st.subheader(f"💬 Ask about: {st.session_state.pdf_name}")

    # Display chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])

    # Question input
    question = st.chat_input("Ask a question about the PDF...")

    if question:
        if not api_key:
            st.error("Please enter your OpenRouter API Key in the sidebar.")
        else:
            st.chat_message("user").write(question)
            st.session_state.chat_history.append({"role": "user", "content": question})

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        system_prompt = f"""You are a helpful assistant that answers questions based on the provided PDF document content.

PDF Content:
{st.session_state.pdf_text}

Answer questions accurately based only on the PDF content. If the answer is not in the document, say so clearly."""

                        messages = [{"role": "system", "content": system_prompt}]
                        for msg in st.session_state.chat_history[-6:]:  # last 3 exchanges
                            messages.append(msg)

                        response = requests.post(
                            "https://openrouter.ai/api/v1/chat/completions",
                            headers={
                                "Authorization": f"Bearer {api_key}",
                                "Content-Type": "application/json"
                            },
                            json={
                                "model": "openai/gpt-4o-mini",
                                "messages": messages,
                                "max_tokens": 1000
                            },
                            timeout=30
                        )

                        if response.status_code == 200:
                            answer = response.json()["choices"][0]["message"]["content"]
                            st.write(answer)
                            st.session_state.chat_history.append({"role": "assistant", "content": answer})
                        else:
                            st.error(f"API Error: {response.status_code}")

                    except Exception as e:
                        st.error(f"Error: {e}")

    # Clear chat button
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()

else:
    st.info("👆 Please upload a PDF file to get started.")
    
    # Demo section
    st.markdown("---")
    st.subheader("What can this tool do?")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("📋 **Summarize**\nGet quick summaries of long documents")
    with col2:
        st.markdown("🔍 **Find Info**\nExtract specific data from reports")
    with col3:
        st.markdown("❓ **Q&A**\nAsk any question about the content")

st.markdown("---")
st.caption("PDF Q&A Assistant — Python · Streamlit · OpenRouter API · GPT-4o-mini")
