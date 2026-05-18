"""Processamento e agregação de dados

Funcionalidades:
- Carrega dados de fazendas (mock)
- Filtra dados para geometrias específicas
- Calcula índices derivados
- Gera alertas baseado em limiares
- Cria boletins estruturados
"""
import logging
from datetime import datetime
from src.utils.shapefile_loader import carregar_fazendas_mock
from src.coleta.open_meteo import formatar_previsao_diaria
from src.coleta.nasa_power import formatar_dados_nasa

logger = logging.getLogger(__name__)

def processar_dados(dados_openmeteo, dados_nasa_power, dados_goes=None):
    """
    Processa dados das APIs e gera boletins estruturados

    Args:
        dados_openmeteo: Dados de previsão Open-Meteo
        dados_nasa_power: Dados climatológicos NASA
        dados_goes: Dados de satélite GOES (opcional)

    Returns:
        list: Lista de boletins por fazenda
    """
    logger.info("🔄 Processando dados...")

    try:
        # Carregar fazendas
        fazendas = carregar_fazendas_mock()
        logger.info(f"  ✓ {len(fazendas)} fazendas carregadas")

        # Formatar dados das APIs
        previsoes = formatar_previsao_diaria(dados_openmeteo)
        dados_nasa = formatar_dados_nasa(dados_nasa_power)

        # Processar por fazenda
        boletins = []
        for fazenda in fazendas:
            boletim = gerar_boletim(fazenda, previsoes, dados_nasa, dados_goes)
            boletins.append(boletim)

        logger.info(f"✓ Processamento concluído ({len(boletins)} boletins)")
        return boletins

    except Exception as e:
        logger.error(f"❌ Erro no processamento: {e}", exc_info=True)
        raise

def gerar_boletim(fazenda, previsoes, dados_nasa, dados_goes=None):
    """Gera um boletim completo para uma fazenda"""
    if previsoes:
        prev_hoje = previsoes[0]  # Primeiro dia
    else:
        prev_hoje = {}

    if dados_nasa:
        dados_clima = dados_nasa[-1]  # Último dia histórico
    else:
        dados_clima = {}

    # Extrair valores
    temp_max = prev_hoje.get("temp_max", 28)
    temp_min = prev_hoje.get("temp_min", 18)
    temp_media = (temp_max + temp_min) / 2
    chuva_mm = prev_hoje.get("chuva_mm", 0)
    prob_chuva = prev_hoje.get("prob_chuva", 0)
    vento_ms = prev_hoje.get("vento_ms", 5)
    eto = prev_hoje.get("eto_mm") or dados_clima.get("eto_mm", 5.0)
    radiacao = dados_clima.get("radiacao_mj", 20)
    umidade = dados_clima.get("umidade", 65)

    # Dados GOES
    ndvi = 0.7
    fogo_detectado = False
    if dados_goes:
        ndvi = dados_goes.get("ndvi", {}).get("valor", 0.7)
        fogo_detectado = dados_goes.get("fogo", {}).get("detectado", False)

    # Gerar alertas
    alertas = gerar_alertas(temp_min, chuva_mm, vento_ms, fogo_detectado)

    # Gerar resumo executivo
    resumo = gerar_resumo_executivo(alertas, chuva_mm, temp_max)

    # Recomendações
    recomendacoes = gerar_recomendacoes(alertas, eto, umidade)

    boletim = {
        "fazenda": fazenda["nome"],
        "lat": fazenda["lat"],
        "lon": fazenda["lon"],
        "cultura": fazenda["cultura"],
        "email": fazenda["email"],
        "data_geracao": datetime.now().isoformat(),
        "resumo_executivo": resumo,
        "temperatura": {
            "min": round(temp_min, 1),
            "max": round(temp_max, 1),
            "media": round(temp_media, 1),
            "unidade": "°C"
        },
        "precipitacao": {
            "prevista": round(chuva_mm, 1),
            "probabilidade": round(prob_chuva, 1),
            "unidade": "mm"
        },
        "umidade": {
            "valor": round(umidade, 1),
            "unidade": "%"
        },
        "vento": {
            "velocidade": round(vento_ms, 1),
            "unidade": "m/s",
            "kmh": round(vento_ms * 3.6, 1)
        },
        "radiacao_solar": round(radiacao, 1),
        "eto": round(eto, 2),
        "ndvi": round(ndvi, 2),
        "alertas": alertas,
        "recomendacoes": recomendacoes,
        "previsao_24h": previsoes[:1] if previsoes else []
    }

    return boletim

def gerar_alertas(temperatura_min, chuva_prevista, vento_max, fogo_detectado):
    """
    Gera alertas baseado em limiares agrícolas

    Alertas possíveis:
    - GEADA: temp_min < 0°C
    - CHUVA_SEVERA: chuva > 50mm
    - VENTO_FORTE: vento > 40 km/h (11 m/s)
    - QUEIMADA: detecção satélite
    """
    alertas = []

    if temperatura_min < 0:
        alertas.append({
            "tipo": "GEADA",
            "severidade": "alta",
            "emoji": "❄️",
            "descricao": f"Risco de geada: temperatura mínima {temperatura_min:.1f}°C",
            "recomendacao": "Proteja culturas sensíveis (café, citros, hortaliças)"
        })
    elif temperatura_min < 5:
        alertas.append({
            "tipo": "GEADA_RISCO",
            "severidade": "media",
            "emoji": "🥶",
            "descricao": f"Risco moderado de geada: {temperatura_min:.1f}°C",
            "recomendacao": "Monitore temperatura noturna"
        })

    if chuva_prevista and chuva_prevista > 50:
        alertas.append({
            "tipo": "CHUVA_SEVERA",
            "severidade": "alta",
            "emoji": "⛈️",
            "descricao": f"Precipitação intensa prevista: {chuva_prevista:.1f}mm",
            "recomendacao": "Adiantar colheita; preparar drenagem"
        })
    elif chuva_prevista and chuva_prevista > 20:
        alertas.append({
            "tipo": "CHUVA_MODERADA",
            "severidade": "media",
            "emoji": "🌧️",
            "descricao": f"Chuva moderada prevista: {chuva_prevista:.1f}mm",
            "recomendacao": "Aguarde antes de pulverizar"
        })

    if vento_max > 11:  # ~40 km/h
        alertas.append({
            "tipo": "VENTO_FORTE",
            "severidade": "media",
            "emoji": "💨",
            "descricao": f"Vento forte: {vento_max:.1f}m/s ({vento_max*3.6:.1f}km/h)",
            "recomendacao": "Não recomendado pulverizar; risco de deriva"
        })

    if fogo_detectado:
        alertas.append({
            "tipo": "QUEIMADA",
            "severidade": "alta",
            "emoji": "🔥",
            "descricao": "Foco de incêndio/queimada detectado próximo",
            "recomendacao": "Acione autoridades ambientais imediatamente"
        })

    return alertas

def gerar_resumo_executivo(alertas, chuva, temp_max):
    """Gera resumo em uma frase"""
    if not alertas:
        return "Condições favoráveis para operações agrícolas."

    alert_alto = [a for a in alertas if a["severidade"] == "alta"]

    if alert_alto:
        return f"⚠️ {alert_alto[0]['descricao']} Monitore as condições."

    return f"Chuva prevista de {chuva:.0f}mm. Temperatura máxima {temp_max:.0f}°C."

def gerar_recomendacoes(alertas, eto, umidade):
    """Gera recomendações práticas"""
    recomendacoes = []

    # ETo e irrigação
    if eto > 6:
        recomendacoes.append(f"💧 ETo alta ({eto:.1f}mm/dia): aumentar lâmina d'água em {eto*0.7:.1f}mm")
    elif eto < 2:
        recomendacoes.append(f"💧 ETo baixa ({eto:.1f}mm/dia): reduzir irrigação")

    # Umidade
    if umidade > 80:
        recomendacoes.append("🌱 Umidade alta: risco de doenças fúngicas. Melhorar ventilação")
    elif umidade < 40:
        recomendacoes.append("☀️ Umidade baixa: risco de evaporação. Aumentar frequência de irrigação")

    # Alertas
    for alerta in alertas:
        if "recomendacao" in alerta:
            recomendacoes.append(f"{alerta['emoji']} {alerta['recomendacao']}")

    # Default se nenhuma recomendação
    if not recomendacoes:
        recomendacoes.append("✓ Sem recomendações críticas no momento")

    return recomendacoes[:3]  # Limitar a 3 recomendações
