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
# Ordem: Azul Forte, Verde Saúde, Amarelo Alerta, Azul Claro, Cinza
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
        colunas_para_filtrar = [
            "Status_Amostra", "Matriz", "Demandante",
            "Projeto", "Boletim", "Técnico Responsável"
        ]
        
        escolhas_usuario = {}
        for col in colunas_para_filtrar:
            if col in df.columns:
                opcoes = sorted(df[col].dropna().unique().tolist())
                selecao = st.multiselect(f"Filtrar {col}:", options=opcoes)
                escolhas_usuario[col] = selecao

    for col, selecao in escolhas_usuario.items():
        if selecao:
            df = df[df[col].isin(selecao)]

   # --- MÉTRICAS PERSONALIZADAS COM TOTAL DE QTDADE ---
    st.markdown("---")
    # Criando 5 colunas para acomodar todas as métricas no topo
    m0, m1, m2, m3, m4 = st.columns(5)
    
    # 0. Quantidade Total (Soma da coluna Qtdade)
    if "Qtdade" in df.columns:
        total_volume = int(df['Qtdade'].sum())
        m0.metric("QUANTIDADE REGISTRADA", f"{total_volume:,}".replace(',', '.'))

    if "Status_Amostra" in df.columns:
        # 1. Amostras Prontas
        prontas = len(df[df["Status_Amostra"] == "PRONTAS"])
        m1.metric("BOLETIM PRONTO", prontas)
        
        # 2. Amostras em Análise
        em_analise = len(df[df["Status_Amostra"] == "EM ANÁLISE"])
        m2.metric("BOLETIM EM ANÁLISE", em_analise)
        
        # 3. Amostras na Fila
        na_fila = len(df[df["Status_Amostra"] == "NA FILA"])
        m3.metric("BOLETIM NA FILA", na_fila)
        
        # 4. Amostras Não Entregues
        nao_entregue = len(df[df["Status_Amostra"] == "NÃO ENTREGUE"])
        m4.metric("BOLETIM REGISTRADO VIRTUALMENTE", nao_entregue)

    st.markdown("---")

    # --- GRÁFICOS COM CORES PERSONALIZADAS ---
    if not df.empty:
        c1, c2 = st.columns(2)
        
        with c1:
            if "Status_Amostra" in df.columns:
                # Adicionado color_discrete_sequence
                fig1 = px.pie(
                    df, 
                    names="Status_Amostra", 
                    title="Distribuição por Status", 
                    hole=0.4,
                    color_discrete_sequence=CORES_LAB
                )
                st.plotly_chart(fig1, use_container_width=True)
        
        with c2:
            if "Demandante" in df.columns:
                # Adicionado color_discrete_sequence
                fig2 = px.bar(
                    df, 
                    x="Demandante", 
                    y="Qtdade", 
                    color="Matriz", 
                    title="Volume por Demandante e Matriz",
                    color_discrete_sequence=CORES_LAB
                )
                st.plotly_chart(fig2, use_container_width=True)

        st.subheader("📋 Detalhamento das Amostras")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("Nenhum dado encontrado para a combinação de filtros selecionada.")









