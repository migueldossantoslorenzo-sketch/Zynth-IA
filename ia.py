import streamlit as st
import google.generativeai as genai
import urllib.parse

# --- 1. CONFIGURAÇÕES TÉCNICAS ---
st.set_page_config(page_title="Zynth IA 💠", layout="wide", page_icon="💠")

# Sistema de Chave API (Pega do Secrets no Deploy ou manual no PC)
try:
    CHAVE_API = st.secrets["GOOGLE_API_KEY"]
except:
    CHAVE_API = "SUA_CHAVE_AQUI" # <--- SUA CHAVE PARA TESTE NO PC

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

# --- 4. LÓGICA DE LOGIN ---
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

# --- 5. SISTEMA DE TEMAS DINÂMICOS ---
plano = st.session_state.user_data["plano"]
is_pro = "Free" not in plano

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

# CSS CORRIGIDO (HEADER VISÍVEL PARA A SETINHA APARECER)
st.markdown(f"""
    <style>
    .stApp {{ background-color: {cf}; color: {ct}; }}
    [data-testid="stSidebar"] {{ background-color: {cf}; border-right: 1px solid {cb}; }}
    .stChatMessage {{ background-color: {cc}; border: 1px solid {cb}; border-radius: 10px; }}
    p, h1, h2, h3, span, li, label {{ color: {ct} !important; }}
    .stChatInput {{ border-radius: 20px; border: 1px solid {cb} !important; }}
    .pro-box {{ border: 2px solid {st.session_state.user_data['cor']}; padding: 10px; border-radius: 10px; }}
    #MainMenu, footer {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)

# --- 6. BARRA LATERAL (PAINEL DO CEO) ---
with st.sidebar:
    st.title("💠 Zynth IA")
    cor_u = st.session_state.user_data["cor"]
    st.markdown(f'<p style="color:{cor_u}; font-weight:bold; border:1px solid; border-radius:5px; text-align:center; padding:5px;">{plano}</p>', unsafe_allow_html=True)
    st.write(f"Operador: **{st.session_state.user_name}**")
    
    st.write("---")
    st.subheader("⚙️ Configurações")
    temas = ["Escuro", "Claro"]
    if is_pro: temas += ["Neon", "Ouro"]
    t_sel = st.selectbox("Tema Visual:", temas, index=0)
    if t_sel != st.session_state.tema:
        st.session_state.tema = t_sel
        st.rerun()

    st.write("---")
    st.subheader("📁 Análise de Arquivos")
    arqs = st.file_uploader("Subir arquivos:", accept_multiple_files=True)
    if not is_pro and arqs and len(arqs) > 10:
        st.error("Limite Free: 10 arquivos.")
        arqs = arqs[:10]

    conteudo_extra = ""
    if arqs:
        for a in arqs:
            try: conteudo_extra += f"\nConteúdo de {a.name}:\n{a.read().decode('utf-8')}\n"
            except: pass
        st.success(f"{len(arqs)} arquivos prontos.")

    if not is_pro:
        st.write("---")
        st.subheader("💎 Seja Zynth Pro")
        if st.button("💳 VER PIX"):
            st.write("Copia a chave abaixo:")
            st.code("COLE_AQUI_O_PIX_DO_IRMAO")
            st.info("Mande o print no Instagram!")
            st.caption("Liberação em até 24h.")

    if st.button("Logout"):
        st.session_state.logado = False
        st.rerun()

# --- 7. CHAT E INTELIGÊNCIA ---
st.title("Zynth Core v8.5.2")

for msg in st.session_state.historico:
    with st.chat_message(msg["role"]):
        if msg["role"] == "user" and is_pro:
            st.markdown(f'<div class="pro-box">{msg["content"]}</div>', unsafe_allow_html=True)
        else: st.write(msg["content"])
        if "img" in msg: st.image(msg["img"])

prompt = st.chat_input("Insira o comando...")

if prompt:
    st.session_state.historico.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        if is_pro: st.markdown(f'<div class="pro-box">{prompt}</div>', unsafe_allow_html=True)
        else: st.write(prompt)

    with st.chat_message("assistant"):
        if any(p in prompt.lower() for p in ["imagem", "foto", "gerar"]):
            q = "8k, cinematic, hd" if is_pro else ""
            url = f"https://pollinations.ai/p/{urllib.parse.quote(prompt + ' ' + q)}?width=1024&height=1024&nologo=true"
            st.image(url)
            msg_final = {"role": "assistant", "content": f"Imagem gerada: {prompt}", "img": url}
        else:
            try:
                hist = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.historico[:-1]]
                if not is_pro: hist = hist[-20:]
                
                chat = modelo_zynth.start_chat(history=hist)
                instrucao = "Você é a Zynth IA. Responda de forma superior." if is_pro else "Responda de forma simples."
                response = chat.send_message(f"{instrucao}\n\n{conteudo_extra}\n\nPergunta: {prompt}")
                
                st.write(response.text)
                msg_final = {"role": "assistant", "content": response.text}
            except Exception as e:
                st.error(f"Erro: {e}")
                msg_final = {"role": "assistant", "content": "Erro técnico."}
    
    st.session_state.historico.append(msg_final)
