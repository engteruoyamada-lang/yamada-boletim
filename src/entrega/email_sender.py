"""Entrega via Gmail API (OAuth2)

Funcionalidades:
- Composição de email com resumo em Markdown
- Anexação de PDF
- Envio via Gmail API
"""
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def enviar_boletins(boletins, pdfs):
    """
    Envia boletins via Gmail para produtores

    Args:
        boletins: Lista de dicts com dados dos boletins
        pdfs: Lista de caminhos dos PDFs gerados

    Returns:
        int: Número de emails enviados com sucesso
    """
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email import encoders
    from src.utils.config import GMAIL_SENDER_EMAIL, RECIPIENT_EMAILS

    logger.info("📧 Enviando boletins por email...")

    # TODO: Implementar
    # 1. Autenticar com Google API (OAuth2)
    # 2. Para cada boletim:
    #    a) Composição do email (corpo em Markdown)
    #    b) Anexação do PDF correspondente
    #    c) Envio via Gmail API
    # 3. Tratar erros de envio

    enviados = 0

    try:
        # Placeholder: retorna 0 por enquanto
        logger.info(f"✓ {enviados} emails enviados com sucesso")
        return enviados

    except Exception as e:
        logger.error(f"❌ Erro ao enviar emails: {e}")
        raise

def compor_corpo_email(boletim):
    """
    Compõe corpo do email em Markdown

    Estrutura:
    - Resumo executivo
    - Variáveis principais (tabela)
    - Alertas destacados
    - Recomendações
    - Link para Streamlit
    """
    corpo = f"""
# Boletim Meteorológico - {boletim['data_geracao']}

## 🌾 {boletim['fazenda']}

### Resumo Executivo
{boletim.get('resumo_executivo', '')}

### Variáveis Principais

| Variável | Valor | Unidade |
|----------|-------|--------|
| Temperatura Máx | {boletim['temperatura']['max']} | °C |
| Temperatura Mín | {boletim['temperatura']['min']} | °C |
| Precipitação | {boletim['precipitacao']['prevista']} | mm |
| Umidade Relativa | {boletim['umidade']} | % |
| Velocidade do Vento | {boletim['vento']['velocidade']} | m/s |
| Evapotranspiração | {boletim['eto']} | mm/dia |

### ⚠️ Alertas
{_formatar_alertas(boletim.get('alertas', []))}

---
*Boletim gerado automaticamente por Yamada Engenharia*
*Acesse o dashboard em: [Streamlit App](http://localhost:8501)*
"""
    return corpo

def _formatar_alertas(alertas):
    """Formata lista de alertas em Markdown"""
    if not alertas:
        return "✅ Nenhum alerta crítico"

    texto = ""
    for alerta in alertas:
        emoji = "🔴" if alerta["severidade"] == "alta" else "🟡"
        texto += f"\n{emoji} **{alerta['tipo']}**: {alerta['descricao']}"
    return texto
