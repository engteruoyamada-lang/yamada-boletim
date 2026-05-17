"""Interface Streamlit - Dashboard Yamada Engenharia

Apresentação interativa com:
- Login (Yamada/Yamada)
- Seleção de fazenda
- Dashboard com cards, gráficos e mapas
- Histórico de boletins
- Download de PDFs
"""
import streamlit as st
import logging

logger = logging.getLogger(__name__)

def main():
    """App principal Streamlit"""

    # TODO: Implementar
    # 1. Configuração da página (tema Yamada)
    # 2. Autenticação (login Yamada/Yamada)
    # 3. Sidebar com seleção de fazenda
    # 4. Dashboard principal:
    #    a) Cards: temperatura, chuva, umidade, ETo
    #    b) Gráficos: previsão 24h, 7 dias
    #    c) Mapa com localização da fazenda
    #    d) Alertas destacados
    # 5. Histórico de boletins
    # 6. Download de PDF

    st.set_page_config(
        page_title="Yamada Engenharia",
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Aplicar tema
    st.markdown("""
    <style>
    :root {
        --primary-color: #1B4D2E;
        --secondary-color: #3DA63A;
        --text-color: #1A1A1A;
        --background-color: #FFFFFF;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("🌾 Yamada Engenharia")
    st.subtitle("Boletim Meteorológico para Agronegócio")

    # Login (simplificado por enquanto)
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        with st.form("login"):
            user = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar"):
                if user == "Yamada" and password == "Yamada":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Credenciais inválidas")
        return

    # Dashboard autenticado
    with st.sidebar:
        st.header("📋 Opções")
        fazenda = st.selectbox("Selecione uma fazenda", ["Fazenda 1", "Fazenda 2"])
        periodo = st.selectbox("Período", ["24h", "7 dias", "30 dias"])

    st.success(f"Conectado como: Yamada")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🌡️ Temperatura", "25°C", "+2°C")
    with col2:
        st.metric("🌧️ Precipitação", "45mm", "75% prob")
    with col3:
        st.metric("💧 Umidade", "65%", "-5%")
    with col4:
        st.metric("💨 Vento", "12 m/s", "SE")

    st.divider()

    col_graph1, col_graph2 = st.columns(2)
    with col_graph1:
        st.subheader("📈 Previsão de Temperatura")
        st.line_chart({"Temperatura": [20, 22, 24, 25, 27, 26, 24]})

    with col_graph2:
        st.subheader("🌧️ Precipitação")
        st.bar_chart({"Chuva (mm)": [0, 5, 15, 45, 30, 5, 0]})

    st.divider()

    with st.expander("⚠️ Alertas"):
        st.warning("🔥 **Geada**: Risco mínimo de geada noturna")
        st.info("🌧️ **Chuva Severa**: Precipitação de 45mm prevista para amanhã")

    with st.expander("📚 Histórico de Boletins"):
        st.dataframe({
            "Data": ["2026-05-17", "2026-05-16", "2026-05-15"],
            "Temperatura": ["25°C", "24°C", "23°C"],
            "Precipitação": ["45mm", "0mm", "10mm"],
        })

if __name__ == "__main__":
    main()
