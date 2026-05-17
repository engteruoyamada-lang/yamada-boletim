"""Testes unitários - Coleta de dados"""
import pytest

def test_coletar_open_meteo():
    """Testa coleta Open-Meteo API"""
    from src.coleta.open_meteo import coletar_open_meteo

    # TODO: Implementar
    # dados = coletar_open_meteo()
    # assert "daily" in dados or "hourly" in dados
    pass

def test_coletar_nasa_power():
    """Testa coleta NASA POWER API"""
    from src.coleta.nasa_power import coletar_nasa_power

    # TODO: Implementar
    # dados = coletar_nasa_power()
    # assert "properties" in dados
    pass

if __name__ == "__main__":
    pytest.main([__file__])
