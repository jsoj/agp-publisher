import io
import os
from xhtml2pdf import pisa

class PDFEngine:
    """Motor de geração de PDF diagramado para boletins executivos."""

    @staticmethod
    def render_pdf(html_content: str, output_path: str = None) -> bytes | None:
        """Converte HTML com CSS em PDF profissional de alta fidelidade."""
        pdf_buffer = io.BytesIO()
        pisa_status = pisa.CreatePDF(src=html_content, dest=pdf_buffer, encoding='utf-8')

        if pisa_status.err:
            print(f"❌ [PDFEngine Error] Falha na geração do PDF: {pisa_status.err}")
            return None

        pdf_bytes = pdf_buffer.getvalue()
        if output_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(pdf_bytes)
            print(f"📄 [PDFEngine] PDF salvo com sucesso em: {output_path}")

        return pdf_bytes
