"""
CSV Analysis & Report Generator
Upload any CSV file and get instant AI-powered analysis and insights.
"""

import streamlit as st
import pandas as pd
import openai
import json
import io
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

st.set_page_config(
    page_title="CSV Analyzer & Report Generator",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
    .stat-card { background: white; border-radius: 12px; padding: 20px;
                 box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center; }
    .insight-box { background: #f0f9ff; border-left: 4px solid #0ea5e9;
                   padding: 12px 16px; border-radius: 0 8px 8px 0; margin: 8px 0; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## ⚙️ Settings")
    api_key = st.text_input("OpenRouter API Key", type="password")
    st.markdown("---")
    st.markdown("## 📊 Analysis Options")
    do_stats    = st.checkbox("Basic Statistics", value=True)
    do_charts   = st.checkbox("Auto Charts", value=True)
    do_ai       = st.checkbox("AI Insights", value=True)
    do_report   = st.checkbox("Download Report", value=True)
    st.markdown("---")
    st.markdown("## 🌍 Language")
    lang = st.selectbox("Output Language", ["English", "Turkish"])

st.title("📊 CSV Analyzer & Report Generator")
st.caption("Upload any CSV file and get instant statistics, charts, and AI-powered insights")

col1, col2, col3 = st.columns(3)
with col1: st.markdown("**📁 Upload CSV** — sales, survey, any data")
with col2: st.markdown("**📈 Auto Analysis** — stats, charts, trends")
with col3: st.markdown("**🤖 AI Insights** — patterns and recommendations")

st.markdown("---")

if not api_key and do_ai:
    st.warning("⚠️ Enter OpenRouter API Key in sidebar for AI insights. Other features work without it.")

uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

# Sample data button
if st.button("📂 Load Sample Sales Data"):
    sample_data = """Month,Sales,Expenses,Profit,Customers,Region
January,45000,32000,13000,120,North
February,38000,28000,10000,95,North
March,52000,35000,17000,145,South
April,61000,38000,23000,178,South
May,58000,40000,18000,165,East
June,72000,45000,27000,210,East
July,68000,42000,26000,195,West
August,75000,48000,27000,225,West
September,82000,52000,30000,248,North
October,79000,50000,29000,235,South
November,91000,58000,33000,275,East
December,105000,65000,40000,320,West"""
    uploaded_file = io.StringIO(sample_data)
    st.success("✅ Sample data loaded!")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Could not read CSV: {e}")
        st.stop()
    
    st.success(f"✅ File loaded: {df.shape[0]} rows × {df.shape[1]} columns")
    
    # Preview
    with st.expander("👀 Data Preview", expanded=True):
        st.dataframe(df.head(10), use_container_width=True)
    
    # ── BASIC STATS ─────────────────────────────────────────────
    if do_stats:
        st.markdown("## 📊 Basic Statistics")
        
        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="stat-card"><h2>{df.shape[0]}</h2><p>Total Rows</p></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stat-card"><h2>{df.shape[1]}</h2><p>Columns</p></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="stat-card"><h2>{len(num_cols)}</h2><p>Numeric Columns</p></div>', unsafe_allow_html=True)
        with col4:
            missing = df.isnull().sum().sum()
            st.markdown(f'<div class="stat-card"><h2>{missing}</h2><p>Missing Values</p></div>', unsafe_allow_html=True)
        
        st.markdown("### 🔢 Numeric Column Statistics")
        if num_cols:
            st.dataframe(df[num_cols].describe().round(2), use_container_width=True)
        
        if cat_cols:
            st.markdown("### 📝 Categorical Columns")
            for col in cat_cols[:3]:
                vc = df[col].value_counts()
                st.markdown(f"**{col}:** {', '.join([f'{k} ({v})' for k, v in vc.head(5).items()])}")
    
    # ── CHARTS ──────────────────────────────────────────────────
    if do_charts and len(df.select_dtypes(include=['number']).columns) > 0:
        st.markdown("## 📈 Auto Charts")
        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        charts_made = 0
        cols = st.columns(2)
        
        # Line chart for first numeric column
        if len(num_cols) >= 1:
            with cols[charts_made % 2]:
                fig, ax = plt.subplots(figsize=(8, 4))
                df[num_cols[0]].plot(ax=ax, color='#0066cc', linewidth=2)
                ax.set_title(f'{num_cols[0]} Trend', fontsize=14, fontweight='bold')
                ax.set_xlabel('Index')
                ax.grid(True, alpha=0.3)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
                charts_made += 1
        
        # Bar chart for second numeric column
        if len(num_cols) >= 2:
            with cols[charts_made % 2]:
                fig, ax = plt.subplots(figsize=(8, 4))
                df[num_cols[1]].plot(kind='bar', ax=ax, color='#22c55e', alpha=0.8)
                ax.set_title(f'{num_cols[1]} Distribution', fontsize=14, fontweight='bold')
                ax.set_xlabel('Index')
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
                charts_made += 1
        
        # Correlation heatmap if 3+ numeric cols
        if len(num_cols) >= 3:
            with cols[charts_made % 2]:
                fig, ax = plt.subplots(figsize=(8, 6))
                corr = df[num_cols].corr()
                im = ax.imshow(corr, cmap='coolwarm', aspect='auto')
                ax.set_xticks(range(len(num_cols)))
                ax.set_yticks(range(len(num_cols)))
                ax.set_xticklabels(num_cols, rotation=45, ha='right')
                ax.set_yticklabels(num_cols)
                plt.colorbar(im)
                ax.set_title('Correlation Matrix', fontsize=14, fontweight='bold')
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
                charts_made += 1
    
    # ── AI INSIGHTS ─────────────────────────────────────────────
    if do_ai and api_key:
        st.markdown("## 🤖 AI Insights")
        
        with st.spinner("AI is analyzing your data..."):
            # Prepare summary for AI
            summary = {
                "rows": df.shape[0],
                "columns": df.shape[1],
                "column_names": df.columns.tolist(),
                "dtypes": df.dtypes.astype(str).to_dict(),
                "sample": df.head(5).to_dict(orient="records"),
                "stats": df.describe().round(2).to_dict() if len(df.select_dtypes(include=['number']).columns) > 0 else {}
            }
            
            lang_note = "Respond in Turkish." if lang == "Turkish" else "Respond in English."
            
            prompt = f"""Analyze this dataset and provide insights. {lang_note}

Dataset info:
{json.dumps(summary, ensure_ascii=False, default=str)[:3000]}

Return ONLY this JSON:
{{
  "overview": "2-3 sentence overview of what this data is about",
  "key_findings": ["finding 1", "finding 2", "finding 3", "finding 4"],
  "trends": ["trend 1", "trend 2", "trend 3"],
  "recommendations": ["recommendation 1", "recommendation 2", "recommendation 3"],
  "data_quality": "assessment of data quality and completeness",
  "best_visualization": "what type of chart would best represent this data"
}}"""
            
            try:
                client = openai.OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
                resp = client.chat.completions.create(
                    model="openai/gpt-4o-mini",
                    max_tokens=1000,
                    messages=[
                        {"role": "system", "content": "You are a data analyst. Return only valid JSON."},
                        {"role": "user", "content": prompt}
                    ]
                )
                raw = resp.choices[0].message.content.strip().replace("```json","").replace("```","").strip()
                insights = json.loads(raw)
                
                st.markdown(f'<div class="insight-box">📋 <b>Overview:</b> {insights.get("overview","")}</div>', unsafe_allow_html=True)
                
                col_l, col_r = st.columns(2)
                with col_l:
                    st.markdown("### 🔍 Key Findings")
                    for f in insights.get("key_findings", []):
                        st.markdown(f"• {f}")
                    
                    st.markdown("### 📈 Trends")
                    for t in insights.get("trends", []):
                        st.markdown(f"• {t}")
                
                with col_r:
                    st.markdown("### 💡 Recommendations")
                    for r in insights.get("recommendations", []):
                        st.markdown(f"• {r}")
                    
                    st.markdown("### ✅ Data Quality")
                    st.info(insights.get("data_quality", ""))
                    
                    st.markdown("### 📊 Best Visualization")
                    st.success(insights.get("best_visualization", ""))
                    
            except Exception as e:
                st.error(f"AI analysis failed: {e}")
    
    # ── DOWNLOAD REPORT ─────────────────────────────────────────
    if do_report:
        st.markdown("---")
        st.markdown("## 📥 Download")
        
        col1, col2 = st.columns(2)
        with col1:
            csv_out = df.to_csv(index=False)
            st.download_button(
                "📥 Download Cleaned CSV",
                data=csv_out,
                file_name="analyzed_data.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col2:
            excel_out = io.BytesIO()
            with pd.ExcelWriter(excel_out, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name="Data", index=False)
                df.describe().round(2).to_excel(writer, sheet_name="Statistics")
            excel_out.seek(0)
            st.download_button(
                "📥 Download Excel Report",
                data=excel_out,
                file_name="data_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
