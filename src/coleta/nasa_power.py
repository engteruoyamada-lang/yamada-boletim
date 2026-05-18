"""Coleta de dados NASA POWER API

Fornece dados históricos e climatológicos de:
- Radiação solar
- Temperatura
- Umidade relativa
- Dados para cálculo de ETo (evapotranspiração de referência)
"""
import logging
import requests
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def coletar_nasa_power(latitude=-15.7942, longitude=-48.2694, dias=7):
    """
    Coleta dados climatológicos da NASA POWER API

    Args:
        latitude: Latitude
        longitude: Longitude
        dias: Número de dias históricos a coletar

    Returns:
        dict: Dados de radiação, temperatura, umidade
    """
    from src.utils.config import NASA_POWER_API_URL

    logger.info(f"☀️  Coletando NASA POWER para ({latitude}, {longitude})...")

    # Datas para API (últimos N dias + hoje)
    data_fim = datetime.now()
    data_inicio = data_fim - timedelta(days=dias)

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start": data_inicio.strftime("%Y%m%d"),
        "end": data_fim.strftime("%Y%m%d"),
        "parameters": "ALLSKY_SFC_SW_DWN,T2M_MAX,T2M_MIN,T2M_MEAN,RH2M,WS2M",
        "community": "AG",
        "format": "JSON",
    }

    try:
        url = f"{NASA_POWER_API_URL}temporal/daily/point"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        logger.info(f"✓ Dados NASA POWER coletados com sucesso")
        return data

    except requests.exceptions.Timeout:
        logger.error("❌ Timeout na API NASA POWER")
        return {}
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erro ao coletar NASA POWER: {e}")
        return {}

def calcular_eto_penman_monteith(radiacao_mj, t_max, t_min, umidade, vento):
    """
    Calcula evapotranspiração de referência (ETo) via Penman-Monteith (FAO-56)

    Entradas:
    - radiacao_mj: radiação solar (MJ/m²/dia)
    - t_max, t_min: temperatura máxima e mínima (°C)
    - umidade: umidade relativa média (%)
    - vento: velocidade do vento a 2m (m/s)

    Saída:
    - ETo em mm/dia

    Fórmula: ETo = [0.408*Δ*(Rn-G) + γ*(Cn/(T+273))*u2*(es-ea)] / [Δ + γ*(1+Cd*u2)]
    """
    import math

    # Constantes
    Gsc = 0.0820  # Constante solar (MJ/(m²·min))
    Cn = 900  # Coeficiente para grama (W/m²·K)
    Cd = 0.34  # Coeficiente de ajuste do vento

    t_med = (t_max + t_min) / 2

    # 1. Declinação solar e ângulo horário
    # Aproximação: radiação de onda curta em MJ/m²
    Rn = radiacao_mj * 0.77 - 2.4  # Radiação líquida (simplificação)
    if Rn < 0:
        Rn = 0

    # 2. Pressão de vapor de saturação (kPa)
    es = 0.6108 * math.exp((17.27 * t_med) / (t_med + 237.3))

    # 3. Pressão atual de vapor (kPa)
    ea = es * (umidade / 100)

    # 4. Déficit de pressão de vapor
    delta_vp = es - ea

    # 5. Slope da curva de pressão de vapor (kPa/°C)
    delta = (4098 * es) / ((t_med + 237.3) ** 2)

    # 6. Pressão atmosférica (kPa) - aproximação para 100m
    P = 101.3 - 0.01055 * 100

    # 7. Constante psicométrica (kPa/°C)
    gamma = 0.000665 * P

    # 8. ETo (mm/dia)
    numerador = (0.408 * delta * Rn) + (gamma * (Cn / (t_med + 273)) * vento * delta_vp)
    denominador = delta + gamma * (1 + Cd * vento)

    eto = numerador / denominador if denominador > 0 else 0

    return max(eto, 0)  # ETo não pode ser negativo

def formatar_dados_nasa(data_nasa):
    """Formata resposta JSON da NASA POWER em lista de dicts"""
    if not data_nasa or "properties" not in data_nasa:
        return []

    props = data_nasa["properties"]
    daily_data = props.get("parameter", {})

    # Extrair dados diários
    radiacao = daily_data.get("ALLSKY_SFC_SW_DWN", {})
    t_max = daily_data.get("T2M_MAX", {})
    t_min = daily_data.get("T2M_MIN", {})
    t_med = daily_data.get("T2M_MEAN", {})
    umidade = daily_data.get("RH2M", {})
    vento = daily_data.get("WS2M", {})

    dados_formatados = []

    # Listar todas as datas (keys dos dicts)
    todas_datas = set(radiacao.keys()) | set(t_max.keys()) | set(t_min.keys())

    for data_str in sorted(todas_datas):
        rad = radiacao.get(data_str, 20)  # Default 20 MJ/m²/dia
        tmax = t_max.get(data_str, 28)
        tmin = t_min.get(data_str, 18)
        tmed = t_med.get(data_str, (tmax + tmin) / 2)
        umid = umidade.get(data_str, 65)
        v = vento.get(data_str, 2)

        # Calcular ETo
        eto = calcular_eto_penman_monteith(rad, tmax, tmin, umid, v)

        dados_formatados.append({
            "data": data_str,
            "radiacao_mj": rad,
            "t_max": tmax,
            "t_min": tmin,
            "t_med": tmed,
            "umidade": umid,
            "vento_ms": v,
            "eto_mm": round(eto, 2)
        })

    return dados_formatados
