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
        # CORREÇÃO: Removido o dropna(axis=1) para não sumir com colunas de prazos vazias
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
        
        # --- FILTRO UNIFICADO DE TÉCNICOS ---
        colunas_tecnicos = ["Técnico 1", "Técnico 2", "Técnico 3", "Técnico 4", "Técnico 5", "Técnico 6"]
        
        # Identifica quais colunas de técnico realmente existem na planilha
        colunas_existentes = [c for c in colunas_tecnicos if c in df.columns]
        
        if colunas_existentes:
            lista_todos_tecnicos = pd.unique(df[colunas_existentes].values.ravel('K'))
            lista_todos_tecnicos = sorted([x for x in lista_todos_tecnicos if str(x) != 'nan' and str(x) != 'None'])
            selecao_tecnicos = st.multiselect("Filtrar por Técnico:", options=lista_todos_tecnicos)
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
    if selecao_tecnicos and colunas_existentes:
        mascara_tecnico = df[colunas_existentes].isin(selecao_tecnicos).any(axis=1)
        df = df[mascara_tecnico]

    for col, selecao in escolhas_usuario.items():
        if selecao:
            df = df[df[col].isin(selecao)]

    # --- MÉTRICAS ---
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
                fig1 = px.pie(df, names="Status_Amostra", title="Distribuição por Status", hole=0.4, color_discrete_sequence=CORES_LAB)
                st.plotly_chart(fig1, use_container_width=True)
        with c2:
            if "Demandante" in df.columns and "Qtdade" in df.columns:
                fig2 = px.bar(df, x="Demandante", y="Qtdade", color="Matriz" if "Matriz" in df.columns else None, title="Volume por Demandante", color_discrete_sequence=CORES_LAB)
                st.plotly_chart(fig2, use_container_width=True)

        # --- TABELA DE DETALHAMENTO (CORRIGIDA) ---
        st.subheader("📋 Detalhamento das Amostras")
        
        # Lista de colunas desejadas para garantir que apareçam na ordem certa
        # Incluímos as colunas de Prazos aqui
        ordem_colunas = [
            "Boletim", "Status_Amostra", "Qtdade", "Matriz", 
            "Técnico 1", "Prazo 1", 
            "Técnico 2", "Prazo 2", 
            "Técnico 3", "Prazo 3", 
            "Técnico 4", "Prazo 4", 
            "Técnico 5", "Prazo 5", 
            "Técnico 6", "Prazo 6"
        ]
        
        # Filtra apenas as que existem no DF para evitar erros de visualização
        colunas_finais = [c for c in ordem_colunas if c in df.columns]
        
        # Exibe o dataframe final
        st.dataframe(df[colunas_finais], use_container_width=True, hide_index=True)
    else:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")






