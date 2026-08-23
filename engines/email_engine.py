import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailEngine:
    """Motor de envio de e-mails via Mailcow Postfix local (IPv4) com suporte a HTML e Texto."""
    def __init__(self, smtp_host: str = "127.0.0.1", smtp_port: int = 25, default_sender: str = "relatorios@projetobrasil2050.site"):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.default_sender = default_sender

    def send_sharepoint_text(self, recipient: str, subject: str, text_body: str, sender: str = None) -> bool:
        from_email = sender or self.default_sender
        msg = MIMEMultipart()
        msg['From'] = f"Projeto Brasil 2050 <{from_email}>"
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.sendmail(from_email, [recipient], msg.as_string())
            return True
        except Exception as e:
            print(f"❌ [EmailEngine Text Error]: {e}")
            return False

    def send_html_newsletter(self, recipient: str, subject: str, html_body: str, sender: str = None) -> bool:
        from_email = sender or self.default_sender
        msg = MIMEText(html_body, 'html', 'utf-8')
        msg['From'] = f"Projeto Brasil 2050 <{from_email}>"
        msg['To'] = recipient
        msg['Subject'] = subject
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.sendmail(from_email, [recipient], msg.as_string())
            return True
        except Exception as e:
            print(f"❌ [EmailEngine HTML Error]: {e}")
            return False
