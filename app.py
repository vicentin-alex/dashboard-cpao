import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Dashboard_SGL_CPAO",
    layout="wide",
    page_icon="🔬"
)

# --- PALETA DE CORES PERSONALIZADA ---
CORES_LAB = ['#004a88', '#28a745', '#ffc107', '#d93025', '#6c757d']

# --- LOGO NA BARRA LATERAL ---
URL_LOGO = "https://raw.githubusercontent.com/vicentin-alex/dashboard-cpao/main/Lablogo.png"

with st.sidebar:
    try:
        st.image(URL_LOGO, use_container_width=True)
    except:
        st.markdown("### 🔬 **CPAO Lab**") 
    st.markdown("---")
    
    # --- ACESSO RESTRITO AO EDITOR ---
    senha_acesso = st.text_input("Acesso Interno", type="password", help="Digite a senha para habilitar ajustes de exibição.")
    e_editor = (senha_acesso == "Acetona25@!")

# 2. CONFIGURAÇÃO DO GOOGLE SHEETS
SHEET_ID = "1PchyFqFOQ8A80xiBAkUZbqfyKbTzrQZwBuhJllMCVSk"
SHEET_NAME = "REGISTRO"
encoded_sheet_name = urllib.parse.quote(SHEET_NAME)
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}"

# 3. TÍTULO ÚNICO NA PÁGINA
st.title("🔬 Laboratório de Análises Físico-Químicas_CPAO")
st.caption("Sistema de Gestão Laboratorial - Visualização Integrada de Prazos e Equipe")
st.markdown("---")

@st.cache_data(ttl=30)
def load_data():
    try:
        df = pd.read_csv(URL, encoding='utf-8')
        if "Boletim" in df.columns:
            df = df.dropna(subset=["Boletim"], how='all')
        
        # Conversão inicial de Datas (Garantindo formato BR)
        if 'Data' in df.columns:
            df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
        
        col_prazos = ["Prazo 1", "Prazo 2", "Prazo 3", "Prazo 4", "Prazo 5", "Prazo 6"]
        for c in col_prazos:
            if c in df.columns:
                df[c] = pd.to_datetime(df[c], dayfirst=True, errors='coerce')
                
        return df
    except Exception as e:
        st.error(f"Erro ao carregar a planilha: {e}")
        return pd.DataFrame()

df_original = load_data()

if not df_original.empty:
    df = df_original.copy()

    with st.sidebar:
        st.header("⚙️ Painel de Filtros")
        
        col_tecnicos_nomes = ["Técnico 1", "Técnico 2", "Técnico 3", "Técnico 4", "Técnico 5", "Técnico 6"]
        col_presentes = [c for c in col_tecnicos_nomes if c in df.columns]
        
        if col_presentes:
            nomes_unicos = pd.unique(df[col_presentes].values.ravel('K'))
            opcoes_tecnicos = sorted([str(x) for x in nomes_unicos if pd.notna(x) and str(x).strip() != ''])
            selecao_tecnicos = st.multiselect("Filtrar por Técnico:", options=opcoes_tecnicos)
        else:
            selecao_tecnicos = []

        col_filtros_extras = ["Status_Amostra", "Matriz", "Demandante", "Projeto", "Boletim"]
        escolhas_usuario = {}
        for col in col_filtros_extras:
            if col in df.columns:
                opcoes = sorted(df[col].dropna().unique().tolist())
                escolhas_usuario[col] = st.multiselect(f"Filtrar {col}:", options=opcoes)

        todas_colunas = df.columns.tolist()
        colunas_cliente = [
            "Status_Amostra", "Boletim", "Link do Boletim", "Data", 
            "Identificação Lab (Início)", "Identificação Lab (Final)", 
            "Qtdade", "Matriz", "Demandante", "Projeto", "Ordem de Serviço",
            "Técnico 1", "Prazo 1", "Técnico 2", "Prazo 2", "Técnico 3", "Prazo 3", 
            "Técnico 4", "Prazo 4", "Técnico 5", "Prazo 5", "Técnico 6", "Prazo 6"
        ]
        col_existentes = [c for c in colunas_cliente if c in todas_colunas]

        if e_editor:
            st.markdown("---")
            st.success("🔓 Modo Editor Ativo")
            colunas_visiveis = st.multiselect("Escolha as colunas:", options=todas_colunas, default=col_existentes)
        else:
            colunas_visiveis = col_existentes

    # --- APLICAÇÃO DOS FILTROS ---
    if selecao_tecnicos and col_presentes:
        df = df[df[col_presentes].isin(selecao_tecnicos).any(axis=1)]

    for col, selecao in escolhas_usuario.items():
        if selecao:
            df = df[df[col].isin(selecao)]

    # --- MÉTRICAS (CORRIGIDO) ---
    st.markdown("---")
    m0, m1, m2, m3, m4 = st.columns(5)
    
    if "Qtdade" in df.columns:
        total_amostras = int(df['Qtdade'].sum())
        m0.metric("QUANTIDADE TOTAL", f"{total_amostras:,}".replace(',', '.'))

    if "Status_Amostra" in df.columns:
        # Padroniza para maiúsculas para evitar erros de digitação na planilha
        st_upper = df["Status_Amostra"].fillna("").str.upper()
        
        m1.metric("BOLETIM PRONTO", len(df[st_upper == "PRONTAS"]))
        m2.metric("BOLETIM EM ANÁLISE", len(df[st_upper == "EM ANÁLISE"]))
        m3.metric("BOLETIM NA FILA", len(df[st_upper == "NA FILA"]))
        m4.metric("REGISTRO VIRTUAL", len(df[st_upper == "NÃO ENTREGUE"]))

    st.markdown("---")

    # --- GRÁFICO DE LINHA DO TEMPO (GANTT - CORRIGIDO) ---
    st.subheader("⏳ Cronograma de Análises e Prazos")
    prazos_lista = ["Prazo 1", "Prazo 2", "Prazo 3", "Prazo 4", "Prazo 5", "Prazo 6"]
    prazos_atuais = [c for c in prazos_lista if c in df.columns]

    if not df.empty and "Data" in df.columns and prazos_atuais:
        df_gantt = df.copy()
        # Garante que as datas são datetime para evitar TypeError
        df_gantt['Data'] = pd.to_datetime(df_gantt['Data'], errors='coerce')
        for c in prazos_atuais:
            df_gantt[c] = pd.to_datetime(df_gantt[c], errors='coerce')

        # Define o Prazo Final Máximo da linha
        df_gantt['Prazo_Final'] = df_gantt[prazos_atuais].max(axis=1)
        
        # Limpa dados inválidos para o gráfico
        df_gantt = df_gantt.dropna(subset=['Data', 'Prazo_Final'])
        df_gantt['Boletim'] = df_gantt['Boletim'].astype(str)

        if not df_gantt.empty:
            hoje = pd.Timestamp.now().normalize()
            
            def check_timeline_status(row):
                status_raw = str(row['Status_Amostra']).upper()
                if "PRONTAS" in status_raw: return "Concluído"
                if row['Prazo_Final'] < hoje: return "Atrasado 🚨"
                if "EM ANÁLISE" in status_raw: return "Em Análise 🔬"
                return "Na Fila 📥"

            df_gantt['Status_Timeline'] = df_gantt.apply(check_timeline_status, axis=1)

            try:
                fig_gantt = px.timeline(
                    df_gantt, 
                    start="Data", 
                    end="Prazo_Final", 
                    y="Boletim", 
                    color="Status_Timeline",
                    color_discrete_map={
                        "Concluído": "#28a745",
                        "Em Análise 🔬": "#ffc107",
                        "Na Fila 📥": "#004a88",
                        "Atrasado 🚨": "#d93025"
                    },
                    hover_data=["Status_Amostra", "Matriz", "Demandante"],
                    category_orders={"Boletim": df_gantt.sort_values(by="Data")["Boletim"].unique().tolist()}
                )
                fig_gantt.update_yaxes(autorange="reversed")
                fig_gantt.update_layout(xaxis_title="Duração Estimada", yaxis_title="Nº Boletim")
                st.plotly_chart(fig_gantt, use_container_width=True)
            except Exception as e:
                st.error("Erro ao gerar gráfico de Gantt. Verifique o formato das datas na planilha.")

    st.markdown("---")

    # --- GRÁFICOS COMPLEMENTARES ---
    c1, c2 = st.columns(2)
    with c1:
        if "Status_Amostra" in df.columns:
            fig_pizza = px.pie(df.dropna(subset=["Status_Amostra"]), names="Status_Amostra", title="Distribuição por Status", hole=0.4, color_discrete_sequence=CORES_LAB)
            st.plotly_chart(fig_pizza, use_container_width=True)
    with c2:
        if "Demandante" in df.columns and "Qtdade" in df.columns:
            fig_barra = px.bar(df, x="Demandante", y="Qtdade", color="Matriz" if "Matriz" in df.columns else None, title="Volume por Demandante", color_discrete_sequence=CORES_LAB)
            st.plotly_chart(fig_barra, use_container_width=True)

    # --- TABELA DE DETALHAMENTO ---
    st.subheader("📋 Detalhamento das Amostras")
    conf_col = {
        "Link do Boletim": st.column_config.LinkColumn("Boletim", display_text="Abrir 📄"),
        "Data": st.column_config.DateColumn("Registro", format="DD/MM/YYYY"),
        "Prazo 1": st.column_config.DateColumn("Prazo 1", format="DD/MM/YYYY"),
        "Prazo 2": st.column_config.DateColumn("Prazo 2", format="DD/MM/YYYY"),
        "Prazo 3": st.column_config.DateColumn("Prazo 3", format="DD/MM/YYYY"),
        "Prazo 4": st.column_config.DateColumn("Prazo 4", format="DD/MM/YYYY"),
        "Prazo 5": st.column_config.DateColumn("Prazo 5", format="DD/MM/YYYY"),
        "Prazo 6": st.column_config.DateColumn("Prazo 6", format="DD/MM/YYYY")
    }

    if colunas_visiveis:
        st.dataframe(df[colunas_visiveis], use_container_width=True, hide_index=True, column_config=conf_col)
    
else:
    st.warning("Conexão com a planilha falhou ou não há dados com os filtros selecionados.")

