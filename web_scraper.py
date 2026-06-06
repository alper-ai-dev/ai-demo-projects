"""
Web Scraping Tool
Extract data from any website — prices, headlines, links, tables, and more.
"""

import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import re
from urllib.parse import urljoin, urlparse
import io

st.set_page_config(
    page_title="Web Scraper Tool",
    page_icon="🕷️",
    layout="wide"
)

st.markdown("""
<style>
    .result-card { background: white; border-radius: 12px; padding: 20px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin: 10px 0; }
    .tag { display: inline-block; padding: 3px 10px; border-radius: 12px;
           margin: 3px; font-size: 0.8em; background: #f0f4ff; color: #1e40af; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.markdown("---")
    st.markdown("## 🎯 What to Extract")
    extract_titles    = st.checkbox("Page Title & Meta", value=True)
    extract_headings  = st.checkbox("Headings (H1, H2, H3)", value=True)
    extract_links     = st.checkbox("All Links", value=True)
    extract_images    = st.checkbox("Image URLs", value=False)
    extract_tables    = st.checkbox("Tables", value=True)
    extract_text      = st.checkbox("Main Text Content", value=True)
    extract_emails    = st.checkbox("Email Addresses", value=True)
    extract_phones    = st.checkbox("Phone Numbers", value=True)
    st.markdown("---")
    st.markdown("## 📥 Export Format")
    export_format = st.selectbox("Download as", ["CSV", "JSON", "Excel"])

st.title("🕷️ Web Scraper Tool")
st.caption("Extract data from any website instantly — no coding required")

col1, col2, col3 = st.columns(3)
with col1: st.markdown("**🔗 Enter URL** — any public website")
with col2: st.markdown("**⚡ Instant Extract** — titles, links, tables, text")
with col3: st.markdown("**📥 Download** — CSV, JSON, or Excel")

st.markdown("---")

# Sample URLs
st.markdown("### 🌐 Enter website URL:")
sample_urls = {
    "Hacker News": "https://news.ycombinator.com",
    "Wikipedia - Python": "https://en.wikipedia.org/wiki/Python_(programming_language)",
    "Books to Scrape": "https://books.toscrape.com",
}

col_url, col_sample = st.columns([3, 1])
with col_url:
    url_input = st.text_input(
        "URL",
        placeholder="https://example.com",
        label_visibility="collapsed"
    )
with col_sample:
    selected_sample = st.selectbox("Or try a sample", ["—"] + list(sample_urls.keys()), label_visibility="collapsed")
    if selected_sample != "—":
        url_input = sample_urls[selected_sample]

scrape_btn = st.button("🕷️ Start Scraping", type="primary", use_container_width=True)

if scrape_btn and url_input:
    # Add https if missing
    if not url_input.startswith("http"):
        url_input = "https://" + url_input
    
    with st.spinner(f"Scraping {url_input}..."):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            response = requests.get(url_input, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. The website took too long to respond.")
            st.stop()
        except requests.exceptions.ConnectionError:
            st.error("❌ Could not connect to the website. Check the URL.")
            st.stop()
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.stop()
    
    st.success(f"✅ Successfully scraped! Status: {response.status_code}")
    
    all_data = {}
    
    # ── PAGE TITLE & META ───────────────────────────────────────
    if extract_titles:
        st.markdown("### 📄 Page Info")
        col1, col2 = st.columns(2)
        
        title = soup.find("title")
        title_text = title.get_text(strip=True) if title else "N/A"
        
        meta_desc = soup.find("meta", attrs={"name": "description"})
        desc_text = meta_desc.get("content", "N/A") if meta_desc else "N/A"
        
        meta_kw = soup.find("meta", attrs={"name": "keywords"})
        kw_text = meta_kw.get("content", "N/A") if meta_kw else "N/A"
        
        with col1:
            st.metric("Page Title", title_text[:80])
            st.text_area("Meta Description", desc_text, height=80)
        with col2:
            st.metric("URL", url_input[:60])
            st.text_area("Meta Keywords", kw_text, height=80)
        
        all_data["page_info"] = {
            "title": title_text, "description": desc_text,
            "keywords": kw_text, "url": url_input
        }
    
    # ── HEADINGS ────────────────────────────────────────────────
    if extract_headings:
        headings = []
        for tag in ["h1", "h2", "h3"]:
            for h in soup.find_all(tag):
                text = h.get_text(strip=True)
                if text:
                    headings.append({"type": tag.upper(), "text": text})
        
        if headings:
            st.markdown(f"### 📰 Headings ({len(headings)} found)")
            df_h = pd.DataFrame(headings)
            st.dataframe(df_h, use_container_width=True, height=200)
            all_data["headings"] = headings
    
    # ── LINKS ───────────────────────────────────────────────────
    if extract_links:
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True)
            full_url = urljoin(url_input, href)
            if text and len(text) > 1:
                links.append({"text": text[:80], "url": full_url})
        
        links = links[:100]  # max 100
        if links:
            st.markdown(f"### 🔗 Links ({len(links)} found, showing first 100)")
            df_l = pd.DataFrame(links)
            st.dataframe(df_l, use_container_width=True, height=200)
            all_data["links"] = links
    
    # ── TABLES ──────────────────────────────────────────────────
    if extract_tables:
        tables = soup.find_all("table")
        if tables:
            st.markdown(f"### 📊 Tables ({len(tables)} found)")
            for i, table in enumerate(tables[:3]):
                try:
                    df_t = pd.read_html(str(table))[0]
                    st.markdown(f"**Table {i+1}** ({df_t.shape[0]} rows × {df_t.shape[1]} cols)")
                    st.dataframe(df_t, use_container_width=True, height=200)
                    all_data[f"table_{i+1}"] = df_t.to_dict(orient="records")
                except:
                    pass
    
    # ── EMAILS ──────────────────────────────────────────────────
    if extract_emails:
        page_text = soup.get_text()
        emails = list(set(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', page_text)))
        if emails:
            st.markdown(f"### 📧 Email Addresses ({len(emails)} found)")
            for email in emails:
                st.markdown(f'<span class="tag">📧 {email}</span>', unsafe_allow_html=True)
            all_data["emails"] = emails
    
    # ── PHONES ──────────────────────────────────────────────────
    if extract_phones:
        page_text = soup.get_text()
        phones = list(set(re.findall(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', page_text)))[:10]
        if phones:
            st.markdown(f"### 📞 Phone Numbers ({len(phones)} found)")
            for phone in phones[:10]:
                st.markdown(f'<span class="tag">📞 {phone}</span>', unsafe_allow_html=True)
            all_data["phones"] = phones
    
    # ── IMAGES ──────────────────────────────────────────────────
    if extract_images:
        images = []
        for img in soup.find_all("img", src=True):
            src = urljoin(url_input, img["src"])
            alt = img.get("alt", "")
            images.append({"alt": alt, "url": src})
        
        images = images[:50]
        if images:
            st.markdown(f"### 🖼️ Images ({len(images)} found)")
            df_img = pd.DataFrame(images)
            st.dataframe(df_img, use_container_width=True, height=200)
            all_data["images"] = images
    
    # ── MAIN TEXT ───────────────────────────────────────────────
    if extract_text:
        for tag in ["script", "style", "nav", "footer", "header"]:
            for s in soup.find_all(tag):
                s.decompose()
        
        main_text = soup.get_text(separator="\n", strip=True)
        main_text = "\n".join([l for l in main_text.split("\n") if len(l) > 30])[:3000]
        
        if main_text:
            st.markdown("### 📝 Main Text Content")
            st.text_area("Extracted text", main_text, height=200)
            all_data["main_text"] = main_text
    
    # ── DOWNLOAD ────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📥 Download Scraped Data")
    
    if export_format == "JSON":
        json_str = json.dumps(all_data, ensure_ascii=False, indent=2)
        st.download_button(
            "📥 Download JSON",
            data=json_str,
            file_name="scraped_data.json",
            mime="application/json",
            use_container_width=True
        )
    elif export_format == "CSV":
        # Flatten to CSV - use links or headings
        main_df = pd.DataFrame(all_data.get("links", all_data.get("headings", [{"data": str(all_data)}])))
        csv = main_df.to_csv(index=False)
        st.download_button(
            "📥 Download CSV",
            data=csv,
            file_name="scraped_data.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:  # Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for key, val in all_data.items():
                if isinstance(val, list) and val and isinstance(val[0], dict):
                    pd.DataFrame(val).to_excel(writer, sheet_name=key[:31], index=False)
        output.seek(0)
        st.download_button(
            "📥 Download Excel",
            data=output,
            file_name="scraped_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
