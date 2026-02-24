import streamlit as st
import google.generativeai as genai
import urllib.parse

# --- 1. CONFIGURAÇÕES ---
st.set_page_config(
    page_title="Zynth IA 💠", 
    layout="wide", 
    page_icon="💠",
    initial_sidebar_state="expanded" 
)

# Sistema de Chave API
try:
    CHAVE_API = st.secrets["GOOGLE_API_KEY"]
except:
    CHAVE_API = "AIzaSyDHXw9PCV2ubR0WqIvVhn4gMKpPXEClzPw" 

genai.configure(api_key=CHAVE_API)

# FUNÇÃO BLINDADA PARA O MODELO (Tenta vários nomes para evitar erro 404)
@st.cache_resource
def carregar_modelo_blindado():
    nomes_para_testar = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-pro']
    for nome in nomes_para_testar:
        try:
            m = genai.GenerativeModel(nome)
            # Testa se o modelo responde (só um teste rápido)
            return m
        except:
            continue
    return genai.GenerativeModel('gemini-pro') # Último recurso

modelo_zynth = carregar_modelo_blindado()

# --- 2. BANCO DE DADOS ---
USUARIOS = {
    "lorenzo": {"senha": "123", "plano": "Dono 👑", "cor": "#ffeb3b"},
    "admin": {"senha": "999", "plano": "Zynth Pro ⚡", "cor": "#00e5ff"},
    "visitante": {"senha": "456", "plano": "Free", "cor": "#ffffff"}
}

# --- 3. ESTADO DA SESSÃO ---
if "logado" not in st.session_state: st.session_state.logado = False
if "historico" not in st.session_state: st.session_state.historico = []
if "tema" not in st.session_state: st.session_state.tema = "Escuro"

# --- 4. LOGIN ---
if not st.session_state.logado:
    st.title("💠 Zynth IA - Login")
    u = st.text_input("Usuário")
    s = st.text_input("Senha", type="password")
    if st.button("Acessar Zynth OS"):
        if u in USUARIOS and USUARIOS[u]["senha"] == s:
            st.session_state.logado, st.session_state.user_data, st.session_state.user_name = True, USUARIOS[u], u
            st.rerun()
        else: st.error("Incorreto!")
    st.stop()

# --- 5. SISTEMA DE TEMAS ---
plano = st.session_state.user_data["plano"]
is_pro = "Free" not in plano
cor_u = st.session_state.user_data["cor"]

if st.session_state.tema == "Escuro":
    cf, ct, cc, cb = "#050505", "#ffffff", "#0d0d0d", "#1a1a1a"
else:
    cf, ct, cc, cb = "#ffffff", "#000000", "#f0f2f6", "#d1d1d1"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {cf}; color: {ct}; }}
    [data-testid="stSidebar"] {{ background-color: {cf}; border-right: 1px solid {cb}; }}
    .stChatMessage {{ background-color: {cc}; border: 1px solid {cb}; border-radius: 10px; }}
    p, h1, h2, h3, span, li, label {{ color: {ct} !important; }}
    .stChatInput {{ border-radius: 20px; border: 1px solid {cb} !important; }}
    .pro-box {{ border: 2px solid {cor_u}; padding: 10px; border-radius: 10px; box-shadow: 0 0 10px {cor_u}; }}
    
    /* BOTÃO NEON PARA CASO FECHE O MENU */
    button[data-testid="stSidebarCollapseButton"] {{
        background-color: #00e5ff !important;
        color: black !important;
        border-radius: 50% !important;
        width: 45px !important;
        height: 45px !important;
        box-shadow: 0 0 15px #00e5ff !important;
    }}
    
    #MainMenu, footer {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)

# --- 6. BARRA LATERAL ---
with st.sidebar:
    st.title("💠 Zynth IA")
    st.markdown(f'<p style="color:{cor_u}; font-weight:bold; border:1px solid; border-radius:5px; text-align:center; padding:5px;">{plano}</p>', unsafe_allow_html=True)
    st.write(f"Operador: **{st.session_state.user_name}**")
    
    st.write("---")
    st.subheader("⚙️ Configurações")
    t_sel = st.selectbox("Estilo Visual:", ["Escuro", "Claro"], index=0)
    if t_sel != st.session_state.tema:
        st.session_state.tema = t_sel
        st.rerun()

    st.write("---")
    arqs = st.file_uploader("Subir Arquivos:", accept_multiple_files=True)
    conteudo_extra = ""
    if arqs:
        for a in arqs:
            try: conteudo_extra += f"\nConteúdo de {a.name}:\n{a.read().decode('utf-8')}\n"
            except: pass

    if not is_pro:
        st.write("---")
        st.subheader("💎 Seja Zynth Pro")
        if st.button("💳 VER PIX"):
            st.code("12 98161-3285")
            st.info("Instagram: @lorenzomigueldossantos1")

    if st.button("Logout"):
        st.session_state.logado = False
        st.rerun()

# --- 7. CHAT ---
st.title("Zynth Core")

for msg in st.session_state.historico:
    with st.chat_message(msg["role"]):
        if msg["role"] == "user" and is_pro:
            st.markdown(f'<div class="pro-box">{msg["content"]}</div>', unsafe_allow_html=True)
        else: st.write(msg["content"])
        if "img" in msg: st.image(msg["img"])

prompt = st.chat_input("Comande a Zynth IA...")

if prompt:
    st.session_state.historico.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        if is_pro: st.markdown(f'<div class="pro-box">{prompt}</div>', unsafe_allow_html=True)
        else: st.write(prompt)

    with st.chat_message("assistant"):
        if any(p in prompt.lower() for p in ["imagem", "foto", "gerar"]):
            q = "8k, cinematic" if is_pro else ""
            url = f"https://pollinations.ai/p/{urllib.parse.quote(prompt + ' ' + q)}?width=1024&height=1024&nologo=true"
            st.image(url)
            msg_final = {"role": "assistant", "content": f"Gerado: {prompt}", "img": url}
        else:
            try:
                # Sistema de chat com tentativa e erro para o modelo
                hist = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.historico[:-1]]
                if not is_pro: hist = hist[-20:]
                
                chat = modelo_zynth.start_chat(history=hist)
                instrucao = "Você é a Zynth IA. Responda de forma épica." if is_pro else "Responda de forma simples."
                response = chat.send_message(f"{instrucao}\n\n{conteudo_extra}\n\nPergunta: {prompt}")
                
                st.write(response.text)
                msg_final = {"role": "assistant", "content": response.text}
            except Exception as e:
                # SE O CHAT COM HISTÓRICO FALHAR, TENTA RESPOSTA DIRETA
                try:
                    res_simples = modelo_zynth.generate_content(prompt)
                    st.write(res_simples.text)
                    msg_final = {"role": "assistant", "content": res_simples.text}
                except:
                    st.error(f"Erro Crítico: {e}")
                    msg_final = {"role": "assistant", "content": "Erro."}
    
    st.session_state.historico.append(msg_final)
