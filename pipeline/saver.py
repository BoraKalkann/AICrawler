import streamlit as st
import json
from fpdf import FPDF
import time
import os
from datetime import datetime

class DataSaver:
    
    def display_node(self, state, format_choice="JSON", is_main_url=False):
        if "url" not in state:
            st.error("Lütfen geçerli bir URL sağlayın!")
            return None
        
        
        scraped_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
        content = {
            "url": state["url"],
            "title": state.get("raw_data", {}).get("title", "Başlık Yok"),
            "text": state.get("cleaned_data", ""),
            "scraped_at": scraped_at,
            "depth": state.get("depth", 0),
            "total_characters": len(state.get("cleaned_data", "")),
            "total_words": len(state.get("cleaned_data", "").split()) if state.get("cleaned_data") else 0
        }
        unique_key = f"{content['url']}_{time.time()}"
        
        
        if is_main_url and content["text"].strip():
            st.markdown("###  İçerik Analizi")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button(" İçeriği Özetle", key=f"summarize_{unique_key}", type="secondary"):
                    with st.spinner("İçerik özetleniyor..."):
                        summary = self.analyser.analyze_content(state)
                        st.session_state[f"summary_{unique_key}"] = summary
            
            with col2:
                if st.button(" İçerik İstatistikleri", key=f"stats_{unique_key}", type="secondary"):
                    stats = self.analyser.get_content_stats(state)
                    st.session_state[f"stats_{unique_key}"] = stats
            
        
            if f"summary_{unique_key}" in st.session_state:
                st.markdown("####  İçerik Özeti")
                st.info(st.session_state[f"summary_{unique_key}"])
            
            
            if f"stats_{unique_key}" in st.session_state:
                st.markdown("####  İçerik İstatistikleri")
                stats = st.session_state[f"stats_{unique_key}"]
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Kelime", stats.get("kelime_sayisi", 0))
                with col2:
                    st.metric("Karakter", stats.get("karakter_sayisi", 0))
                with col3:
                    st.metric("Satır", stats.get("satir_sayisi", 0))
                with col4:
                    st.metric("Okuma Süresi", stats.get("tahmini_okuma_suresi", "N/A"))
            
            st.markdown("---")
        
       
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 0.5rem; border-radius: 5px; color: white; font-size: 0.9rem; margin-bottom: 1rem;">
            <strong> Tarama Bilgileri:</strong> {scraped_at} • <strong> İçerik:</strong> {content['total_words']} kelime, {content['total_characters']} karakter
        </div>
        """, unsafe_allow_html=True)
        
      
        if format_choice == "JSON":
            json_content = json.dumps(content, ensure_ascii=False, indent=2)
            st.json(content)
            st.download_button(
                label=" JSON olarak indir",
                data=json_content,
                file_name=f"{content['title']}_{scraped_at.replace(':', '-').replace(' ', '_')}.json",
                mime="application/json",
                key=f"json_{unique_key}"
            )
        elif format_choice == "PDF":
           
            pdf_content = f"""
             URL: {content['url']}
             BAŞLIK: {content['title']}
             TARAMA TARİHİ: {scraped_at}
             İSTATİSTİKLER: {content['total_words']} kelime • {content['total_characters']} karakter
             DERİNLİK: {content['depth']}

            ════════════════════════════════════════

            İÇERİK:

            {content['text']}

            ════════════════════════════════════════
             Bu veri AI Web Crawler tarafından otomatik olarak çekilmiştir.
            """
            
            st.text_area("PDF Önizleme", pdf_content, height=200)
            
            pdf = FPDF()
            pdf.add_page()
            font_file = os.path.join("pipeline", "fonts", "DejaVuSans.ttf")
            if os.path.exists(font_file):
                pdf.add_font("DejaVu", "", font_file, uni=True)
                pdf.set_font("DejaVu", "", 12)
            else:
                pdf.set_font("helvetica", "", 12)
            
            try:
                pdf.multi_cell(0, 5, pdf_content.encode('latin1', 'replace').decode('latin1'))
            except:
                simple_content = f"URL: {content['url']}\nBaslik: {content['title']}\nTarih: {scraped_at}\n\n{content['text']}"
                pdf.multi_cell(0, 5, simple_content)
                
            pdf_output = pdf.output(dest='S')
            if isinstance(pdf_output, str):
                pdf_bytes = pdf_output.encode('latin1')
            else:
                pdf_bytes = bytes(pdf_output)
            st.download_button(
                label=" PDF olarak indir",
                data=pdf_bytes,
                file_name=f"{content['title']}_{scraped_at.replace(':', '-').replace(' ', '_')}.pdf",
                mime="application/pdf",
                key=f"pdf_{unique_key}"
            )
        return state