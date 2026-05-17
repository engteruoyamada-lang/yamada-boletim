"""Orquestrador principal do pipeline Yamada Engenharia"""
import logging
from datetime import datetime
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Executa o pipeline completo de geração e entrega de boletins"""

    logger.info("=" * 60)
    logger.info("🌾 INICIANDO PIPELINE YAMADA ENGENHARIA")
    logger.info(f"Data/Hora: {datetime.now().isoformat()}")
    logger.info("=" * 60)

    try:
        # 1. Validação de configuração
        from src.utils.config import validate_config
        if not validate_config():
            logger.error("❌ Configuração inválida. Abortando.")
            return False

        logger.info("✓ Configuração validada")

        # 2. Coleta de dados
        logger.info("📊 Etapa 1: Coleta de dados...")
        from src.coleta.open_meteo import coletar_open_meteo
        from src.coleta.nasa_power import coletar_nasa_power
        # from src.coleta.goes import coletar_goes  # Implementar depois

        dados_openmeteo = coletar_open_meteo()
        dados_nasa = coletar_nasa_power()
        logger.info("✓ Coleta de dados concluída")

        # 3. Processamento e agregação
        logger.info("⚙️  Etapa 2: Processamento...")
        from src.processamento.aggregador import processar_dados

        boletins = processar_dados(dados_openmeteo, dados_nasa)
        logger.info(f"✓ Processamento concluído ({len(boletins)} boletins gerados)")

        # 4. Geração de PDF
        logger.info("📄 Etapa 3: Geração de PDFs...")
        from src.relatorio.pdf_generator import gerar_pdfs

        pdfs = gerar_pdfs(boletins)
        logger.info(f"✓ PDFs gerados ({len(pdfs)} arquivos)")

        # 5. Envio de emails
        logger.info("📧 Etapa 4: Envio de emails...")
        from src.entrega.email_sender import enviar_boletins

        enviados = enviar_boletins(boletins, pdfs)
        logger.info(f"✓ Emails enviados ({enviados} mensagens)")

        logger.info("=" * 60)
        logger.info("✅ PIPELINE CONCLUÍDO COM SUCESSO")
        logger.info("=" * 60)
        return True

    except Exception as e:
        logger.error(f"❌ ERRO NO PIPELINE: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
