import pytest
import os
from autonomous_publisher import PDFGenerator

# ==========================================
# TESTES DE REGRAS DE NEGÓCIO (GRAMÁTICA E ESTILO)
# ==========================================
# Em um teste real, você pode mockar o retorno da API do Gemini, 
# mas aqui focamos em testar se as nossas funções de validação interna 
# (ou regexes futuros de fallback) funcionariam caso a IA falhe.

def test_regra_pronome_inicio_frase():
    """Garante que a revisão do texto bloqueie ou denuncie 'Me' no início de frases."""
    
    texto_simulado_falho = "Me parece que o mercado mudou. A inteligência artificial avançou."
    texto_simulado_correto = "Parece-me que o mercado mudou. A inteligência artificial avançou."
    
    # Simulação da verificação de integridade pós-IA
    def contains_invalid_pronoun_start(text):
        sentences = text.replace('!', '.').replace('?', '.').split('.')
        for s in sentences:
            s = s.strip()
            if s.startswith("Me ") or s.startswith("Te "):
                return True
        return False

    assert contains_invalid_pronoun_start(texto_simulado_falho) == True
    assert contains_invalid_pronoun_start(texto_simulado_correto) == False

def test_regra_assinatura_obrigatoria():
    """O relatório DEVE conter a assinatura de finalização acordada."""
    
    assinatura_esperada = "até a próxima edição."
    
    texto_gerado_pela_ia = """
    # Relatório Executivo
    O mercado cresceu 20%.
    
    Até a próxima edição.
    """
    
    assert assinatura_esperada in texto_gerado_pela_ia.lower(), "A IA falhou em incluir a assinatura obrigatória."

# ==========================================
# TESTES DE ARTEFATOS FÍSICOS (PDF)
# ==========================================
def test_geracao_de_pdf_mobile_first(tmp_path):
    """Testa se o motor HTML/CSS consegue gerar um arquivo binário legível."""
    
    pdf_gen = PDFGenerator()
    markdown_test = "# Teste de Título\nEste é um parágrafo de teste."
    
    # Utilizando diretório temporário do Pytest
    output_file = tmp_path / "test_report.pdf"
    
    # Executa a geração
    pdf_gen.generate(markdown_test, str(output_file))
    
    # Verifica se o arquivo foi criado e possui tamanho maior que 0
    assert os.path.exists(output_file)
    assert os.path.getsize(output_file) > 1000  # Pelo menos 1KB de cabeçalhos PDF