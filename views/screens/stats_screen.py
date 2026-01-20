import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from services.database import buscar_leads_filtrados

def exibir_estatisticas():
    st.header("📈 Relatórios de Desempenho")
    u = st.session_state.user_data
    leads = buscar_leads_filtrados(u)
    
    if not leads:
        st.info("Dados insuficientes para gerar relatórios.")
        return

    # Criar DataFrame inicial
    df_completo = pd.DataFrame(leads)
    df_completo['data_criacao'] = pd.to_datetime(df_completo['data_criacao'])
    df_completo['data_dia'] = df_completo['data_criacao'].dt.date

    # --- NOVO: FILTRO DE PERÍODO ---
    col_filtro1, col_filtro2 = st.columns([1, 2])
    with col_filtro1:
        periodo = st.selectbox(
            "Selecionar Período",
            ["Hoje", "Últimos 7 Dias", "Últimos 30 Dias", "Todo o Período"],
            index=3
        )

    # Lógica do Filtro de Data
    hoje = datetime.now().date()
    if periodo == "Hoje":
        df = df_completo[df_completo['data_dia'] == hoje]
    elif periodo == "Últimos 7 Dias":
        data_limite = hoje - timedelta(days=7)
        df = df_completo[df_completo['data_dia'] >= data_limite]
    elif periodo == "Últimos 30 Dias":
        data_limite = hoje - timedelta(days=30)
        df = df_completo[df_completo['data_dia'] >= data_limite]
    else:
        df = df_completo

    if df.empty:
        st.warning(f"Não existem leads registados no período: {periodo}")
        return

    # --- MÉTRICAS (Com o estilo cinza escuro do main.py) ---
    m1, m2, m3 = st.columns(3)
    total = len(df)
    finalizados = len(df[df['status'] == 'Finalizado'])
    taxa = (finalizados / total * 100) if total > 0 else 0
    
    m1.metric("Total de Leads", total)
    m2.metric("Ativos", len(df[df['status'] != 'Finalizado']))
    m3.metric("Conversão", f"{taxa:.1f}%")

    st.divider()

    # --- GRÁFICO DE EVOLUÇÃO ---
    st.subheader(f"📅 Evolução - {periodo}")
    evolucao_diaria = df.groupby('data_dia').size().reset_index(name='Quantidade')
    evolucao_diaria = evolucao_diaria.sort_values('data_dia')
    
    # Exibe o gráfico de linha (azul)
    st.line_chart(evolucao_diaria.set_index('data_dia'), color="#0ea5e9")

    st.divider()

    # --- DISTRIBUIÇÃO ---
    g1, g2 = st.columns(2)
    with g1:
        st.subheader("📊 Status")
        st.bar_chart(df['status'].value_counts(), color="#25D366")
    
    with g2:
        st.subheader("👥 Performance por Vendedor")
        st.bar_chart(df['vendedor_id'].value_counts(), color="#0ea5e9")

    # Opção de download dos dados filtrados
    st.divider()
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📥 Baixar Relatório ({periodo})",
        data=csv,
        file_name=f"leads_gs_{periodo.lower().replace(' ', '_')}.csv",
        mime="text/csv",
        use_container_width=True
    )
