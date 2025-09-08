import streamlit as st
from crawler import WebCrawler
from pipeline.saver import DataSaver
from pipeline.chatbot import ContentChatbot
import validators

class CrawlerApp:
    def __init__(self):
        self.crawler = WebCrawler()
        self.saver = DataSaver()
        self.chatbot = ContentChatbot()
    
    def validate_url(self, url):
        """URL doğrulaması"""
        if not url:
            return False, "URL boş olamaz!"
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            if validators.url(url):
                return True, url
            else:
                return False, "Geçersiz URL formatı!"
        except:
            return False, "URL kontrol edilemedi!"
    
    def setup_page_config(self):
        """Streamlit sayfa konfigürasyonu"""
        st.set_page_config(
            page_title="AI WebCrawler",
            page_icon="🐍",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        st.markdown("""
        <style>
            .main-header {
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                padding: 2rem;
                border-radius: 10px;
                color: white;
                text-align: center;
                margin-bottom: 2rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            
            .crawler-stats {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                padding: 1rem;
                border-radius: 8px;
                color: white;
                margin: 1rem 0;
            }
            
            .url-card {
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                padding: 1rem;
                border-radius: 8px;
                margin: 1rem 0;
                border-left: 5px solid #00a8ff;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .depth-badge {
                background: linear-gradient(45deg, #fa709a 0%, #fee140 100%);
                color: white;
                padding: 0.2rem 0.6rem;
                border-radius: 15px;
                font-size: 0.8rem;
                font-weight: bold;
                display: inline-block;
                margin: 0.2rem;
            }
            
            .success-box {
                background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
                padding: 1rem;
                border-radius: 8px;
                border-left: 4px solid #00d2d3;
                margin: 1rem 0;
            }
            
            .chat-section {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2rem;
                border-radius: 10px;
                margin-top: 2rem;
                color: white;
            }
            
            .chat-message {
                background: rgba(255, 255, 255, 0.1);
                padding: 1rem;
                border-radius: 8px;
                margin: 0.5rem 0;
                backdrop-filter: blur(10px);
            }
            
            .user-message {
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                margin-left: 20%;
            }
            
            .bot-message {
                background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
                margin-right: 20%;
                color: #333;
            }
            
            .stButton > button {
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 0.7rem 2rem;
                border-radius: 25px;
                font-weight: bold;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            }
            
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
            }
            
            .sidebar-section {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 1rem;
                border-radius: 10px;
                color: white;
                margin-bottom: 1rem;
            }
            
            .sidebar-chat {
                background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
                padding: 0.5rem;
                border-radius: 8px;
                margin: 0.5rem 0;
                font-size: 0.8rem;
            }
        </style>
        """, unsafe_allow_html=True)
    
    def render_header(self):
        """Ana başlığı render et"""
        st.markdown("""
        <div class="main-header">
            <h1>AI Web Crawler</h1>
            <p style="font-size: 1.2rem; margin: 0;">Web sitelerini akıllıca tarayan yapay zeka destekli sayfa</p>
            <p style="font-size: 0.9rem; opacity: 0.8; margin-top: 0.5rem;">
                Web sitesini tarayın, içeriği indirin ve veriler hakkında soru sorun! 
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Sol sidebar'ı render et"""
        st.sidebar.markdown("""
        <div class="sidebar-section">
            <h2> Kontrol Paneli</h2>
            <p>Tarama ayarlarınızı buradan yapabilirsiniz</p>
        </div>
        """, unsafe_allow_html=True)

        url_input = st.sidebar.text_input(
            "Web Sitesi URL'si:",
            placeholder="https://example.com ",
            help="Lütfen taramak istediğiniz web sitesinin adresini girin"
        )

        st.sidebar.markdown("### Tarama Parametreleri")
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            max_depth = st.slider(
                "Derinlik",
                min_value=0, 
                max_value=5, 
                value=0,      
                help="0: Sadece ana sayfa, 1+: Alt sayfalar da taranır"
            )
        
        with col2:
            max_links = st.slider(
                " Link Sayısı",
                min_value=1, 
                max_value=10, 
                value=3,
                help="Her sayfadan kaç link alınacak (depth > 0 ise)"
            )

        format_choice = st.sidebar.radio(
            "İndirme Formatı:",
            ("JSON", "PDF"),
            help="Taranan verilerin hangi formatta kaydedileceği"
        )
        
       
        self.render_sidebar_help()
        
        return url_input, max_depth, max_links, format_choice
    
    def render_right_chatbot(self, right_col):
        """Sağ tarafta chatbot bölümünü render et"""
        with right_col:
            st.sidebar.title("AI Asisstant")
            st.markdown("""
            <div class="sidebar-section">
                <h2>AI Asistanı</h2>
                <p>Taranan içerik hakkında soru sorabilirsiniz!</p>
            </div>
            """, unsafe_allow_html=True)
            
            self.chatbot.set_context(st.session_state["crawl_results"])
            
            if "chat_history" not in st.session_state:
                st.session_state["chat_history"] = []
        
            user_question = st.text_input(
                "Sorunuz: ",
                placeholder="Bu metinde hangi konular var?",
                key="right_chat_input"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                send_button = st.button("Gönder", use_container_width=True, type="primary", key="send_btn")
            with col2:
                if st.session_state["chat_history"]:
                    clear_button = st.button("Temizle", use_container_width=True, key="clear_btn")
                else:
                    clear_button = False
            
            
            if send_button and user_question.strip():
               
                st.session_state["chat_history"].append({
                    "type": "user",
                    "content": user_question
                })
                
               
                with st.spinner(" AI düşünüyor..."):
                    bot_response = self.chatbot.answer_question(user_question)
                
                
                st.session_state["chat_history"].append({
                    "type": "bot", 
                    "content": bot_response
                })
               
                st.rerun()
            
            
            if clear_button:
                st.session_state["chat_history"] = []
                st.rerun()
            
            
            if st.session_state["chat_history"]:
                st.markdown("###  Sohbet Geçmişi")
                
                
                with st.container():
                    for message in st.session_state["chat_history"]:
                        if message["type"] == "user":
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                                        padding: 1rem; margin: 0.5rem 0; border-radius: 10px; color: white;">
                                <strong>👤 Sen:</strong><br>{message["content"]}
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                                        padding: 1rem; margin: 0.5rem 0; border-radius: 10px; color: #333;">
                                <strong>AI Asistan:</strong><br>{message["content"]}
                            </div>
                            """, unsafe_allow_html=True)
            
           
    
    def render_sidebar_help(self):
        """Sidebar yardım bölümü"""
        st.sidebar.markdown("---")
        st.sidebar.markdown("""
        <div class="sidebar-section">
            <h3>Nasıl Kullanılır?</h3>
            <ol>
                <li><strong>URL girin ve tarama başlatın</strong></li>
                <li><strong>Parametreleri ayarlayın</strong></li>
                <li><strong>Tarama tamamlandıktan sonra</strong></li>
                <li><strong>Sağ panelden soru sorabilirsiniz! </strong></li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("""
        <div class="sidebar-section">
            <h3>Hızlı İpuçları</h3>
            <ul>
                <li><strong>Derinlik 0:</strong> Sadece ana sayfa</li>
                <li><strong>Derinlik 1:</strong> Ana + 1. seviye linkler</li>
                <li><strong>Chatbot:</strong> Sadece taranan içerik hakkında</li>
                <li><strong>JSON:</strong> Yapılandırılmış veri</li>
                <li><strong>PDF:</strong> Okunabilir belge</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    def run(self):
        """Ana uygulamayı çalıştır"""
        self.setup_page_config()
        self.render_header()
        
        if "shown_urls" not in st.session_state:
            st.session_state["shown_urls"] = set()
        if "crawl_results" not in st.session_state:
            st.session_state["crawl_results"] = []
        if "is_crawling" not in st.session_state:
            st.session_state["is_crawling"] = False
        
        
        url_input, max_depth, max_links, format_choice = self.render_sidebar()
        
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button(" Tarama Başlat", type="primary", use_container_width=True) and url_input:
                is_valid, processed_url = self.validate_url(url_input)
                
                if not is_valid:
                    st.error(f" {processed_url}")
                else:
                    st.session_state["is_crawling"] = True
                    st.session_state["crawl_results"] = []
                    st.session_state["shown_urls"] = set()
                    st.session_state["chat_history"] = []  
                    
                    with st.spinner(" Web sitesi taranıyor... Lütfen bekleyin"):
                        try:
                            results = self.crawler.crawl(
                                processed_url, 
                                depth=0, 
                                max_depth=max_depth, 
                                max_links=max_links, 
                                format_choice=format_choice
                            )
                            st.session_state["crawl_results"] = results if results else []
                            st.session_state["is_crawling"] = False
                            
                            if st.session_state["crawl_results"]:
                                st.success(f" Tarama tamamlandı! {len(st.session_state['crawl_results'])} sayfa bulundu.")
                                st.info(" Artık sağ panelden taranan içerik hakkında soru sorabilirsiniz!")
                            else:
                                st.warning("Hiçbir sayfa bulunamadı.")
                                
                        except Exception as e:
                            st.error(f" Tarama sırasında hata: {str(e)}")
                            st.session_state["is_crawling"] = False

        if st.session_state["crawl_results"]:
            
            main_col, chat_col = st.columns([2, 1])  
            
            with main_col:
                self.display_results(format_choice)
           
            self.render_right_chatbot(chat_col)
    
    def display_results(self, format_choice):
        """Tarama sonuçlarını göster"""
        st.markdown("---")
        
        total_pages = len(st.session_state["crawl_results"])
        successful_pages = len([r for r in st.session_state["crawl_results"] if "error" not in r])
        failed_pages = total_pages - successful_pages
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(" Toplam Sayfa", total_pages)
        with col2:
            st.metric(" Başarılı", successful_pages)
        with col3:
            st.metric(" Hatalı", failed_pages)
        with col4:
            st.metric("Başarı Oranı", f"{(successful_pages/total_pages*100):.1f}%")

        st.markdown("###  Taranan Sayfalar")
        
        for i, result in enumerate(st.session_state["crawl_results"]):
            if "error" in result:
                st.markdown(f"""
                <div class="url-card" style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);">
                    <h4 style="color: white; margin: 0;">⚠ Hata</h4>
                    <p style="margin: 0.5rem 0; color: white;"><strong>URL:</strong> {result['url']}</p>
                    <p style="margin: 0; color: white; opacity: 0.9;"><strong>Hata:</strong> {result['error']}</p>
                    <span class="depth-badge">Derinlik: {result.get('depth', 0)}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                title = result.get("raw_data", {}).get("title", "Başlık Yok")
                text_length = len(result.get("cleaned_data", ""))

                st.markdown(f"""
                <div class="url-card">
                    <h4 style="color: white; margin: 0;"> {title}</h4>
                    <p style="margin: 0.5rem 0; color: white;"><strong>URL:</strong> {result['url']}</p>
                    <p style="margin: 0; color: white; opacity: 0.9;"><strong>İçerik:</strong> {text_length} karakter</p>
                    <span class="depth-badge">Derinlik: {result.get('depth', 0)}</span>
                </div>
                """, unsafe_allow_html=True)
                
                self.saver.display_node(result, format_choice=format_choice)
            
            if i < len(st.session_state["crawl_results"]) - 1:
                st.markdown("---")

if __name__ == "__main__":
    app = CrawlerApp()
    app.run()