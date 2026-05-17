# Testa apenas a coleta do Open-Meteo — sem precisar de nenhuma credencial
from collector_openmeteo import fetch_openmeteo

# Coordenadas de Ribeirão Preto como exemplo
dados = fetch_openmeteo(lat=-21.1704, lon=-47.8103)

print("Coleta OK!")
print(f"Primeiras horas coletadas: {dados['hourly_24h'].head()}")
print(f"Previsão de hoje: {dados['daily_7d'][0]}")