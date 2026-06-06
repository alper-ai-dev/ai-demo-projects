"""
PDF to Word Report Generator
Upload a PDF → AI analyzes it → Downloads a formatted Word report
"""

import streamlit as st
import openai
import PyPDF2
import subprocess
import tempfile
import os
import io
import json

st.set_page_config(
    page_title="PDF → Word Report Generator",
    page_icon="📝",
    layout="wide"
)

st.markdown("""
<style>
    .step-box { background: white; border-radius: 12px; padding: 20px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin: 10px 0; }
    .step-num { background: #0066cc; color: white; border-radius: 50%; 
                width: 32px; height: 32px; display: inline-flex; 
                align-items: center; justify-content: center; 
                font-weight: bold; margin-right: 10px; }
</style>
""", unsafe_allow_html=True)

# ─── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    api_key = st.text_input("OpenRouter API Key", type="password")
    
    st.markdown("---")
    st.markdown("## 📄 Report Options")
    report_title = st.text_input("Report Title", value="Document Analysis Report")
    report_lang = st.selectbox("Report Language", ["English", "Turkish"])
    include_summary = st.checkbox("Executive Summary", value=True)
    include_keypoints = st.checkbox("Key Points", value=True)
    include_recommendations = st.checkbox("Recommendations", value=True)
    include_conclusion = st.checkbox("Conclusion", value=True)

# ─── MAIN ──────────────────────────────────────────────────────
st.title("📝 PDF → Word Report Generator")
st.caption("Upload any PDF document and get a professionally formatted Word report")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**📄 Upload PDF**\nAny document, contract, research paper, or report")
with col2:
    st.markdown("**🤖 AI Analysis**\nAI reads and extracts key information")
with col3:
    st.markdown("**📥 Download Word**\nGet a formatted .docx report instantly")

st.markdown("---")

if not api_key:
    st.warning("⚠️ Please enter your OpenRouter API Key in the sidebar.")
else:
    uploaded_file = st.file_uploader("Upload PDF Document", type="pdf")
    
    if uploaded_file:
        st.success(f"✅ {uploaded_file.name} uploaded")
        
        if st.button("🚀 Generate Word Report", type="primary", use_container_width=True):
            
            progress = st.progress(0)
            status = st.empty()
            
            # Step 1: Extract text
            status.info("📖 Reading PDF...")
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
            full_text = ""
            for page in pdf_reader.pages:
                full_text += page.extract_text() + "\n"
            
            if not full_text.strip():
                st.error("Could not extract text from PDF. The PDF might be scanned/image-based.")
                st.stop()
            
            progress.progress(20)
            
            # Step 2: AI Analysis
            status.info("🤖 AI is analyzing the document...")
            
            client = openai.OpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1"
            )
            
            lang_instruction = "in Turkish" if report_lang == "Turkish" else "in English"
            
            sections_needed = []
            if include_summary: sections_needed.append("executive_summary")
            if include_keypoints: sections_needed.append("key_points")
            if include_recommendations: sections_needed.append("recommendations")
            if include_conclusion: sections_needed.append("conclusion")
            
            prompt = f"""Analyze this document and create a structured report {lang_instruction}.

Document text:
{full_text[:6000]}

Return ONLY a JSON object with these fields:
{{
  "document_type": "type of document",
  "main_topic": "main topic in one sentence",
  "executive_summary": "3-4 paragraph executive summary",
  "key_points": ["point 1", "point 2", "point 3", "point 4", "point 5"],
  "recommendations": ["recommendation 1", "recommendation 2", "recommendation 3"],
  "conclusion": "concluding paragraph",
  "key_stats": ["stat or fact 1", "stat or fact 2", "stat or fact 3"]
}}"""
            
            try:
                resp = client.chat.completions.create(
                    model="openai/gpt-4o-mini",
                    max_tokens=2000,
                    messages=[
                        {"role": "system", "content": "You are a professional document analyst. Return only valid JSON."},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                raw = resp.choices[0].message.content.strip()
                raw = raw.replace("```json", "").replace("```", "").strip()
                analysis = json.loads(raw)
                
            except Exception as e:
                st.error(f"AI analysis failed: {e}")
                st.stop()
            
            progress.progress(60)
            
            # Step 3: Generate Word document
            status.info("📝 Creating Word document...")
            
            output_path = os.path.join(tempfile.gettempdir(), "report.docx")
            output_path_js = output_path.replace("\\", "\\\\")
            
            # Build JS for docx generation
            key_points_js = "\n".join([
                f'new Paragraph({{ numbering: {{ reference: "bullets", level: 0 }}, children: [new TextRun("{p.replace(chr(34), chr(39))}")]  }}),'
                for p in analysis.get("key_points", [])
            ])
            
            recommendations_js = "\n".join([
                f'new Paragraph({{ numbering: {{ reference: "numbers", level: 0 }}, children: [new TextRun("{r.replace(chr(34), chr(39))}")]  }}),'
                for r in analysis.get("recommendations", [])
            ])
            
            summary_paras = analysis.get("executive_summary", "").split("\n")
            summary_js = "\n".join([
                f'new Paragraph({{ children: [new TextRun("{p.strip().replace(chr(34), chr(39))}")]  }}),'
                for p in summary_paras if p.strip()
            ])
            
            js_code = f"""
const fs = require('fs');
const {{ Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType,
        LevelFormat }} = require('docx');

const doc = new Document({{
  numbering: {{
    config: [
      {{ reference: "bullets",
        levels: [{{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: {{ paragraph: {{ indent: {{ left: 720, hanging: 360 }} }} }} }}] }},
      {{ reference: "numbers",
        levels: [{{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: {{ paragraph: {{ indent: {{ left: 720, hanging: 360 }} }} }} }}] }},
    ]
  }},
  styles: {{
    default: {{ document: {{ run: {{ font: "Arial", size: 24 }} }} }},
    paragraphStyles: [
      {{ id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: {{ size: 36, bold: true, font: "Arial", color: "1F4E79" }},
        paragraph: {{ spacing: {{ before: 360, after: 240 }}, outlineLevel: 0 }} }},
      {{ id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: {{ size: 28, bold: true, font: "Arial", color: "2E75B6" }},
        paragraph: {{ spacing: {{ before: 280, after: 160 }}, outlineLevel: 1 }} }},
    ]
  }},
  sections: [{{
    properties: {{
      page: {{
        size: {{ width: 12240, height: 15840 }},
        margin: {{ top: 1440, right: 1440, bottom: 1440, left: 1440 }}
      }}
    }},
    children: [
      // Title
      new Paragraph({{
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("{report_title.replace(chr(34), chr(39))}")]
      }}),
      
      // Document type & topic
      new Paragraph({{
        children: [
          new TextRun({{ text: "Document Type: ", bold: true }}),
          new TextRun("{analysis.get('document_type', '').replace(chr(34), chr(39))}")
        ]
      }}),
      new Paragraph({{
        children: [
          new TextRun({{ text: "Main Topic: ", bold: true }}),
          new TextRun("{analysis.get('main_topic', '').replace(chr(34), chr(39))}")
        ],
        spacing: {{ after: 240 }}
      }}),

      // Executive Summary
      new Paragraph({{ heading: HeadingLevel.HEADING_2, children: [new TextRun("Executive Summary")] }}),
      {summary_js}

      // Key Points
      new Paragraph({{ heading: HeadingLevel.HEADING_2, children: [new TextRun("Key Points")] }}),
      {key_points_js}

      // Recommendations  
      new Paragraph({{ heading: HeadingLevel.HEADING_2, children: [new TextRun("Recommendations")], spacing: {{ before: 240 }} }}),
      {recommendations_js}

      // Conclusion
      new Paragraph({{ heading: HeadingLevel.HEADING_2, children: [new TextRun("Conclusion")], spacing: {{ before: 240 }} }}),
      new Paragraph({{ children: [new TextRun("{analysis.get('conclusion', '').replace(chr(34), chr(39))}")]  }}),
      
      // Footer note
      new Paragraph({{
        children: [new TextRun({{ text: "Generated by PDF Report Generator • AI-Powered Analysis", italics: true, color: "888888", size: 18 }})],
        alignment: AlignmentType.CENTER,
        spacing: {{ before: 480 }}
      }})
    ]
  }}]
}});

Packer.toBuffer(doc).then(buffer => {{
  fs.writeFileSync('{output_path_js}', buffer);
  console.log('OK');
}});
"""
            
            # JS dosyasını ai-proje klasörüne yaz (docx modülü orada)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            js_path = os.path.join(script_dir, "_temp_report.js")
            
            try:
                with open(js_path, 'w', encoding='utf-8') as f:
                    f.write(js_code)
                
                result = subprocess.run(
                    ['node', js_path],
                    capture_output=True, text=True, timeout=30,
                    cwd=script_dir
                )
                if result.returncode != 0:
                    st.error(f"Word generation failed: {result.stderr}")
                    st.stop()
            finally:
                if os.path.exists(js_path):
                    os.unlink(js_path)
            
            progress.progress(90)
            
            # Step 4: Offer download
            status.empty()
            progress.empty()
            
            with open(output_path, 'rb') as f:
                docx_bytes = f.read()
            
            st.success("✅ Word report generated successfully!")
            
            # Preview
            with st.expander("📋 Report Preview", expanded=True):
                st.markdown(f"**Document Type:** {analysis.get('document_type', '')}")
                st.markdown(f"**Main Topic:** {analysis.get('main_topic', '')}")
                st.markdown("**Key Points:**")
                for kp in analysis.get("key_points", []):
                    st.markdown(f"• {kp}")
            
            st.download_button(
                label="📥 Download Word Report (.docx)",
                data=docx_bytes,
                file_name=f"report_{uploaded_file.name.replace('.pdf', '')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )