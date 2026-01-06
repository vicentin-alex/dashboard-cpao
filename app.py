
import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse


# --- CONFIGURAÇÃO DO GOOGLE SHEETS ---
SHEET_ID = "1PchyFqFOQ8A80xiBAkUZbqfyKbTzrQZwBuhJllMCVSk"
SHEET_NAME = "REGISTRO"


encoded_sheet_name = urllib.parse.quote(SHEET_NAME)
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}"


import streamlit as st
# ... (restante do seu código anterior)


st.set_page_config(
        page_title="Dashboard_SGL",
        layout="wide"
)
st.title("🔬 Laboratório de Análises Físico-Químicas_CPAO")




@st.cache_data(ttl=30)
def load_data():
        df = pd.read_csv(URL, encoding='utf-8')
        df = df.dropna(axis=1, how='all')
        if 'Data' in df.columns:
            df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        return df


try:
        df_original = load_data()
        df = df_original.copy()
    
        st.title("🔬 Laboratório de Análises Físico-Químicas_CPAO")
        st.caption("Filtros independentes: Deixe vazio para selecionar tudo.")
        st.markdown("---")


        # --- BARRA LATERAL COM FILTROS INDEPENDENTES ---
        with st.sidebar:
            st.header("Painel de Filtros")
            
            colunas_para_filtrar = [
                "Status_Amostra", "Matriz", "Demandante",
                "Projeto", "Registrado por:", "Amostra entregue por:"
            ]
            
            # Dicionário para armazenar as escolhas do usuário
            escolhas_usuario = {}


            for col in colunas_para_filtrar:
                if col in df.columns:
                    opcoes = sorted(df[col].dropna().unique().tolist())
                    # Iniciamos o multiselect VAZIO por padrão
                    selecao = st.multiselect(f"Filtrar {col}:", options=opcoes, help=f"Selecione itens de {col}. Se deixar vazio, todos serão considerados.")
                    escolhas_usuario[col] = selecao


        # --- LÓGICA DE FILTRAGEM INDEPENDENTE ---
        # Só filtramos a coluna se o usuário tiver selecionado pelo menos um item nela
        for col, selecao in escolhas_usuario.items():
            if selecao: # Se a lista não estiver vazia
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
                    # Mostra o Top 10 Demandantes para não poluir o gráfico
                    fig2 = px.bar(df, x="Demandante", y="Qtdade", color="Matriz", title="Volume por Demandante e Matriz")
                    st.plotly_chart(fig2, use_container_width=True)


            # --- TABELA DE DADOS ---
            st.subheader("📋 Detalhamento das Amostras")
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("Nenhum dado encontrado para a combinação de filtros selecionada.")


except Exception as e:
        st.error(f"Erro: {e}")


