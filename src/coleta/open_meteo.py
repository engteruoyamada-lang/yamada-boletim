"""Coleta de dados Open-Meteo API

Requisita previsão numérica do tempo de múltiplas fontes:
- GFS (americano)
- ICON (alemão)
- ERA5 (reanálise europeia)

Variáveis: temperatura, precipitação, umidade, vento, radiação solar, ETo
"""
import logging

logger = logging.getLogger(__name__)

def coletar_open_meteo(latitude=None, longitude=None, dias=7):
    """
    Coleta dados de previsão da Open-Meteo API

    Args:
        latitude: Latitude (opcional, usa shapefiles se None)
        longitude: Longitude (opcional, usa shapefiles se None)
        dias: Número de dias a prever (default: 7)

    Returns:
        dict: Dados de previsão formatados
    """
    import requests
    import pandas as pd
    from src.utils.config import OPEN_METEO_API_URL

    logger.info("📍 Coletando dados Open-Meteo...")

    # TODO: Implementar
    # 1. Se lat/lon não fornecidos, extrair do shapefile
    # 2. Fazer request à API
    # 3. Extrair variáveis relevantes
    # 4. Formatar em DataFrame

    params = {
        "latitude": latitude or -15.7942,  # Placeholder (Goiás)
        "longitude": longitude or -48.2694,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max,evapotranspiration",
        "hourly": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,solar_radiation",
        "forecast_days": dias,
    }

    try:
        response = requests.get(OPEN_METEO_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        logger.info(f"✓ Dados Open-Meteo coletados com sucesso")
        return data

    except Exception as e:
        logger.error(f"❌ Erro ao coletar Open-Meteo: {e}")
        raise
