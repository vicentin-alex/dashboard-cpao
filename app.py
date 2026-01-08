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

# --- LOGO NA BARRA LATERAL ---
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
st.caption("Controle de Visualização de Colunas Ativado")
st.markdown("---")

@st.cache_data(ttl=30)
def load_data():
    try:
        df = pd.read_csv(URL, encoding='utf-8')
        # Limpeza de linhas totalmente vazias do final da planilha
        colunas_chave = ["Boletim", "Status_Amostra"]
        existentes = [c for c in colunas_chave if c in df.columns]
        if existentes:
            df = df.dropna(subset=existentes, how='all')
        
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
        st.header("⚙️ Painel de Filtros")
        
        # --- FILTRO UNIFICADO DE TÉCNICOS ---
        col_tecnicos = ["Técnico 1", "Técnico 2", "Técnico 3", "Técnico 4", "Técnico 5", "Técnico 6"]
        col_presentes = [c for c in col_tecnicos if c in df.columns]
        
        if col_presentes:
            nomes_unicos = pd.unique(df[col_presentes].values.ravel('K'))
            opcoes_tecnicos = sorted([str(x) for x in nomes_unicos if pd.notna(x) and str(x).strip() != ''])
            selecao_tecnicos = st.multiselect("Filtrar por Técnico:", options=opcoes_tecnicos)
        else:
            selecao_tecnicos = []

        # --- OUTROS FILTROS ---
        colunas_filtros_extras = ["Status_Amostra", "Matriz", "Demandante", "Projeto", "Boletim"]
        escolhas_usuario = {}
        for col in colunas_filtros_extras:
            if col in df.columns:
                opcoes = sorted(df[col].dropna().unique().tolist())
                escolhas_usuario[col] = st.multiselect(f"Filtrar {col}:", options=opcoes)

        # --- NOVO: SELEÇÃO PERSISTENTE DE COLUNAS ---
        st.markdown("---")
        st.subheader("🖥️ Ajuste de Exibição")
        todas_colunas = df.columns.tolist()
        
        # Definimos o que aparece por padrão ao abrir
        colunas_default = ["Boletim", "Preparo", "Status_Amostra", "Técnico 1", "Prazo 1", "Link do Boletim"]
        colunas_default = [c for c in colunas_default if c in todas_colunas]
        
        colunas_visiveis = st.multiselect(
            "Colunas visíveis na tabela:",
            options=todas_colunas,
            default=colunas_default
        )

    # --- LÓGICA DE FILTRAGEM ---
    if selecao_tecnicos and col_presentes:
        df = df[df[col_presentes].isin(selecao_tecnicos).any(axis=1)]

    for col, selecao in escolhas_usuario.items():
        if selecao:
            df = df[df[col].isin(selecao)]

    # --- MÉTRICAS ---
    st.markdown("---")
    m0, m1, m2, m3, m4 = st.columns(5)
    if "Qtdade" in df.columns:
        total = int(df['Qtdade'].sum())
        m0.metric("QUANTIDADE TOTAL", f"{total:,}".replace(',', '.'))

    if "Status_Amostra" in df.columns:
        status_valido = df[df["Status_Amostra"].notna()]
        m1.metric("PRONTAS", len(status_valido[status_valido["Status_Amostra"] == "PRONTAS"]))
        m2.metric("EM ANÁLISE", len(status_valido[status_valido["Status_Amostra"] == "EM ANÁLISE"]))
        m3.metric("NA FILA", len(status_valido[status_valido["Status_Amostra"] == "NA FILA"]))
        m4.metric("NÃO ENTREGUE", len(status_valido[status_valido["Status_Amostra"] == "NÃO ENTREGUE"]))

    st.markdown("---")

    # --- GRÁFICOS ---
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            if "Status_Amostra" in df.columns:
                df_pizza = df.dropna(subset=["Status_Amostra"])
                fig1 = px.pie(df_pizza, names="Status_Amostra", title="Distribuição por Status", hole=0.4, color_discrete_sequence=CORES_LAB)
                st.plotly_chart(fig1, use_container_width=True)
        with c2:
            if "Demandante" in df.columns and "Qtdade" in df.columns:
                fig2 = px.bar(df, x="Demandante", y="Qtdade", color="Matriz" if "Matriz" in df.columns else None, title="Volume por Demandante", color_discrete_sequence=CORES_LAB)
                st.plotly_chart(fig2, use_container_width=True)

        # --- TABELA DE DETALHAMENTO ---
        st.subheader("📋 Detalhamento das Amostras")
        
        config_colunas = {}
        if "Link do Boletim" in df.columns:
            config_colunas["Link do Boletim"] = st.column_config.LinkColumn(
                "Link do Boletim",
                display_text="Abrir Boletim 📄",
                help="Clique para abrir o link oficial do boletim"
            )

        # Exibe apenas as colunas selecionadas no multiselect da sidebar
        if colunas_visiveis:
            st.dataframe(
                df[colunas_visiveis], 
                use_container_width=True, 
                hide_index=True,
                column_config=config_colunas
            )
        else:
            st.warning("Selecione pelo menos uma coluna no painel lateral para visualizar os detalhes.")
        
    else:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")


