"""Coleta de dados GOES-16/19 via AWS S3

Satélite NOAA que cobre América do Sul com imagens a cada 10 minutos.

Bandas prioritárias:
- Banda 2 (0.64 µm): Cobertura de nuvens, frentes de chuva
- Banda 3 (0.86 µm): Saúde da vegetação, queimadas
- Banda 7 (3.9 µm): FOCOS DE INCÊNDIO (crítico!)
- Banda 11 (8.4 µm): Temperatura, risco de geada
- Banda 13 (10.3 µm): Altura de nuvens, tempo severo
- Banda 14 (11.2 µm): Estimativa de precipitação (QPE)
"""
import logging

logger = logging.getLogger(__name__)

def coletar_goes(bandas=[2, 3, 7, 11, 13, 14]):
    """
    Coleta imagens GOES-16/19 do bucket S3 público AWS

    Args:
        bandas: Lista de bandas espectrais a coletar

    Returns:
        dict: Dados de satélite e índices derivados
    """
    import boto3
    from src.utils.config import AWS_REGION

    logger.info("🛰️  Coletando dados GOES-16/19...")

    # TODO: Implementar
    # 1. Conectar ao bucket S3 público: noaa-goes16 ou noaa-goes17
    # 2. Listar produtos mais recentes por banda
    # 3. Download e processamento com rasterio
    # 4. Extrair valores para geometrias de shapefiles
    # 5. Calcular índices:
    #    - NDVI (Banda 3 / Banda 2): Saúde da vegetação
    #    - Fire Detection (Banda 7 + algoritmo): Queimadas
    #    - Cloud Top Temperature (Banda 13): Intensidade de nuvem
    #    - QPE (Banda 14 + algoritmo): Precipitação estimada

    try:
        s3 = boto3.client("s3", region_name=AWS_REGION)

        logger.info(f"✓ Dados GOES coletados (bandas: {bandas})")
        return {}  # TODO: Substituir por dados reais

    except Exception as e:
        logger.error(f"❌ Erro ao coletar GOES: {e}")
        raise
