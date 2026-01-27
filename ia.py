import streamlit as st
import google.generativeai as genai
import urllib.parse

# --- 1. CONFIGURAÇÕES TÉCNICAS ---
st.set_page_config(page_title="Zynth IA 💠", layout="wide", page_icon="💠")

try:
    CHAVE_API = st.secrets["GOOGLE_API_KEY"]
except:
    CHAVE_API = "AIzaSyDHXw9PCV2ubR0WqIvVhn4gMKpPXEClzPw" # <--- SUA CHAVE PARA TESTE NO PC

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

# --- 2. BANCO DE DADOS ---
USUARIOS = {
    "lorenzo": {"senha": "123", "plano": "Dono 👑", "cor": "#ffeb3b"},
    "admin": {"senha": "999", "plano": "Zynth Pro ⚡", "cor": "#00e5ff"},
    "visitante": {"senha": "456", "plano": "Free", "cor": "#ffffff"}
}

# --- 3. ESTADO DA SESSÃO ---
if "logado" not in st.session_state: st.session_state.logado = False
if "historico" not in st.session_state: st.session_state.historico = []

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

# --- 5. ESTILO CSS DARK ---
plano = st.session_state.user_data["plano"]
is_pro = "Free" not in plano

st.markdown(f"""
    <style>
    .stApp {{ background-color: #050505; color: white; }}
    [data-testid="stSidebar"] {{ background-color: #080808; border-right: 1px solid #222; }}
    .stChatMessage {{ background-color: #0d0d0d; border-radius: 10px; border: 1px solid #222; }}
    p, h1, h2, h3, span, label {{ color: white !important; }}
    .badge {{ color: {st.session_state.user_data['cor']}; font-weight: bold; border: 1px solid; border-radius: 5px; text-align: center; padding: 5px; }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)

# --- 6. BARRA LATERAL ---
with st.sidebar:
    st.title("💠 Zynth IA")
    st.markdown(f'<p class="badge">{plano}</p>', unsafe_allow_html=True)
    st.write(f"Operador: {st.session_state.user_name}")
    
    st.write("---")
    st.subheader("📁 Upload de Arquivos")
    
    # LÓGICA DE ARQUIVOS (O que você pediu!)
    if is_pro:
        arquivos = st.file_uploader("Subir arquivos (ILIMITADO):", type=['txt', 'py', 'js', 'html', 'css'], accept_multiple_files=True)
    else:
        arquivos = st.file_uploader("Subir arquivos (Limite: 10):", type=['txt', 'py'], accept_multiple_files=True)
        if arquivos and len(arquivos) > 10:
            st.error("Limite Free: Apenas 10 arquivos!")
            arquivos = arquivos[:10] # Corta para os primeiros 10

    texto_dos_arquivos = ""
    if arquivos:
        for arc in arquivos:
            try:
                texto_dos_arquivos += f"\n\n--- Arquivo: {arc.name} ---\n" + arc.read().decode("utf-8")
            except:
                st.warning(f"Não consegui ler o arquivo {arc.name}")
        st.success(f"{len(arquivos)} arquivo(s) carregado(s)!")

    st.write("---")
    if is_pro:
        persona = st.selectbox("Personalidade:", ["Padrão", "Hacker", "Cientista", "Gamer"])
    else:
        st.caption("🔒 Personalidades (Apenas PRO)")

    if st.button("Encerrar Sessão"):
        st.session_state.logado = False
        st.rerun()

    if not is_pro:
        st.write("---")
        st.write("💎 **Zynth Pro (R$ 20,00)**")
        if st.button("💳 VER PIX"):
            st.warning("PIX:12981613285 ")
            st.info("📩 Mande o print no Instagram: @lorenzomigueldossantos1")
            
            st.caption("🚀 As liberações são feitas todos os dias às 10h e às 20h. Aguarde o seu acesso!")


# --- 7. INTERFACE DE CHAT ---
st.title("Zynth OS")

for msg in st.session_state.historico:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "img" in msg: st.image(msg["img"])

prompt = st.chat_input("Insira o comando...")

if prompt:
    st.session_state.historico.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.write(prompt)

    with st.chat_message("assistant"):
        if any(p in prompt.lower() for p in ["imagem", "foto", "gerar"]):
            qualidade = "8k, cinematic" if is_pro else ""
            url = f"https://pollinations.ai/p/{urllib.parse.quote(prompt + ' ' + qualidade)}?width=1024&height=1024&nologo=true"
            st.image(url)
            msg_final = {"role": "assistant", "content": f"Imagem gerada: {prompt}", "img": url}
        else:
            try:
                # Memória: 20 para Free, Tudo para Pro
                contexto = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.historico[:-1]]
                
                if not is_pro:
                    contexto = contexto[-20:] 
                    instrucao = "Você é a Zynth IA. Responda de forma direta."
                else:
                    instrucao = f"Você é a Zynth IA Pro ({persona}). Seja extremamente detalhista."

                chat = modelo_zynth.start_chat(history=contexto)
                # Envia o prompt + o texto de todos os arquivos juntos!
                response = chat.send_message(f"{instrucao}\n\n{texto_dos_arquivos}\n\nPergunta do usuário: {prompt}")
                
                st.write(response.text)
                msg_final = {"role": "assistant", "content": response.text}
            except Exception as e:
                st.error(f"Erro: {e}")
                msg_final = {"role": "assistant", "content": "Erro no núcleo."}
    
    st.session_state.historico.append(msg_final)