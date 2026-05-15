# delivery.py
# Substitui completamente o Twilio + SendGrid pelo Gmail API com OAuth2.
# Envia o PDF como anexo e o resumo executivo no corpo em HTML com identidade Yamada.

import os
import base64
import json
import threading
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime

# Bibliotecas do Google — instaladas via requirements.txt
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ─── Escopo de permissão ──────────────────────────────────────────────────────
# "gmail.send" permite apenas envio — não lê nem apaga e-mails.
# É o escopo mínimo necessário e o mais seguro para este caso de uso.
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# ─── Paleta Yamada (usada no HTML do e-mail) ──────────────────────────────────
VERDE_ESCURO = "#1B4D2E"
VERDE_MEDIO  = "#3DA63A"
PRETO        = "#1A1A1A"


def _carregar_credenciais() -> Credentials:
    """
    Carrega as credenciais OAuth2 do Gmail a partir de variáveis de ambiente.

    No ambiente local de desenvolvimento, você terá um arquivo token.json
    gerado pelo script de autorização inicial (ver instruções abaixo).

    No GitHub Actions, o conteúdo desse token.json é armazenado como Secret
    (GMAIL_TOKEN_JSON) e o conteúdo do credentials.json como outro Secret
    (GMAIL_CREDENTIALS_JSON). Esta função reconstitui ambos em memória.
    """
    # Tenta carregar o token já existente (acesso + refresh token)
    token_json_str = os.environ.get("GMAIL_TOKEN_JSON")

    if not token_json_str:
        # Fallback para desenvolvimento local: lê do arquivo em disco
        token_path = Path("token.json")
        if token_path.exists():
            token_json_str = token_path.read_text()
        else:
            raise FileNotFoundError(
                "Credenciais Gmail não encontradas. "
                "Execute 'python autorizar_gmail.py' localmente primeiro."
            )

    # Desserializa o JSON do token
    token_data = json.loads(token_json_str)
    creds = Credentials.from_authorized_user_info(token_data, SCOPES)

    # Se o access token expirou, renova automaticamente usando o refresh token.
    # O refresh token não expira (a menos que o acesso seja revogado no Google).
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        print("Token Gmail renovado automaticamente.")

        # Atualiza o arquivo local se existir (útil no desenvolvimento)
        token_path = Path("token.json")
        if token_path.exists():
            token_path.write_text(creds.to_json())

    return creds


def _montar_email_html(nome_fazenda: str, resumo: dict, data_ref: str) -> str:
    """
    Monta o corpo HTML do e-mail com identidade visual Yamada.
    Clientes de e-mail têm suporte limitado a CSS — use apenas inline styles.
    """
    situacao    = resumo.get("situacao", "—")
    atencao     = resumo.get("atencao", "—")
    recomendacao = resumo.get("recomendacao", "—")

    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width"></head>
    <body style="margin:0;padding:0;background:#F4F4F4;font-family:Arial,Helvetica,sans-serif;">

      <!-- Wrapper -->
      <table width="100%" cellpadding="0" cellspacing="0" border="0">
        <tr><td align="center" style="padding:24px 12px;">

          <!-- Container principal 600px -->
          <table width="600" cellpadding="0" cellspacing="0" border="0"
                 style="max-width:600px;background:#FFFFFF;border-radius:8px;
                        overflow:hidden;border:1px solid #E0E0E0;">

            <!-- CABEÇALHO com degradê simulado por dois blocos -->
            <tr>
              <td style="background:{VERDE_ESCURO};padding:28px 32px 0;">
                <p style="margin:0;color:#FFFFFF;font-size:22px;
                           font-weight:bold;letter-spacing:1px;">
                  YAMADA ENGENHARIA
                </p>
                <p style="margin:4px 0 0;color:{VERDE_MEDIO};font-size:12px;
                           letter-spacing:2px;">
                  BOLETIM METEOROLÓGICO
                </p>
              </td>
            </tr>
            <tr>
              <td style="background:{VERDE_MEDIO};padding:10px 32px 18px;">
                <p style="margin:0;color:#FFFFFF;font-size:14px;">
                  {nome_fazenda} &nbsp;|&nbsp; {data_ref}
                </p>
              </td>
            </tr>

            <!-- CORPO -->
            <tr>
              <td style="padding:28px 32px;">

                <!-- Seção: Situação do dia -->
                <table width="100%" cellpadding="0" cellspacing="0" border="0"
                       style="margin-bottom:16px;">
                  <tr>
                    <td style="border-left:4px solid {VERDE_MEDIO};
                                padding:12px 16px;background:#F8FFF8;
                                border-radius:0 4px 4px 0;">
                      <p style="margin:0 0 4px;font-size:11px;color:#666666;
                                 text-transform:uppercase;letter-spacing:1px;">
                        Situação do dia
                      </p>
                      <p style="margin:0;font-size:14px;color:{PRETO};
                                 line-height:1.6;">
                        {situacao}
                      </p>
                    </td>
                  </tr>
                </table>

                <!-- Seção: Pontos de atenção -->
                <table width="100%" cellpadding="0" cellspacing="0" border="0"
                       style="margin-bottom:16px;">
                  <tr>
                    <td style="border-left:4px solid #F0A500;
                                padding:12px 16px;background:#FFFDF0;
                                border-radius:0 4px 4px 0;">
                      <p style="margin:0 0 4px;font-size:11px;color:#666666;
                                 text-transform:uppercase;letter-spacing:1px;">
                        Pontos de atenção
                      </p>
                      <p style="margin:0;font-size:14px;color:{PRETO};
                                 line-height:1.6;">
                        {atencao}
                      </p>
                    </td>
                  </tr>
                </table>

                <!-- Seção: Recomendação principal -->
                <table width="100%" cellpadding="0" cellspacing="0" border="0"
                       style="margin-bottom:24px;">
                  <tr>
                    <td style="border-left:4px solid {VERDE_ESCURO};
                                padding:12px 16px;background:#F0F7F0;
                                border-radius:0 4px 4px 0;">
                      <p style="margin:0 0 4px;font-size:11px;color:#666666;
                                 text-transform:uppercase;letter-spacing:1px;">
                        Recomendação principal
                      </p>
                      <p style="margin:0;font-size:14px;color:{PRETO};
                                 line-height:1.6;">
                        <strong>{recomendacao}</strong>
                      </p>
                    </td>
                  </tr>
                </table>

                <!-- Aviso sobre o anexo -->
                <table width="100%" cellpadding="0" cellspacing="0" border="0">
                  <tr>
                    <td style="background:#F4F4F4;border-radius:6px;
                                padding:14px 18px;text-align:center;">
                      <p style="margin:0;font-size:13px;color:#555555;">
                        📎 O relatório completo em PDF está em anexo neste e-mail.
                      </p>
                    </td>
                  </tr>
                </table>

              </td>
            </tr>

            <!-- RODAPÉ -->
            <tr>
              <td style="background:{VERDE_ESCURO};padding:16px 32px;
                          text-align:center;">
                <p style="margin:0;color:#AAAAAA;font-size:11px;
                           font-style:italic;">
                  Engenharia que Constrói. Soluções que Preservam.
                </p>
                <p style="margin:4px 0 0;color:#888888;font-size:10px;">
                  Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')} •
                  Yamada Engenharia
                </p>
              </td>
            </tr>

          </table>
        </td></tr>
      </table>

    </body>
    </html>
    """


def enviar_email_gmail(
    email_destino: str,
    nome_fazenda: str,
    pdf_path: str,
    resumo: dict,
    data_ref: str,
    email_remetente: str = None,
) -> dict:
    """
    Envia o boletim por e-mail usando a Gmail API.

    Parâmetros:
        email_destino   : endereço do cliente
        nome_fazenda    : nome da fazenda (aparece no assunto e no corpo)
        pdf_path        : caminho local do PDF gerado
        resumo          : dict com chaves 'situacao', 'atencao', 'recomendacao'
        data_ref        : string da data, ex: "15/05/2026"
        email_remetente : sua conta Gmail; se None, lê de EMAIL_FROM env var
    """
    if email_remetente is None:
        email_remetente = os.environ.get("EMAIL_FROM", "")
        if not email_remetente:
            raise ValueError("Defina EMAIL_FROM nas variáveis de ambiente.")

    try:
        # ── 1. Carrega credenciais OAuth2 ─────────────────────────────────────
        creds   = _carregar_credenciais()
        service = build("gmail", "v1", credentials=creds)

        # ── 2. Monta a mensagem MIME ──────────────────────────────────────────
        msg = MIMEMultipart("mixed")
        msg["From"]    = email_remetente
        msg["To"]      = email_destino
        msg["Subject"] = (
            f"Boletim Yamada Engenharia — {nome_fazenda} — {data_ref}"
        )

        # Parte HTML (corpo principal)
        html_body = _montar_email_html(nome_fazenda, resumo, data_ref)
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        # Parte do anexo PDF
        pdf_bytes = Path(pdf_path).read_bytes()
        pdf_parte = MIMEApplication(pdf_bytes, _subtype="pdf")
        pdf_nome  = Path(pdf_path).name
        pdf_parte.add_header(
            "Content-Disposition", "attachment", filename=pdf_nome
        )
        msg.attach(pdf_parte)

        # ── 3. Codifica em base64url (exigido pela Gmail API) ─────────────────
        raw_bytes   = msg.as_bytes()
        raw_b64     = base64.urlsafe_b64encode(raw_bytes).decode("utf-8")

        # ── 4. Envia via API ──────────────────────────────────────────────────
        resultado = (
            service.users()
            .messages()
            .send(userId="me", body={"raw": raw_b64})
            .execute()
        )

        print(f"✓ E-mail enviado para {email_destino} | ID: {resultado['id']}")
        return {"status": "ok", "message_id": resultado["id"]}

    except HttpError as e:
        print(f"✗ Erro Gmail API para {email_destino}: {e}")
        return {"status": "erro", "detalhe": str(e)}

    except Exception as e:
        print(f"✗ Erro inesperado ao enviar para {email_destino}: {e}")
        return {"status": "erro", "detalhe": str(e)}


def entregar_para_cliente(cliente: dict, pdf_path: str, dados: dict) -> None:
    """
    Ponto de entrada principal. Recebe um cliente e envia o boletim.

    cliente = {
        "nome":    "Fazenda São João",
        "email":   "gestor@fazenda.com.br",
        "lat":     -22.5,
        "lon":     -47.3,
        "shapefile": "fazenda_sao_joao"  # nome sem extensão, dentro de shapefiles/
    }
    """
    data_ref = datetime.now().strftime("%d/%m/%Y")
    resumo   = dados.get("resumo_executivo", {})

    enviar_email_gmail(
        email_destino   = cliente["email"],
        nome_fazenda    = cliente["nome"],
        pdf_path        = pdf_path,
        resumo          = resumo,
        data_ref        = data_ref,
    )