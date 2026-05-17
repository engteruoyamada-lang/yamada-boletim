"""Carregamento de configurações e variáveis de ambiente"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Carrega .env
ENV_PATH = Path(__file__).parent.parent.parent / ".env"
load_dotenv(ENV_PATH)

# Gmail
GMAIL_SENDER_EMAIL = os.getenv("GMAIL_SENDER_EMAIL", "")
GMAIL_CREDENTIALS_PATH = os.getenv("GMAIL_CREDENTIALS_PATH", "secrets/gmail_credentials.json")
RECIPIENT_EMAILS = os.getenv("RECIPIENT_EMAILS", "").split(";")

# Streamlit
STREAMLIT_USER = os.getenv("STREAMLIT_USER", "Yamada")
STREAMLIT_PASSWORD = os.getenv("STREAMLIT_PASSWORD", "Yamada")

# APIs Públicas
OPEN_METEO_API_URL = os.getenv("OPEN_METEO_API_URL", "https://api.open-meteo.com/v1/forecast")
NASA_POWER_API_URL = os.getenv("NASA_POWER_API_URL", "https://power.larc.nasa.gov/api/v1/")
AWS_REGION = os.getenv("AWS_REGION", "us-west-2")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Caminhos
PROJECT_ROOT = Path(__file__).parent.parent.parent
ASSETS_PATH = PROJECT_ROOT / "assets"
LOGO_PATH = ASSETS_PATH / "logo" / "yamada_logo.png"
SHAPEFILES_PATH = PROJECT_ROOT / "shapefiles"
SECRETS_PATH = PROJECT_ROOT / "secrets"

# Verificações de integridade
def validate_config():
    """Valida se todas as configurações necessárias estão presentes"""
    errors = []

    if not GMAIL_SENDER_EMAIL:
        errors.append("GMAIL_SENDER_EMAIL não está configurado")

    if not Path(GMAIL_CREDENTIALS_PATH).exists():
        errors.append(f"Credenciais Gmail não encontradas em {GMAIL_CREDENTIALS_PATH}")

    if not LOGO_PATH.exists():
        errors.append(f"Logo não encontrado em {LOGO_PATH}")

    if not any(SHAPEFILES_PATH.glob("*.shp")):
        errors.append(f"Nenhum shapefile encontrado em {SHAPEFILES_PATH}")

    if errors:
        for error in errors:
            print(f"⚠️  {error}")
        print("\n📖 Veja .env.example para configuração completa")
        return False

    return True
