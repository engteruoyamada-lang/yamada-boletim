# shapefile_loader.py
# Carrega shapefiles de fazendas e expõe geometrias prontas para uso
# no recorte do GOES e na renderização do mapa PDF.

import geopandas as gpd
import numpy as np
from pathlib import Path
from shapely.geometry import box as shapely_box

# Diretório raiz dos shapefiles — relativo à raiz do repositório
SHAPEFILES_DIR = Path("shapefiles")

# CRS de referência: WGS84 geográfico (latitude/longitude)
CRS_PADRAO = "EPSG:4326"


def carregar_fazenda(nome_shapefile: str) -> gpd.GeoDataFrame:
    """
    Carrega o shapefile de uma fazenda e garante que está em WGS84.

    Parâmetros:
        nome_shapefile: nome da subpasta e do arquivo, ex: "fazenda_sao_joao"
                        (sem extensão)

    Retorna:
        GeoDataFrame com a geometria da fazenda em EPSG:4326
    """
    pasta  = SHAPEFILES_DIR / nome_shapefile
    shp    = pasta / f"{nome_shapefile}.shp"

    if not shp.exists():
        raise FileNotFoundError(
            f"Shapefile não encontrado: {shp}\n"
            f"Verifique se os 4 arquivos (.shp, .dbf, .prj, .shx) existem em {pasta}/"
        )

    gdf = gpd.read_file(shp)

    # Reprojeta para WGS84 se necessário
    if gdf.crs is None:
        print(f"⚠️  {nome_shapefile}: CRS não definido. Assumindo EPSG:4326.")
        gdf = gdf.set_crs(CRS_PADRAO)
    elif gdf.crs.to_epsg() != 4326:
        print(f"  Reprojetando {nome_shapefile} de {gdf.crs} para EPSG:4326...")
        gdf = gdf.to_crs(CRS_PADRAO)

    print(f"✓ Shapefile '{nome_shapefile}' carregado: {len(gdf)} feição(ões)")
    return gdf


def bbox_da_fazenda(gdf: gpd.GeoDataFrame, buffer_graus: float = 0.05) -> dict:
    """
    Calcula a bounding box da fazenda com um buffer de segurança.

    O buffer garante que o polígono não fique colado na borda do recorte.
    0.05 graus ≈ 5.5 km na latitude do Brasil central — adequado para a maioria.

    Retorna:
        dict com chaves: lon_min, lat_min, lon_max, lat_max
    """
    bounds = gdf.total_bounds  # [minx, miny, maxx, maxy] = [lon_min, lat_min, ...]

    return {
        "lon_min": float(bounds[0]) - buffer_graus,
        "lat_min": float(bounds[1]) - buffer_graus,
        "lon_max": float(bounds[2]) + buffer_graus,
        "lat_max": float(bounds[3]) + buffer_graus,
    }


def centroide_da_fazenda(gdf: gpd.GeoDataFrame) -> tuple[float, float]:
    """
    Retorna (latitude, longitude) do centroide da fazenda.
    Usado para passar à Open-Meteo e NASA POWER.
    """
    centroide = gdf.dissolve().centroid.iloc[0]
    return float(centroide.y), float(centroide.x)  # (lat, lon)