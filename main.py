# main.py
# Orquestra o pipeline completo: coleta → processamento → PDF → entrega.
# É o único script chamado pelo GitHub Actions.

import json
import os
from pathlib import Path
from datetime import datetime

from collector_openmeteo import fetch_openmeteo
from collector_goes import baixar_banda_goes
from processor import processar_dados
from report_gen import gerar_pdf
from delivery import entregar_para_cliente
from shapefile_loader import centroide_da_fazenda, carregar_fazenda


def main():
    print(f"\n{'='*60}")
    print(f"Pipeline Yamada Engenharia — {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*60}\n")

    # Cria diretórios de saída se não existirem
    Path("output").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)

    # Carrega lista de clientes
    clientes = json.loads(Path("clientes.json").read_text(encoding="utf-8"))

    # Dados GOES são coletados uma vez e reutilizados para todos os clientes
    # (economiza chamadas ao S3 e tempo de processamento)
    print("→ Coletando dados do satélite GOES...")
    dados_goes_b14 = baixar_banda_goes(banda=14, lat_centro=-22.0, lon_centro=-47.5)
    dados_goes_b13 = baixar_banda_goes(banda=13, lat_centro=-22.0, lon_centro=-47.5)

    for cliente in clientes:
        nome = cliente["nome"]
        print(f"\n── Processando: {nome} ──")

        try:
            # Determina lat/lon: prioriza centroide do shapefile se disponível
            if cliente.get("shapefile"):
                gdf = carregar_fazenda(cliente["shapefile"])
                lat, lon = centroide_da_fazenda(gdf)
                print(f"   Centroide do shapefile: lat={lat:.4f}, lon={lon:.4f}")
            else:
                lat, lon = cliente["lat"], cliente["lon"]

            # Coleta dados meteorológicos para a coordenada da fazenda
            print(f"   Coletando Open-Meteo...")
            dados_meteo = fetch_openmeteo(lat, lon)

            # Processa e gera alertas
            dados = processar_dados(
                dados_meteo = dados_meteo,
                dados_goes  = {
                    "banda14": dados_goes_b14,
                    "banda13": dados_goes_b13,
                },
                cliente = cliente,
            )

            # Gera PDF
            slug      = nome.lower().replace(" ", "_").replace("/", "-")
            data_slug = datetime.now().strftime("%Y%m%d")
            pdf_path  = f"output/boletim_{slug}_{data_slug}.pdf"

            print(f"   Gerando PDF...")
            gerar_pdf(
                dados         = dados,
                fazenda       = nome,
                regiao        = cliente.get("regiao", "Brasil"),
                caminho_saida = pdf_path,
                cliente       = cliente,  # passa o dict completo para o shapefile
            )

            # Entrega por e-mail
            print(f"   Enviando e-mail para {cliente['email']}...")
            entregar_para_cliente(cliente, pdf_path, dados)

            print(f"   ✓ {nome} — concluído")

        except Exception as e:
            # Um cliente com erro não para o pipeline dos outros
            print(f"   ✗ ERRO em '{nome}': {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*60}")
    print("Pipeline concluído.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()