import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import gspread
from google.oauth2.service_account import Credentials
import datetime
import base64 # <-- NOVA IMPORTAÇÃO PARA A MARCA D'ÁGUA INFALÍVEL

# ================= BLOCO 1: MARCA D'ÁGUA SVG INFALÍVEL =================
def inject_watermark(nome_paciente, id_sessao):
    paciente_display = nome_paciente if nome_paciente else "PACIENTE NÃO IDENTIFICADO"
    token_display = id_sessao if id_sessao else "TOKEN"
    
    # Criando um SVG dinâmico com o texto
    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="400" height="400">
        <g transform="translate(200,200) rotate(-35)">
            <text text-anchor="middle" fill="rgba(150, 150, 150, 0.25)" font-size="20" font-family="Arial, sans-serif" font-weight="bold">
                <tspan x="0" dy="-30">INSTRUMENTO SIGILOSO</tspan>
                <tspan x="0" dy="30">{paciente_display}</tspan>
                <tspan x="0" dy="30">{token_display}</tspan>
            </text>
        </g>
    </svg>
    """
    
    # Convertendo o SVG para Base64 para não depender de arquivos externos
    b64_svg = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
    
    # Injetando como uma camada pseudo-element (.stApp::before) que fica por cima de TUDO
    watermark_style = f"""
    <style>
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background-image: url("data:image/svg+xml;base64,{b64_svg}");
        background-repeat: repeat;
        background-position: center;
        pointer-events: none;
        z-index: 999999 !important;
    }}
    </style>
    """
    st.markdown(watermark_style, unsafe_allow_html=True)

# ================= CONFIGURAÇÕES DE E-MAIL =================
SEU_EMAIL = st.secrets["EMAIL_USUARIO"]
SENHA_DO_EMAIL = st.secrets["SENHA_USUARIO"]
EMAIL_DESTINO = "psicologabrunaligoski@gmail.com"
# ===========================================================

# ================= CONEXÃO COM GOOGLE SHEETS =================
@st.cache_resource
def conectar_planilha():
    creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS_JSON"])
    escopos = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(creds_dict, scopes=escopos)
    client = gspread.authorize(creds)
    # CONECTA DIRETAMENTE À PLANILHA CENTRAL DE TOKENS
    return client.open("Controle_Tokens").sheet1 

try:
    planilha = conectar_planilha()
except Exception as e:
    st.error(f"Erro de conexão com a planilha de controle: {e}")
    st.stop()
# =============================================================

def enviar_email_resultados(dados_avaliado, dados_respondente, resultados_brutos, token):
    assunto = f"Resultados SRS-2 (Adulto Heterorrelato) - Paciente: {dados_avaliado['nome']}"
    
    corpo = f"Avaliação SRS-2 (Adulto Heterorrelato) concluída.\n\n"
    corpo += f"=== DADOS DO(A) PACIENTE ===\n"
    corpo += f"Nome: {dados_avaliado['nome']}\n"
    corpo += f"Data de Nascimento: {dados_avaliado['data_nasc']}\n"
    corpo += f"Token de Validação: {token}\n\n"
    
    corpo += f"=== DADOS DO(A) RESPONDENTE ===\n"
    corpo += f"Nome: {dados_respondente['nome']}\n"
    corpo += f"Vínculo de Parentesco: {dados_respondente['vinculo']}\n\n"
    
    corpo += "================ GABARITO DE RESPOSTAS ================\n"
    corpo += "Formato: [Número da Questão] - [Valor da Resposta]\n\n"
    
    for num_q, valor in resultados_brutos.items():
        corpo += f"{num_q} - {valor}\n"

    msg = MIMEMultipart()
    msg['From'] = SEU_EMAIL
    msg['To'] = EMAIL_DESTINO
    msg['Subject'] = assunto
    msg.attach(MIMEText(corpo, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SEU_EMAIL, SENHA_DO_EMAIL)
        server.send_message(msg)
        server.quit()
        return True
    except:
        return False

# ================= PERGUNTAS DO TESTE (COM AJUSTE DE GÊNERO) =================
perguntas = [
    "Parece muito mais desconfortável em situações sociais do que quando está sozinho(a).",
    "As expressões em seu rosto não combinam com o que está dizendo.",
    "Parece confiante (ou seguro/a) quando está interagindo com outras pessoas.",
    "Quando há sobrecarga de estímulos, apresenta padrões rígidos e inflexíveis de comportamento, aparentemente estranhos.",
    "Não percebe quando os outros estão tentando tirar vantagem dele(a).",
    "Prefere estar sozinho(a) do que com os outros.",
    "Demonstra perceber o que os outros estão pensando ou sentindo.",
    "Se comporta de maneira estranha ou bizarra.",
    "Precisa da ajuda de outras pessoas para satisfazer suas necessidades básicas.",
    "Leva as coisas muito \"ao pé da letra\" e não compreende o real significado de uma conversa.",
    "É autoconfiante.",
    "É capaz de comunicar seus sentimentos para as outras pessoas.",
    "É estranho(a) na \"tomada de vez\" das interações com seus colegas (por exemplo, não parece entender a reciprocidade de uma conversa).",
    "Não tem boa coordenação.",
    "Reconhece e responde de forma apropriada às mudanças no tom de voz e expressões faciais de outras pessoas.",
    "Evita o contato visual ou tem contato visual diferente.",
    "Reconhece quando algo é inesperado ou injusto.",
    "Tem dificuldade em fazer amigos, mesmo tentando dar o melhor de si.",
    "Fica frustrado(a) tentando expressar suas ideias em uma conversa.",
    "Mostra interesses sensoriais incomuns ou estranhos (por exemplo, cheirar os dedos com frequência) ou chacoalha repetidamente pequenos itens.",
    "É capaz de imitar ações e comportamento de outras pessoas quando é socialmente apropriado fazê-lo.",
    "Interage apropriadamente com outros adultos.",
    "Não participa de atividades em grupo e eventos sociais a menos que seja convidado(a) a fazê-lo.",
    "Tem mais dificuldade do que outras pessoas com mudanças em sua rotina.",
    "Não parece se importar em estar fora de sintonia ou em um \"mundo\" diferente dos outros.",
    "Oferece conforto para os outros quando estão tristes.",
    "Evita iniciar interações sociais com outros adultos.",
    "Pensa ou fala sobre a mesma coisa repetidamente.",
    "É considerado(a) estranho(a) ou esquisito(a) pelas outras pessoas.",
    "Fica perturbado(a) em uma situação com muitas coisas acontecendo.",
    "Não consegue tirar algo da sua mente uma vez que começa a pensar sobre isso.",
    "Tem boa higiene pessoal.",
    "É socialmente desajeitado(a), mesmo quando tenta ser educado(a).",
    "Evita pessoas que querem se aproximar dele(a) por meio de contato afetivo.",
    "Tem dificuldade em acompanhar o fluxo de uma conversa normal.",
    "Tem dificuldade em se relacionar com os membros da família.",
    "Tem dificuldade em se relacionar com adultos.",
    "Responde adequadamente às mudanças de humor das outras pessoas (por exemplo, quando o humor de um amigo muda de feliz para triste).",
    "Tem uma variedade de interesses extraordinariamente incomuns.",
    "É imaginativo(a) sem perder contato com a realidade.",
    "Muda de uma atividade para outra sem objetivo aparente.",
    "Parece excessivamente sensível aos sons, texturas ou cheiros.",
    "Gosta de se mostrar \"bom(boa) de conversa\" (conversa informal com os outros).",
    "Não entende como os acontecimentos estão relacionados entre si (causa e efeito), da mesma forma que outros adultos.",
    "Geralmente fica interessado(a) no que as pessoas próximas estão prestando atenção.",
    "Tem expressão facial excessivamente séria.",
    "Ri em momentos inapropriados.",
    "Tem senso de humor e entende as piadas.",
    "É extremamente hábil em tarefas intelectuais ou computacionais, mas não consegue fazer tão bem a maioria das outras tarefas.",
    "Tem comportamentos estranhos e repetitivos.",
    "Tem dificuldade em responder perguntas diretamente e acaba falando em torno do assunto.",
    "Sabe quando está falando muito alto ou fazendo muito barulho.",
    "Fala com as pessoas com um tom de voz incomum (por exemplo, fala como um robô ou como se estivesse dando uma palestra).",
    "Parece agir com as pessoas como se elas fossem objetos.",
    "Sabe quando está muito próximo(a) ou invadindo o espaço de alguém.",
    "Caminha entre duas pessoas que estão conversando.",
    "Isolado(a); tende a não deixar sua casa.",
    "Concentra-se demais em partes das coisas ao invés de ver o todo.",
    "É excessivamente desconfiado(a).",
    "É emocionalmente distante, não demonstrando seus sentimentos.",
    "É inflexível e tem dificuldade para mudar de ideia.",
    "Dá explicações incomuns ou ilógicas do porquê de fazer as coisas.",
    "Toca ou cumprimenta os outros de uma maneira incomum.",
    "Fica muito agitado(a) em situações sociais.",
    "Fica com olhar perdido ou olha fixamente para o nada."
]

opcoes_respostas = {
    "1 = Não é verdade": 1,
    "2 = Algumas vezes é verdade": 2,
    "3 = Muitas vezes é verdade": 3,
    "4 = Quase sempre é verdade": 4
}

st.set_page_config(page_title="SRS-2 Adulto Heterorrelato", layout="centered")

# CSS para Botão Azul Forçado
st.markdown("""
    <style>
    div[data-testid="stFormSubmitButton"] > button {
        background-color: #0047AB !important;
        color: white !important;
        border: none !important;
        padding: 0.6rem 2.5rem !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        font-size: 16px !important;
    }
    div[data-testid="stFormSubmitButton"] > button:hover {
        background-color: #003380 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

if "avaliacao_concluida" not in st.session_state:
    st.session_state.avaliacao_concluida = False

# Título Centralizado
st.markdown("<h1 style='text-align: center;'>Clínica de Psicologia e Psicanálise Bruna Ligoski</h1>", unsafe_allow_html=True)

if st.session_state.avaliacao_concluida:
    st.success("Avaliação concluída e enviada com sucesso! Muito obrigado(a) pela sua colaboração.")
    st.stop()

# ================= VALIDAÇÃO SILENCIOSA DO TOKEN E SMART LINK =================
parametros = st.query_params
token_url = parametros.get("token", None)
nome_na_url = parametros.get("nome", "") # Captura do link inteligente

if not token_url:
    st.warning("⚠️ Link de acesso inválido ou incompleto. Solicite um novo link à profissional.")
    st.stop()

try:
    registros = planilha.get_all_records()
    dados_token = None
    linha_alvo = 2 
    for i, reg in enumerate(registros):
        if str(reg.get("Token")) == token_url:
            dados_token = reg
            linha_alvo += i
            break
            
    if not dados_token or dados_token.get("Status") != "Aberto":
        st.error("⚠️ Este link é inválido ou já foi utilizado.")
        st.stop()
except Exception:
    st.error("Erro técnico na validação do link.")
    st.stop()

# ================= INTERFACE DO TESTE =================
linha_fina = "<hr style='margin-top: 8px; margin-bottom: 8px;'/>"
st.markdown(linha_fina, unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>Escala de Responsividade Social (SRS-2) - Adulto Heterorrelato</h3>", unsafe_allow_html=True)
st.markdown(linha_fina, unsafe_allow_html=True)

st.info("**Instrução:** Em cada questão, por favor escolha a alternativa que melhor descreva o comportamento do(a) paciente nos últimos 6 meses.")

# --- IDENTIFICAÇÃO (FORA DO FORM PARA MARCA D'ÁGUA DINÂMICA) ---
st.subheader("Dados do(a) Paciente (Avaliado/a)")
nome_avaliado = st.text_input("Nome completo do(a) paciente *", value=nome_na_url)
data_nasc_avaliado = st.date_input("Data de nascimento do(a) paciente *", format="DD/MM/YYYY", min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today(), value=None)
    
st.divider()
st.subheader("Dados do(a) Respondente")
nome_respondente = st.text_input("Nome completo do(a) respondente *")
vinculo_respondente = st.text_input("Vínculo / Parentesco (Ex: Pai, Mãe, Cônjuge) *")

# CHAMADA DA NOVA FUNÇÃO DA MARCA D'ÁGUA
inject_watermark(nome_avaliado, token_url)

st.divider()

with st.form("form_srs2_heterorrelato"):
    respostas_coletadas = {}
    for index, texto_pergunta in enumerate(perguntas):
        num_q = index + 1
        st.write(f"**{num_q}. {texto_pergunta}**")
        resposta = st.radio(f"Oculto {num_q}", list(opcoes_respostas.keys()), index=None, label_visibility="collapsed")
        respostas_coletadas[num_q] = opcoes_respostas[resposta] if resposta else None
        st.divider()

    if st.form_submit_button("Enviar Avaliação"):
        questoes_em_branco = [q for q, r in respostas_coletadas.items() if r is None]

        if not nome_avaliado or not nome_respondente or not vinculo_respondente or data_nasc_avaliado is None:
            st.error("Por favor, preencha todos os dados de identificação obrigatórios.")
        elif questoes_em_branco:
            st.error(f"Por favor, responda todas as perguntas. Faltam {len(questoes_em_branco)} questão(ões).")
        else:
            dados_final_paciente = {
                "nome": nome_avaliado,
                "data_nasc": data_nasc_avaliado.strftime("%d/%m/%Y")
            }
            dados_final_respondente = {
                "nome": nome_respondente,
                "vinculo": vinculo_respondente
            }

            with st.spinner('Enviando avaliação...'):
                if enviar_email_resultados(dados_final_paciente, dados_final_respondente, respostas_coletadas, token_url):
                    try:
                        planilha.update_cell(linha_alvo, 5, "Respondido")
                        st.session_state.avaliacao_concluida = True
                        st.rerun()
                    except:
                        st.session_state.avaliacao_concluida = True
                        st.rerun()
                else:
                    st.error("Houve um erro no envio. Tente novamente.")
