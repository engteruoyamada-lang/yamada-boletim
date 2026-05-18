"""Interface Streamlit - Dashboard Yamada Engenharia

Apresentação interativa com:
- Login (Yamada/Yamada)
- Seleção de fazenda com dados reais
- Dashboard com cards, gráficos e mapas
- Histórico de boletins
- Download de PDFs
"""
import streamlit as st
import geopandas as gpd
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

@st.cache_resource
def load_shapefiles():
    """Carrega todos os shapefiles disponíveis"""
    shapefiles_dir = Path("shapefiles")
    fazendas = {}

    if shapefiles_dir.exists():
        for shp_file in shapefiles_dir.glob("*.shp"):
            try:
                gdf = gpd.read_file(shp_file)
                nome = gdf.get("nome", [shp_file.stem]).values[0] if "nome" in gdf.columns else shp_file.stem
                fazendas[str(nome)] = {"path": str(shp_file), "gdf": gdf}
            except Exception as e:
                logger.error(f"Erro ao carregar {shp_file}: {e}")

    return fazendas

def get_fazenda_info(gdf):
    """Extrai informações principais da fazenda"""
    info = {}
    for col in ["nome", "area_ha", "cultura", "municipio", "email", "lat", "lon"]:
        if col in gdf.columns and len(gdf) > 0:
            info[col] = gdf[col].values[0]
    return info

def main():
    """App principal Streamlit"""

    st.set_page_config(
        page_title="Yamada Engenharia",
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("🌾 Yamada Engenharia")
    st.markdown("### Boletim Meteorológico para Agronegócio")

    # Login
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
    fazendas = load_shapefiles()

    with st.sidebar:
        st.header("📋 Opcoes")
        fazenda_nome = st.selectbox(
            "Selecione uma fazenda",
            list(fazendas.keys()) if fazendas else ["Nenhuma fazenda disponível"]
        )
        periodo = st.selectbox("Período", ["24h", "7 dias", "30 dias"])

    st.success(f"Conectado como: Yamada")

    # Informacoes da fazenda selecionada
    if fazendas and fazenda_nome in fazendas:
        gdf = fazendas[fazenda_nome]["gdf"]
        info = get_fazenda_info(gdf)

        # Mostrar informacoes da fazenda
        st.markdown("### Informacoes da Fazenda")
        col_info1, col_info2, col_info3, col_info4 = st.columns(4)

        with col_info1:
            st.metric("Municipio", info.get("municipio", "N/A"))
        with col_info2:
            st.metric("Area", f"{info.get('area_ha', 0):.1f} ha")
        with col_info3:
            st.metric("Cultura", info.get("cultura", "N/A"))
        with col_info4:
            st.metric("Coordenadas", f"{info.get('lat', 0):.3f}, {info.get('lon', 0):.3f}")

        if info.get("email"):
            st.info(f"Email da fazenda: {info['email']}")

    st.divider()

    # Metricas climaticas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Temperatura", "25°C", "+2°C")
    with col2:
        st.metric("Precipitacao", "45mm", "75% prob")
    with col3:
        st.metric("Umidade", "65%", "-5%")
    with col4:
        st.metric("Vento", "12 m/s", "SE")

    st.divider()

    # Graficos
    col_graph1, col_graph2 = st.columns(2)
    with col_graph1:
        st.subheader("Previsao de Temperatura")
        st.line_chart({"Temperatura": [20, 22, 24, 25, 27, 26, 24]})

    with col_graph2:
        st.subheader("Precipitacao")
        st.bar_chart({"Chuva (mm)": [0, 5, 15, 45, 30, 5, 0]})

    st.divider()

    # Alertas e historico
    with st.expander("Alertas"):
        st.warning("Geada: Risco minimo de geada noturna")
        st.info("Chuva Severa: Precipitacao de 45mm prevista para amanha")

    with st.expander("Historico de Boletins"):
        st.dataframe({
            "Data": ["2026-05-17", "2026-05-16", "2026-05-15"],
            "Temperatura": ["25°C", "24°C", "23°C"],
            "Precipitacao": ["45mm", "0mm", "10mm"],
        })

if __name__ == "__main__":
    main()
