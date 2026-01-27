import streamlit as st
import google.generativeai as genai
import urllib.parse

# --- 1. CONFIGURAÇÕES DO SISTEMA ---
st.set_page_config(
    page_title="Zynth IA 💠", 
    layout="wide", 
    page_icon="💠",
    initial_sidebar_state="expanded" 
)

# Sistema de Chave API (Cofre ou Manual)
try:
    CHAVE_API = st.secrets["GOOGLE_API_KEY"]
except:
    CHAVE_API = "AIzaSyDHXw9PCV2ubR0WqIvVhn4gMKpPXEClzPw" 

genai.configure(api_key=CHAVE_API)

@st.cache_resource
def carregar_modelo():
    try:
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for m in modelos:
            if "1.5-flash" in m: return genai.GenerativeModel(m)
        return genai.GenerativeModel(modelos[0])
    except:
        return genai.GenerativeModel('gemini-1.5-flash')

modelo_zynth = carregar_modelo()

# --- 2. BANCO DE DADOS DE USUÁRIOS ---
USUARIOS = {
    "lorenzo": {"senha": "123", "plano": "Dono 👑", "cor": "#ffeb3b"},
    "admin": {"senha": "999", "plano": "Zynth Pro ⚡", "cor": "#00e5ff"},
    "visitante": {"senha": "456", "plano": "Free", "cor": "#ffffff"}
}

# --- 3. ESTADO DA SESSÃO ---
if "logado" not in st.session_state: st.session_state.logado = False
if "historico" not in st.session_state: st.session_state.historico = []
if "tema" not in st.session_state: st.session_state.tema = "Escuro"

# --- 4. TELA DE LOGIN ---
if not st.session_state.logado:
    st.title("💠 Zynth IA - Login")
    u = st.text_input("Usuário")
    s = st.text_input("Senha", type="password")
    if st.button("Acessar Zynth OS"):
        if u in USUARIOS and USUARIOS[u]["senha"] == s:
            st.session_state.logado, st.session_state.user_data, st.session_state.user_name = True, USUARIOS[u], u
            st.rerun()
        else: st.error("Usuário ou senha incorretos!")
    st.stop()

# --- 5. SISTEMA DE CORES E TEMAS ---
plano = st.session_state.user_data["plano"]
is_pro = "Free" not in plano
cor_u = st.session_state.user_data["cor"]

if st.session_state.tema == "Escuro":
    cf, ct, cc, cb = "#050505", "#ffffff", "#0d0d0d", "#1a1a1a"
elif st.session_state.tema == "Claro":
    cf, ct, cc, cb = "#ffffff", "#000000", "#f0f2f6", "#d1d1d1"
elif st.session_state.tema == "Neon" and is_pro:
    cf, ct, cc, cb = "#000000", "#00e5ff", "#001a1a", "#00e5ff"
elif st.session_state.tema == "Ouro" and is_pro:
    cf, ct, cc, cb = "#0a0a00", "#ffd700", "#1a1a00", "#ffd700"
else:
    cf, ct, cc, cb = "#050505", "#ffffff", "#0d0d0d", "#1a1a1a"

# CSS SUPREMO (COM O BOTÃO DE ABRIR NEON E FIXO)
st.markdown(f"""
    <style>
    .stApp {{ background-color: {cf}; color: {ct}; }}
    [data-testid="stSidebar"] {{ background-color: {cf}; border-right: 1px solid {cb}; }}
    .stChatMessage {{ background-color: {cc}; border: 1px solid {cb}; border-radius: 10px; }}
    p, h1, h2, h3, span, li, label {{ color: {ct} !important; }}
    .stChatInput {{ border-radius: 20px; border: 1px solid {cb} !important; }}
    .pro-box {{ border: 2px solid {cor_u}; padding: 10px; border-radius: 10px; box-shadow: 0 0 10px {cor_u}; }}
    
    /* BOTÃO NEON DE ABRIR O MENU (Sempre visível se fechar) */
    button[data-testid="stSidebarCollapseButton"] {{
        background-color: #00e5ff !important;
        color: black !important;
        border-radius: 50% !important;
        width: 45px !important;
        height: 45px !important;
        position: fixed !important;
        top: 15px !important;
        left: 15px !important;
        z-index: 99999 !important;
        box-shadow: 0 0 15px #00e5ff !important;
    }}
    
    #MainMenu, footer {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)

# --- 6. BARRA LATERAL (PAINEL DO CEO) ---
with st.sidebar:
    st.title("💠 Zynth IA")
    st.markdown(f'<p style="color:{cor_u}; font-weight:bold; border:1px solid; border-radius:5px; text-align:center; padding:5px;">{plano}</p>', unsafe_allow_html=True)
    st.write(f"Operador: **{st.session_state.user_name}**")
    
    st.write("---")
    st.subheader("⚙️ Configurações")
    opcoes_tema = ["Escuro", "Claro"]
    if is_pro: opcoes_tema += ["Neon", "Ouro"]
    t_sel = st.selectbox("Estilo Visual:", opcoes_tema, index=0)
    if t_sel != st.session_state.tema:
        st.session_state.tema = t_sel
        st.rerun()

    st.write("---")
    st.subheader("📁 Análise de Arquivos")
    # Coitado dos pobre: 10 arquivos. Pro: Ilimitado
    if is_pro:
        arqs = st.file_uploader("Subir arquivos (Ilimitado):", accept_multiple_files=True)
    else:
        arqs = st.file_uploader("Subir arquivos (Limite: 10):", accept_multiple_files=True)
        if arqs and len(arqs) > 10:
            st.error("Limite Free: 10 arquivos.")
            arqs = arqs[:10]

    conteudo_extra = ""
    if arqs:
        for a in arqs:
            try: conteudo_extra += f"\nConteúdo de {a.name}:\n{a.read().decode('utf-8')}\n"
            except: pass
        st.success(f"{len(arqs)} arquivos processados.")

    if not is_pro:
        st.write("---")
        st.subheader("💎 Seja Zynth Pro")
        if st.button("💳 VER PIX (R$ 20,00)"):
            st.code("12981613285")
            st.info("Mande o print no Instagram! @lorenzomigueldossantos1")
            st.caption("Liberação às 10h e 20h diariamente.")

    if st.button("Sair"):
        st.session_state.logado = False
        st.rerun()

# --- 7. CHAT E INTELIGÊNCIA ---
st.title("Zynth Core")

# Renderizar Histórico
for msg in st.session_state.historico:
    with st.chat_message(msg["role"]):
        if msg["role"] == "user" and is_pro:
            st.markdown(f'<div class="pro-box">{msg["content"]}</div>', unsafe_allow_html=True)
        else: st.write(msg["content"])
        if "img" in msg: st.image(msg["img"])

# Entrada do Usuário
prompt = st.chat_input("Insira o comando...")

if prompt:
    st.session_state.historico.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        if is_pro: st.markdown(f'<div class="pro-box">{prompt}</div>', unsafe_allow_html=True)
        else: st.write(prompt)

    with st.chat_message("assistant"):
        # GERAÇÃO DE IMAGEM
        if any(p in prompt.lower() for p in ["imagem", "foto", "gerar", "desenho"]):
            qualidade = "8k, cinematic, highly detailed" if is_pro else ""
            url = f"https://pollinations.ai/p/{urllib.parse.quote(prompt + ' ' + qualidade)}?width=1024&height=1024&nologo=true"
            st.image(url)
            msg_final = {"role": "assistant", "content": f"💠 Zynth gerou: {prompt}", "img": url}
            st.write(msg_final["content"])
        
        # RESPOSTA DE TEXTO
        else:
            try:
                # Memória: 20 para Free, Total para Pro
                hist = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.historico[:-1]]
                if not is_pro: hist = hist[-20:]
                
                chat = modelo_zynth.start_chat(history=hist)
                instrucao = "Você é a Zynth IA Pro. Responda como um gênio detalhista." if is_pro else "Responda de forma simples."
                response = chat.send_message(f"{instrucao}\n\n{conteudo_extra}\n\nPergunta: {prompt}")
                
                st.write(response.text)
                msg_final = {"role": "assistant", "content": response.text}
            except Exception as e:
                st.error(f"Erro no núcleo Zynth: {e}")
                msg_final = {"role": "assistant", "content": "Erro técnico."}
    
    st.session_state.historico.append(msg_final)
