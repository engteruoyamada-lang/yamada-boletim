# Shapefiles das Fazendas

Este diretório contém os shapefiles (formato vetorial geoespacial) que definem as localizações e limites das fazendas monitoradas pelo sistema Yamada.

## Como Adicionar uma Fazenda

### 1. Preparar o Shapefile

Cada fazenda deve ser representada como um arquivo Shapefile (`.shp`). Um Shapefile completo consiste de:

```
fazenda_nome/
├── fazenda_nome.shp        # Geometrias
├── fazenda_nome.shx        # Índice
├── fazenda_nome.dbf        # Atributos
└── fazenda_nome.prj        # Projeção (opcional, mas recomendado)
```

**Formatos aceitos**: Polígonos (área da fazenda) ou pontos (coordenadas centrais).

### 2. Projeção Recomendada

- **Sistema de Coordenadas**: WGS84 (EPSG:4326)
- Longitude/Latitude (graus decimais)

Exemplo de estrutura de atributos obrigatórios no `.dbf`:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `nome` | String | Nome da fazenda |
| `lat` | Float | Latitude (para pontos) |
| `lon` | Float | Longitude (para pontos) |
| `area_ha` | Float | Área em hectares |
| `cultura` | String | Cultura principal (milho, soja, café, etc.) |
| `email` | String | Email do produtor |

### 3. Adicionar ao Repositório

```bash
# 1. Copiar os arquivos .shp/.shx/.dbf/.prj para esta pasta
cp ~/seu_shapefile/* ./

# 2. Adicionar ao git
git add fazenda_nome.*

# 3. Fazer commit
git commit -m "Add fazenda_nome shapefile"

# 4. Push
git push origin main
```

### 4. Verificar Integridade

O sistema carregará automaticamente todos os shapefiles desta pasta via `geopandas`. Teste localmente:

```python
import geopandas as gpd

# Carregar todos os shapefiles
gdf = gpd.read_file("shapefiles/*.shp")
print(gdf.head())
print(f"Fazendas carregadas: {len(gdf)}")
```

## Ferramentas para Criar/Editar Shapefiles

- **QGIS** (Open Source): https://www.qgis.org/
- **ArcGIS** (Comercial): https://www.arcgis.com/
- **PostGIS** (Database): https://postgis.net/
- **Python**: Crie programaticamente com geopandas/shapely

## Estrutura Esperada no Código

O arquivo `src/processamento/aggregador.py` lerá automaticamente:

```python
import geopandas as gpd
import glob

# Carrega todos os shapefiles
shapefiles = glob.glob("shapefiles/*.shp")
fazendas = gpd.GeoDataFrame(
    pd.concat([gpd.read_file(f) for f in shapefiles], ignore_index=True)
)
```

---

**Última atualização**: 2026-05-17  
**Versão**: 1.0
