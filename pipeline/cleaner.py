from bs4 import BeautifulSoup
import google.generativeai as genai
import os
from dotenv import load_dotenv
from .state import PipelineState

class ContentCleaner:
    def __init__(self):
        load_dotenv()
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-2.0-flash")
    
    def clean_node(self, state: PipelineState):
        soup = BeautifulSoup(state["raw_data"]["html"], "html.parser")
        for script in soup(["script", "style", "nav", "footer", "aside"]):
            script.decompose()

        text = "\n".join([line for line in soup.get_text("\n").splitlines() if line.strip()])
        prompt = f"""
        "Sen bir metin çıkarma uzmanısın.
        Bu HTML içeriğinden SADECE ana makale/içerik metnini çıkar.
        ÇIKARMA:
        - Navigasyon menüleri
        - Reklamlar ve popup'lar  
        - Footer bilgileri
        - Yorum bölümleri
        - Sosyal medya butonları
        - Çerez uyarıları
        - Dil seçenekleri 

        SADECE ana içeriği, başlıklar ve paragraflar halinde döndür.
        İçerik yoksa "İçerik bulunamadı" yaz.

        HTML:
        {text}
        """
        response = self.model.generate_content(prompt)
        state["cleaned_data"] = response.text.strip() if response else ""
        return state