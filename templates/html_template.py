def render_dolar_newsletter(date_str: str, cotacao: str, variacao: str, min_val: str, max_val: str, items: list[dict]) -> str:
    """Gera HTML responsivo da Newsletter Projeto Brasil 2050."""
    items_html = ""
    for i, it in enumerate(items, 1):
        items_html += f"""
        <div style="margin-bottom: 20px;">
          <h3 style="font-size: 15px; font-weight: 700; color: #061325; margin: 0 0 6px 0;">
            {i}. {it['title']}
          </h3>
          <p style="font-size: 14px; line-height: 1.6; color: #334155; margin: 0 0 6px 0;">
            {it['description']}
          </p>
          <a href="{it['url']}" target="_blank" style="color: #0c2340; font-size: 13px; font-weight: 600; text-decoration: underline;">
            Fonte: {it['source']} &rarr;
          </a>
        </div>
        """

    return f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="pt-BR">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Projeto Brasil 2050 - Boletim Econômico</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #f8fafc; padding: 30px 15px;">
    <tr>
      <td align="center">
        <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width: 600px; width: 100%; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 25px rgba(6, 19, 37, 0.08); border: 1px solid #e2e8f0;">
          <tr>
            <td style="background-color: #061325; background: linear-gradient(135deg, #061325 0%, #0c2340 60%, #0a332c 100%); padding: 35px 30px; text-align: center;">
              <div style="color: #c99a2c; font-size: 11px; font-weight: 700; letter-spacing: 2.5px; text-transform: uppercase; margin-bottom: 8px;">
                PROJETO BRASIL 2050 &bull; RELATÓRIO EXECUTIVO
              </div>
              <h1 style="color: #ffffff; font-size: 23px; font-weight: 700; margin: 0 0 8px 0; letter-spacing: -0.5px; line-height: 1.3;">
                Boletim Diário de Câmbio & Mercado
              </h1>
              <p style="color: #cbd5e1; font-size: 13px; margin: 0;">
                {date_str}
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding: 28px 30px 15px 30px;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #f1f5f9; border-left: 5px solid #0f5132; border-radius: 8px; padding: 22px 24px;">
                <tr>
                  <td>
                    <span style="color: #64748b; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.2px; display: block; margin-bottom: 6px;">
                      DÓLAR COMERCIAL (USD/BRL) &bull; FECHAMENTO
                    </span>
                    <div style="font-size: 38px; font-weight: 800; color: #061325; line-height: 1.1; margin: 8px 0;">
                      {cotacao}
                      <span style="font-size: 16px; font-weight: 700; color: #0f5132; background-color: #d1fae5; padding: 4px 12px; border-radius: 20px; vertical-align: middle; margin-left: 10px; display: inline-block;">
                        {variacao}
                      </span>
                    </div>
                    <p style="color: #475569; font-size: 13px; margin: 8px 0 0 0;">
                      <strong>Faixa do dia:</strong> Mínima {min_val} &bull; Máxima {max_val}
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <tr>
            <td style="padding: 15px 30px 25px 30px;">
              <h2 style="font-size: 16px; font-weight: 700; color: #0c2340; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin: 20px 0 16px 0;">
                Principais Direcionadores do Mercado
              </h2>
              {items_html}
            </td>
          </tr>
          <tr>
            <td style="background-color: #061325; padding: 24px 30px; text-align: center;">
              <div style="color: #c99a2c; font-size: 12px; font-weight: 700; letter-spacing: 1.5px; margin-bottom: 6px;">
                PROJETO BRASIL 2050
              </div>
              <p style="color: #94a3b8; font-size: 12px; margin: 0 0 10px 0; line-height: 1.5;">
                Inteligência de Mercado &bull; Análise Macroeconômica &bull; Visão de Futuro
              </p>
              <p style="color: #64748b; font-size: 11px; margin: 0;">
                Este boletim é informativo. Acesse <a href="https://projetobrasil2050.site" target="_blank" style="color: #cbd5e1; text-decoration: underline;">projetobrasil2050.site</a>
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""
