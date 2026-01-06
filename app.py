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
# --- ADICIONAR LOGO NA BARRA LATERAL ---
URL_LOGO = "https://raw.githubusercontent.com/vicentin-alex/dashboard-cpao/main/Lablogo.png"

with st.sidebar:
    # Centraliza a logo e trata erro caso o link mude
    try:
        st.image(URL_LOGO, use_container_width=True)
    except:
        st.markdown("### 🔬 CPAO Lab") 
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

# Funçao para carregar dados
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

# Execução do Dashboard
df_original = load_data()

if not df_original.empty:
    df = df_original.copy()

    # --- BARRA LATERAL COM FILTROS ---
    with st.sidebar:
        st.header("Painel de Filtros")
        colunas_para_filtrar = [
            "Status_Amostra", "Matriz", "Demandante",
            "Projeto", "Registrado por:", "Amostra entregue por:"
        ]
        
        escolhas_usuario = {}
        for col in colunas_para_filtrar:
            if col in df.columns:
                opcoes = sorted(df[col].dropna().unique().tolist())
                selecao = st.multiselect(f"Filtrar {col}:", options=opcoes)
                escolhas_usuario[col] = selecao

    # Lógica de Filtragem
    for col, selecao in escolhas_usuario.items():
        if selecao:
            df = df[df[col].isin(selecao)]

    # --- MÉTRICAS ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Amostras Exibidas", len(df))
    
    if "Qtdade" in df.columns:
        m2.metric("Qtd Total", f"{int(df['Qtdade'].sum()):,}".replace(',', '.'))
    
    if "Química" in df.columns:
        m3.metric("Ensaios Química", df["Química"].notna().sum())
        
    if "Física" in df.columns:
        m4.metric("Ensaios Física", df["Física"].notna().sum())

    st.markdown("---")

    # --- GRÁFICOS ---
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            if "Status_Amostra" in df.columns:
                fig1 = px.pie(df, names="Status_Amostra", title="Distribuição por Status", hole=0.4)
                st.plotly_chart(fig1, use_container_width=True)
        
        with c2:
            if "Demandante" in df.columns:
                fig2 = px.bar(df, x="Demandante", y="Qtdade", color="Matriz", title="Volume por Demandante e Matriz")
                st.plotly_chart(fig2, use_container_width=True)

        st.subheader("📋 Detalhamento das Amostras")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("Nenhum dado encontrado para a combinação de filtros selecionada.")





