"""Coleta de dados Open-Meteo API

Requisita previsão numérica do tempo de múltiplas fontes:
- GFS (americano)
- ICON (alemão)
- ERA5 (reanálise europeia)

Variáveis: temperatura, precipitação, umidade, vento, radiação solar, ETo
"""
import logging
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

def coletar_open_meteo(latitude=-15.7942, longitude=-48.2694, dias=7):
    """
    Coleta dados de previsão da Open-Meteo API

    Args:
        latitude: Latitude (default: Goiás)
        longitude: Longitude (default: Goiás)
        dias: Número de dias a prever (default: 7)

    Returns:
        dict: Dados de previsão com chaves 'daily' e 'hourly'
    """
    from src.utils.config import OPEN_METEO_API_URL

    logger.info(f"📍 Coletando Open-Meteo para ({latitude}, {longitude})...")

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,windspeed_10m_max,evapotranspiration",
        "hourly": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,solar_radiation",
        "timezone": "America/Sao_Paulo",
        "forecast_days": min(dias, 16),
    }

    try:
        response = requests.get(OPEN_METEO_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        logger.info(f"✓ Previsão para {dias} dias coletada")
        return data

    except requests.exceptions.Timeout:
        logger.error("❌ Timeout na API Open-Meteo")
        return {}
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erro ao coletar Open-Meteo: {e}")
        return {}

def formatar_previsao_diaria(data_openmeteo):
    """Formata resposta JSON em lista de dicts"""
    if not data_openmeteo or "daily" not in data_openmeteo:
        return []

    daily = data_openmeteo["daily"]
    datas = daily.get("time", [])
    temps_max = daily.get("temperature_2m_max", [])
    temps_min = daily.get("temperature_2m_min", [])
    chuvas = daily.get("precipitation_sum", [])
    prob_chuva = daily.get("precipitation_probability_max", [])
    ventos = daily.get("windspeed_10m_max", [])
    eto = daily.get("evapotranspiration", [])

    previsoes = []
    for i, data in enumerate(datas):
        previsoes.append({
            "data": data,
            "temp_max": temps_max[i] if i < len(temps_max) else None,
            "temp_min": temps_min[i] if i < len(temps_min) else None,
            "chuva_mm": chuvas[i] if i < len(chuvas) else 0,
            "prob_chuva": prob_chuva[i] if i < len(prob_chuva) else 0,
            "vento_ms": ventos[i] if i < len(ventos) else None,
            "eto_mm": eto[i] if i < len(eto) else None,
        })

    return previsoes
