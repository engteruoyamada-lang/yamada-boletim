"""Loader de fazendas (simplificado, sem geopandas)"""
import json
from pathlib import Path

def carregar_fazendas_mock():
    """Carrega fazendas de teste (mock)"""
    fazendas = [
        {
            "nome": "Fazenda Goiás",
            "lat": -15.7942,
            "lon": -48.2694,
            "area_ha": 500,
            "cultura": "Soja",
            "email": "produtor1@fazenda.com.br"
        },
        {
            "nome": "Fazenda São Paulo",
            "lat": -23.5505,
            "lon": -46.6333,
            "area_ha": 800,
            "cultura": "Milho",
            "email": "produtor2@fazenda.com.br"
        },
        {
            "nome": "Fazenda Mato Grosso",
            "lat": -15.8267,
            "lon": -56.3045,
            "area_ha": 1200,
            "cultura": "Algodão",
            "email": "produtor3@fazenda.com.br"
        }
    ]
    return fazendas

def carregar_boletim_recente(fazenda_nome):
    """Carrega boletim mais recente de uma fazenda"""
    from datetime import datetime

    data_hoje = datetime.now().strftime("%Y-%m-%d")
    path = Path(f"boletins/{data_hoje}/{fazenda_nome.lower().replace(' ', '_')}.json")

    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def listar_boletins(fazenda_nome):
    """Lista todos os boletins de uma fazenda"""
    boletins_path = Path("boletins")
    boletins = []

    if boletins_path.exists():
        for data_dir in sorted(boletins_path.iterdir(), reverse=True):
            filename = f"{fazenda_nome.lower().replace(' ', '_')}.json"
            boletim_file = data_dir / filename
            if boletim_file.exists():
                with open(boletim_file, 'r', encoding='utf-8') as f:
                    boletins.append({
                        "data": data_dir.name,
                        "caminho": str(boletim_file)
                    })

    return boletins
