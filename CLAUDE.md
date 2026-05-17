# Yamada Engenharia — Boletim Meteorológico para Agronegócio

## Visão Geral

Sistema MVP serverless que coleta dados meteorológicos de fontes abertas e gratuitas, processa informações relevantes para produtores rurais e entrega um boletim diário via email em PDF com identidade visual Yamada Engenharia.

**Stack**: Open-Meteo + GOES-16/19 + NASA POWER → Processamento Python → PDF (ReportLab/Matplotlib) → Gmail API → Streamlit UI

**Orçamento**: Zero (apenas APIs públicas gratuitas).

---

## Arquitetura Geral

```
┌─────────────────────────────────────────────────────────────┐
│                   COLETA DE DADOS                            │
├──────────────┬──────────────────┬──────────────────────────┤
│ Open-Meteo   │ GOES-16/19 (S3)  │ NASA POWER               │
│ • Previsão   │ • Imagens satélite│ • Radiação solar         │
│ • 6 variáveis│ • 7 bandas úteis │ • Dados climatológicos   │
└──────────────┴──────────────────┴──────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              PROCESSAMENTO & AGREGAÇÃO                       │
│  • Filtra por shapefile de fazendas (geopandas)             │
│  • Calcula ETo (evapotranspiração)                          │
│  • Gera alertas de risco (geada, chuva severa, queimada)    │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                 GERAÇÃO DE RELATÓRIO                         │
│  • Streamlit: dashboard interativo + tabelas + mapas        │
│  • PDF: ReportLab + Matplotlib com identidade Yamada        │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              ENTREGA                                         │
│  • Gmail API (OAuth2): PDF anexado + resumo em texto        │
│  • Automação: GitHub Actions (cron 08h30 UTC diário)        │
│  • UI: Streamlit com login (Yamada/Yamada)                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. COLETA DE DADOS

### 1.1 Open-Meteo API

**O quê**: API de previsão numérica do tempo completamente gratuita, sem autenticação.

**Modelos base**: GFS (USA), ICON (Alemanha), ERA5 (reanálise histórica).

**Variáveis fornecidas** (horárias e diárias):
- **Temperatura**: mín, máx, atual (°C)
- **Precipitação**: volume (mm) e probabilidade (%)
- **Umidade relativa**: (%)
- **Velocidade do vento**: média e rajada (m/s)
- **Radiação solar**: radiação de onda curta global (W/m²)
- **Evapotranspiração**: evapotranspiração de referência (mm/dia)

**Por que é importante para o agronegócio**:
- Determina chuva prevista para irrigação ou colheita.
- Temperatura e umidade guiam operações de pulverização e colheita.
- Radiação solar influencia crescimento das plantas e evaporação.
- Evapotranspiração é entrada direta para cálculo de lâmina d'água.

**Endpoint usado**: `https://api.open-meteo.com/v1/forecast`

**Frequência**: Diária (01 previsão por dia).

---

### 1.2 GOES-16/19 (Satélite da NOAA)

**O quê**: Satélite geoestacionário que cobre toda a América do Sul com imagens a cada 10 minutos.

**Instrumento**: ABI (Advanced Baseline Imager) com 16 bandas espectrais. Disponível via bucket S3 público da AWS sem custo.

**Bandas prioritárias para agronegócio**:

| Banda | Comprimento de onda | Resolução | Uso agrícola | Horário |
|-------|-------------------|-----------|-----|----------|
| **2** | 0,64 µm (Vermelho) | 500 m/pixel | Cobertura de nuvens, frentes de chuva, imagens coloridas | Diurno |
| **3** | 0,86 µm (Veggie) | 1 km/pixel | Saúde da vegetação, estresse hídrico, queimadas | Diurno |
| **7** | 3,9 µm (Onda Curta) | 2 km/pixel | **Focos de incêndio/queimada em tempo real**, nevoeiro | 24/7 |
| **9** | 6,9 µm (Vapor d'água) | 2 km/pixel | Umidade atmosférica, trajetória de sistemas de chuva | 24/7 |
| **11** | 8,4 µm (Termal) | 2 km/pixel | Temperatura de superfície, **risco de geada** | 24/7 |
| **13** | 10,3 µm (Clean) | 2 km/pixel | **Altura e intensidade de nuvens**, risco de tempo severo | 24/7 |
| **14** | 11,2 µm (Infravermelho) | 2 km/pixel | **Estimativa de precipitação por satélite (QPE)** | 24/7 |

**Por que é crítico**:
- **Banda 7**: Identifica queimadas em tempo quase real (alerta crítico).
- **Banda 11**: Risco de geada é fator decisório para café, cana, citros no Sul/Sudeste.
- **Banda 13**: Direciona alertas de tempo severo (chuva, granizo, tempestade).
- **Banda 14**: Transforma temperatura de nuvem em precipitação estimada (mm/6h).

**Frequência**: A cada 10 minutos (consolidamos em resumos de 6h/24h).

---

### 1.3 NASA POWER API

**O quê**: API com dados históricos e climatológicos de radiação, temperatura e umidade em qualquer coordenada.

**Variáveis fornecidas**:
- Radiação solar incidente (kWh/m²/dia)
- Temperatura máxima e mínima
- Umidade relativa
- Velocidade do vento

**Por que é importante**:
- Base para cálculo de ETo (evapotranspiração de referência) pelo método Penman-Monteith.
- **ETo** é a variável mais importante para recomendação de lâmina d'água em irrigação.
- Dados históricos permitem comparação com climatologia e análise de anomalias.

**Frequência**: Diária (dados históricos consolidados).

---

## 2. PROCESSAMENTO & AGREGAÇÃO

### Dados de Entrada
- Coordenadas de fazendas (latitude, longitude) via **shapefiles** em `shapefiles/`.
- Cada fazenda pode ter múltiplas parcelas/talhões.

### Lógica de Processamento

1. **Download de dados** de todas as 3 fontes.
2. **Filtragem espacial**: Extrai variáveis apenas para os pontos/polígonos das fazendas (geopandas).
3. **Cálculo de ETo**: Combina dados NASA POWER com equação Penman-Monteith.
4. **Geração de alertas**:
   - Risco de geada (Banda 11 + temperatura mínima prevista < 0°C)
   - Tempo severo (Banda 13 + índices de instabilidade)
   - Queimadas ativas (Banda 7 + geolocalização)
   - Precipitação estimada por satélite (Banda 14 QPE)
5. **Agregação temporal**: Consolida previsão 24h + observações 6h anteriores.
6. **Ranking de recomendações**: Ordena ações por urgência/risco.

### Saída
Estrutura JSON com:
```json
{
  "fazenda": "Fazenda XYZ",
  "data_geracao": "2026-05-17T08:30:00Z",
  "resumo_executivo": "Risco de chuva forte amanhã à noite",
  "temperatura": {"min": 15, "max": 28, "unidade": "°C"},
  "precipitacao": {"prevista": 45, "probabilidade": 75, "unidade": "mm"},
  "umidade": 65,
  "vento": {"velocidade": 12, "unidade": "m/s"},
  "eto": 5.2,
  "alertas": [
    {"tipo": "CHUVA_SEVERA", "severidade": "alta", "descricao": "..."}
  ]
}
```

---

## 3. GERAÇÃO DE RELATÓRIO

### 3.1 Streamlit (Dashboard Interativo)

**Localização**: `src/relatorio/streamlit_app.py`

**Funcionalidades**:
- **Login**: user: `Yamada` / senha: `Yamada`
- **Seleção de fazenda**: Dropdown com todas as fazendas do shapefile.
- **Dashboard**:
  - Resumo executivo em cards (temperatura, chuva, ETo, alertas).
  - Gráficos de previsão (24h, 7 dias).
  - Mapa com localização da fazenda e áreas de risco.
  - Histórico de boletins anteriores.
- **Tema**: Identidade Yamada (verde escuro #1B4D2E, verde médio #3DA63A, preto, branco).

### 3.2 PDF (ReportLab + Matplotlib)

**Localização**: `src/relatorio/pdf_generator.py`

**Conteúdo**:
- Cabeçalho com logo Yamada + data/hora.
- Resumo executivo (1 parágrafo).
- Tabela de variáveis (temperatura, chuva, umidade, vento, ETo).
- Gráficos (Matplotlib):
  - Previsão de temperatura (24h).
  - Precipitação acumulada.
  - Umidade + velocidade do vento.
  - Índice de risco (escala 0–10).
- Alertas destacados em caixas coloridas.
- Rodapé com fonte de dados e aviso legal.

**Design**: Futurista com conectores visuais, ícones meteorológicos, paleta Yamada.

---

## 4. ENTREGA

### 4.1 Gmail API (OAuth2)

**Localização**: `src/entrega/email_sender.py`

**Fluxo**:
1. Autentica com credenciais OAuth2 (arquivo `secrets/gmail_credentials.json`).
2. Compõe email:
   - **Para**: Lista de emails dos produtores (de spreadsheet ou DB).
   - **Assunto**: `[Yamada] Boletim Meteorológico — {data}`
   - **Corpo**: Resumo em Markdown (temperatura, chuva, ETo, alertas, recomendações).
   - **Anexo**: PDF do relatório.
3. Envia via API Gmail.

**Variáveis de ambiente necessárias**:
```
GMAIL_SENDER_EMAIL=seu_email@gmail.com
GMAIL_CREDENTIALS_PATH=secrets/gmail_credentials.json
```

### 4.2 GitHub Actions (Automação)

**Localização**: `.github/workflows/boletim_diario.yml`

**Trigger**: Cron job diário às **08h30 UTC**.

**Passos**:
1. Checkout do repositório.
2. Setup Python + dependências.
3. Executa coleta + processamento + geração de PDF.
4. Envia email via Gmail API.
5. Commit do boletim em histórico (opcional).

---

## 5. INTERFACE STREAMLIT

### Estrutura da Pasta
```
src/relatorio/
├── __init__.py
├── streamlit_app.py       # App principal
├── components/
│   ├── login.py           # Autenticação
│   ├── dashboard.py       # Dashboard cards/gráficos
│   ├── mapa.py            # Visualização de mapas
│   └── alertas.py         # Exibição de alertas
└── styles.py              # CSS/tema Yamada
```

### Fluxo de Usuário

1. **Login**: `user: Yamada / senha: Yamada`
2. **Seleção de fazenda**: Dropdown carrega geopandas.
3. **Dashboard**: Exibe boletim atual + 7 dias.
4. **Download**: Botão para baixar PDF do boletim.
5. **Histórico**: Acesso a boletins anteriores.

---

## 6. ESTRUTURA DE PASTAS

```
yamada-boletim/
├── CLAUDE.md                          # Este arquivo
├── README.md                          # Guia rápido de uso
├── requirements.txt                   # Dependências Python
├── .env.example                       # Template de variáveis
├── .gitignore                         # Ignora .env, secrets/, venv/
│
├── src/
│   ├── __init__.py
│   ├── coleta/
│   │   ├── __init__.py
│   │   ├── open_meteo.py             # Download Open-Meteo
│   │   ├── goes.py                   # Download GOES-16/19 do S3
│   │   └── nasa_power.py             # Download NASA POWER
│   ├── processamento/
│   │   ├── __init__.py
│   │   └── aggregador.py             # Processamento + alertas
│   ├── relatorio/
│   │   ├── __init__.py
│   │   ├── streamlit_app.py          # App Streamlit
│   │   ├── pdf_generator.py          # Geração de PDF
│   │   └── components/
│   │       ├── __init__.py
│   │       ├── login.py
│   │       ├── dashboard.py
│   │       └── alertas.py
│   ├── entrega/
│   │   ├── __init__.py
│   │   └── email_sender.py           # Gmail API
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py                 # Carregamento de variáveis
│   │   └── logging_setup.py
│   └── main.py                       # Orquestrador principal
│
├── assets/
│   ├── logo/                         # 👈 **COLOQUE SEU LOGO AQUI**
│   │   ├── yamada_logo.png           # Logotipo Yamada
│   │   └── yamada_logo_white.png     # Variante branca
│   ├── fonts/                        # Fontes customizadas
│   │   └── roboto-bold.ttf           # (opcional)
│   └── icons/                        # Ícones meteorológicos
│
├── shapefiles/                       # 👈 **COLOQUE SEUS SHAPEFILES AQUI**
│   ├── fazenda_01.shp
│   ├── fazenda_01.shx
│   ├── fazenda_01.dbf
│   └── README.md                     # Como adicionar fazendas
│
├── config/
│   ├── __init__.py
│   └── branding.py                   # Cores e estilos Yamada
│
├── secrets/                          # 👈 NUNCA COMMITAR (no .gitignore)
│   └── gmail_credentials.json        # OAuth2 credentials
│
├── .github/
│   └── workflows/
│       └── boletim_diario.yml        # GitHub Actions cron
│
├── tests/
│   ├── __init__.py
│   ├── test_coleta.py
│   ├── test_processamento.py
│   └── test_entrega.py
│
└── .git                              # Repositório Git
```

---

## 7. IDENTIDADE VISUAL YAMADA

### Paleta de Cores
- **Verde escuro**: `#1B4D2E` (principal, elementos estruturais)
- **Verde médio**: `#3DA63A` (destaques, CTAs, alertas positivos)
- **Preto**: `#1A1A1A` (textos, fundos escuros)
- **Branco**: `#FFFFFF` (backgrounds, textos claros)

### Tema Futurista
- Conectores visuais entre seções (linhas, setas).
- Ícones SVG minimalistas para variáveis (temperatura, chuva, vento).
- Tipografia moderna (sans-serif, ex: Roboto, Inter).
- Efeito de "glow" em elementos críticos (alertas).
- Microinterações (hover, feedback visual).

---

## 8. PRÓXIMOS PASSOS

1. **Configuração OAuth2 Gmail**: Gerar credenciais na Google Cloud Console.
2. **Preparar shapefiles**: Adicionar fazendas em `shapefiles/`.
3. **Implementar coleta**: Open-Meteo → GOES → NASA POWER.
4. **Processamento**: Agregação, cálculo ETo, alertas.
5. **PDF + Streamlit**: Geração de relatórios.
6. **Teste end-to-end**: Executar pipeline completo.
7. **GitHub Actions**: Agendar cron diário.
8. **Produção**: Deploy de Streamlit (ex: Streamlit Cloud, AWS Lambda).

---

## 9. REFERÊNCIAS

- **Open-Meteo**: https://open-meteo.com/
- **GOES-16/19**: https://aws.amazon.com/public-datasets/goes/
- **NASA POWER**: https://power.larc.nasa.gov/
- **Geopandas**: https://geopandas.org/
- **Streamlit**: https://streamlit.io/
- **ReportLab**: https://www.reportlab.com/
- **Gmail API**: https://developers.google.com/gmail/api

---

**Versão**: 1.0  
**Data**: 2026-05-17  
**Mantido por**: Yamada Engenharia
