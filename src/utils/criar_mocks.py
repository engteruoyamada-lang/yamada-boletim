"""Gerador de dados mock para testes"""
import json
from datetime import datetime, timedelta
from pathlib import Path

def criar_boletim_mock(fazenda_nome, lat, lon):
    """Cria um boletim meteorológico mock"""
    data_hoje = datetime.now().strftime("%Y-%m-%d")

    return {
        "fazenda": fazenda_nome,
        "lat": lat,
        "lon": lon,
        "data_geracao": datetime.now().isoformat(),
        "resumo_executivo": f"Condições favráveis para operações agrícolas. Chuva prevista de 45mm para amanhã à noite. Recomenda-se adiantar colheita se possível.",
        "temperatura": {
            "min": 15,
            "max": 28,
            "media": 21.5,
            "unidade": "°C"
        },
        "precipitacao": {
            "prevista": 45,
            "probabilidade": 75,
            "unidade": "mm",
            "historico_6h": 0
        },
        "umidade": {
            "valor": 65,
            "minima": 45,
            "maxima": 85,
            "unidade": "%"
        },
        "vento": {
            "velocidade": 12,
            "direcao": "SE",
            "rajada": 25,
            "unidade": "m/s"
        },
        "radiacao_solar": 22.5,
        "eto": 5.2,
        "ndvi": 0.75,
        "alertas": [
            {
                "tipo": "CHUVA_SEVERA",
                "severidade": "alta",
                "descricao": "Precipitação de 45mm prevista para amanhã à noite. Evite operações de pulverização."
            },
            {
                "tipo": "VENTO_FORTE",
                "severidade": "media",
                "descricao": "Velocidade do vento atingirá 25 m/s (90 km/h). Risco de danos a estruturas leves."
            }
        ],
        "recomendacoes": [
            "⚠️ Adiantar colheita antes da chuva",
            "💨 Reforçar estruturas contra vento forte",
            "💧 Preparar sistemas de drenagem"
        ],
        "previsao_24h": [
            {"hora": i, "temp": 20 + (i % 3), "chuva": 0 if i < 18 else (45 / 6)}
            for i in range(24)
        ]
    }

# Criar boletins mock para 3 fazendas
fazendas = [
    ("Fazenda Goiás", -15.7942, -48.2694),
    ("Fazenda São Paulo", -23.5505, -46.6333),
    ("Fazenda Mato Grosso", -15.8267, -56.3045),
]

# Criar diretório de boletins
data_hoje = datetime.now().strftime("%Y-%m-%d")
Path(f"boletins/{data_hoje}").mkdir(parents=True, exist_ok=True)

for fazenda_nome, lat, lon in fazendas:
    boletim = criar_boletim_mock(fazenda_nome, lat, lon)

    # Salvar JSON
    filename = f"boletins/{data_hoje}/{fazenda_nome.lower().replace(' ', '_')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(boletim, f, ensure_ascii=False, indent=2)
    print(f"✓ Boletim mock criado: {filename}")

print(f"\n✓ {len(fazendas)} boletins mock criados em boletins/{data_hoje}/")
