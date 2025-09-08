import google.generativeai as genai
import os
from dotenv import load_dotenv
from .state import PipelineState

class ContentChatbot:
    def __init__(self):
        load_dotenv()
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.context_data = []
    
    def set_context(self, crawl_results):
        self.context_data = []
        for result in crawl_results:
            if result.get("cleaned_data") and result.get("cleaned_data").strip():
                context_item = {
                    "url": result.get("url", ""),
                    "title": result.get("raw_data", {}).get("title", "Başlık Yok"),
                    "content": result.get("cleaned_data", ""),
                    "depth": result.get("depth", 0)
                }
                self.context_data.append(context_item)
    
    def answer_question(self, question):
        if not self.context_data:
            return "Henüz herhangi bir içerik taranmamış. Lütfen önce bir web sitesi tarayın."
             
        combined_content = ""
        for item in self.context_data:
            combined_content += f"\n--- {item['title']} (URL: {item['url']}) ---\n{item['content']}\n"
        
        if len(combined_content) > 30000:  
            combined_content = combined_content[:30000] + "\n[İçerik kısaltılmış...]"
        
        prompt = f"""
        Sen bir web içeriği analiz asistanısın. Sadece sana verilen web içeriklerine dayanarak soruları yanıtla.
        KURALLAR:
        1. SADECE verilen içeriklerden bilgi kullan
        2. İçerikte olmayan bilgileri ASLA uydurup söyleme
        3. Emin olmadığın konularda "Bu bilgi taranan içeriklerde bulunmuyor" de
        4. Genel bilgi sorularını reddet, sadece taranan içerikle ilgili soruları yanıtla
        5. Yanıtlarını Türkçe ver
        6.İçerik için kaynak vermene gerek yok.
        7.Çok ayrıntılı özet verme (Tabi kullanıcı özellikle istemezse)

        TARANAN WEB İÇERİKLERİ:
        {combined_content}

        KULLANICI SORUSU: {question}

        YANITINI VER:
        """
       
        response = self.model.generate_content(prompt)
        return response.text.strip() if response else "Yanıt alınamadı, lütfen tekrar deneyin."
        