import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Dashboard_SGL",
    layout="wide",
    page_icon="🔬"
)

# --- PALETA DE CORES PERSONALIZADA ---
CORES_LAB = ['#004a88', '#28a745', '#ffc107', '#007bff', '#6c757d']

# --- ADICIONAR LOGO NA BARRA LATERAL ---
URL_LOGO = "https://raw.githubusercontent.com/vicentin-alex/dashboard-cpao/main/Lablogo.png"

with st.sidebar:
    try:
        st.image(URL_LOGO, use_container_width=True)
    except:
        st.markdown("### 🔬 **CPAO Lab**") 
    st.markdown("---")

# 2. CONFIGURAÇÃO DO GOOGLE SHEETS
SHEET_ID = "1PchyFqFOQ8A80xiBAkUZbqfyKbTzrQZwBuhJllMCVSk"
SHEET_NAME = "REGISTRO"
encoded_sheet_name = urllib.parse.quote(SHEET_NAME)
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}"

# 3. TÍTULO ÚNICO NA PÁGINA
st.title("🔬 Laboratório de Análises Físico-Químicas_CPAO")
st.caption("Filtros independentes: Deixe vazio para selecionar tudo.")
st.markdown("---")

@st.cache_data(ttl=30)
def load_data():
    try:
        df = pd.read_csv(URL, encoding='utf-8')
        df = df.dropna(axis=1, how='all')
        if 'Data' in df.columns:
            df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Erro ao carregar a planilha: {e}")
        return pd.DataFrame()

df_original = load_data()

if not df_original.empty:
    df = df_original.copy()

    with st.sidebar:
        st.header("Painel de Filtros")
        
        # --- FILTRO UNIFICADO DE TÉCNICOS (1 ao 6) ---
        # Definimos as colunas exatas que existem na sua planilha
        colunas_tecnicos = ["Técnico 1", "Técnico 2", "Técnico 3", "Técnico 4", "Técnico 5", "Técnico 6"]
        
        # Extraímos todos os nomes únicos que aparecem nessas 6 colunas
        existentes = [col for col in colunas_tecnicos if col in df.columns]
        if existentes:
            lista_todos_tecnicos = pd.unique(df[existentes].values.ravel('K'))
            lista_todos_tecnicos = sorted([x for x in lista_todos_tecnicos if str(x) != 'nan' and str(x) != 'None'])
            
            selecao_tecnicos = st.multiselect("Filtrar por Técnico (1 a 6):", options=lista_todos_tecnicos)
        else:
            selecao_tecnicos = []

        # --- DEMAIS FILTROS ---
        colunas_para_filtrar = ["Status_Amostra", "Matriz", "Demandante", "Projeto", "Boletim"]
        
        escolhas_usuario = {}
        for col in colunas_para_filtrar:
            if col in df.columns:
                opcoes = sorted(df[col].dropna().unique().tolist())
                selecao = st.multiselect(f"Filtrar {col}:", options=opcoes)
                escolhas_usuario[col] = selecao

    # --- APLICAÇÃO DA LÓGICA DE FILTRAGEM ---
    
    # Filtro de Técnicos: Se o nome estiver em QUALQUER uma das colunas de técnico
    if selecao_tecnicos and existentes:
        mascara_tecnico = df[existentes].isin(selecao_tecnicos).any(axis=1)
        df = df[mascara_tecnico]

    # Outros Filtros
    for col, selecao in escolhas_usuario.items():
        if selecao:
            df = df[df[col].isin(selecao)]

    # --- MÉTRICAS PERSONALIZADAS ---
    st.markdown("---")
    m0, m1, m2, m3, m4 = st.columns(5)
    
    if "Qtdade" in df.columns:
        total_volume = int(df['Qtdade'].sum())
        m0.metric("QUANTIDADE REGISTRADA", f"{total_volume:,}".replace(',', '.'))

    if "Status_Amostra" in df.columns:
        m1.metric("BOLETIM PRONTO", len(df[df["Status_Amostra"] == "PRONTAS"]))
        m2.metric("BOLETIM EM ANÁLISE", len(df[df["Status_Amostra"] == "EM ANÁLISE"]))
        m3.metric("BOLETIM NA FILA", len(df[df["Status_Amostra"] == "NA FILA"]))
        m4.metric("REGISTRADO VIRTUALMENTE", len(df[df["Status_Amostra"] == "NÃO ENTREGUE"]))

    st.markdown("---")

    # --- GRÁFICOS ---
    if not df.empty:
        c1, c2 = st.columns(2)
        
        with c1:
            if "Status_Amostra" in df.columns:
                fig1 = px.pie(
                    df, 
                    names="Status_Amostra", 
                    title="Distribuição por Status", 
                    hole=0.4,
                    color_discrete_sequence=CORES_LAB
                )
                st.plotly_chart(fig1, use_container_width=True)
        
        with c2:
            if "Demandante" in df.columns and "Qtdade" in df.columns:
                fig2 = px.bar(
                    df, 
                    x="Demandante", 
                    y="Qtdade", 
                    color="Matriz" if "Matriz" in df.columns else None, 
                    title="Volume por Demandante",
                    color_discrete_sequence=CORES_LAB
                )
                st.plotly_chart(fig2, use_container_width=True)

        st.subheader("📋 Detalhamento das Amostras")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")







