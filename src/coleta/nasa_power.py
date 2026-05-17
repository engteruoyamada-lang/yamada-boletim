"""Coleta de dados NASA POWER API

Fornece dados históricos e climatológicos de:
- Radiação solar
- Temperatura
- Umidade relativa
- Dados para cálculo de ETo (evapotranspiração de referência)
"""
import logging

logger = logging.getLogger(__name__)

def coletar_nasa_power(latitude=None, longitude=None):
    """
    Coleta dados climatológicos da NASA POWER API

    Args:
        latitude: Latitude
        longitude: Longitude

    Returns:
        dict: Dados de radiação e temperatura
    """
    import requests
    from src.utils.config import NASA_POWER_API_URL

    logger.info("☀️  Coletando dados NASA POWER...")

    # TODO: Implementar
    # 1. Extrair coordenadas de shapefiles se não fornecidas
    # 2. Request à API POWER para radiação, temperatura, umidade
    # 3. Calcular ETo via Penman-Monteith
    # 4. Retornar em DataFrame

    params = {
        "latitude": latitude or -15.7942,
        "longitude": longitude or -48.2694,
        "parameters": "ALLSKY_SFC_SW_DWN,T2M,RH2M,WS2M",
        "community": "AG",
        "format": "JSON",
    }

    try:
        url = f"{NASA_POWER_API_URL}temporal/daily/point"
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        logger.info(f"✓ Dados NASA POWER coletados com sucesso")
        return data

    except Exception as e:
        logger.error(f"❌ Erro ao coletar NASA POWER: {e}")
        raise
