Arquitetura e Engenharia de Prompt (AGP)
1. Fluxo de Execução (Pipeline de Processamento)
O sistema foi desenhado em uma arquitetura orientada a tarefas sequenciais rigorosas, permitindo fail-fast (falhar rápido) caso alguma etapa não atenda aos critérios de qualidade.
Coleta com Grounding (DailyCollector): Dispara consultas à API do Gemini buscando lançamentos de modelos, novas aplicações e novidades do mundo Open Source em IA. O objetivo não é gerar um texto bonito, mas sim extrair fatos puros, links e referências do dia.
Redação Sênior (ExecutiveSummarizer - Agent 1): Transforma os dados brutos em um relatório técnico/narrativo focado em IA. Inclui o cabeçalho obrigatório (I.A. Nível 01, Nome/Telefone, Link do WhatsApp e Data de hoje), e lista referências.
Auditoria Factual e Gramatical (ExecutiveSummarizer - Agent 2): Lê o rascunho do Agente 1. Corrige gramática, garante que o cabeçalho "I.A. Nível 01" e as fontes estão intactos, remove cabeçalhos de email ("De/Para") e aplica a frase final obrigatória.
Geração de PDF (PDFGenerator): Converte o Markdown validado em HTML e renderiza em PDF utilizando a biblioteca xhtml2pdf.
Publicação (WhatsAppPublisher): Via requisição HTTP multipart, envia o arquivo PDF gerado diretamente para a API (como Evolution API).
2. Padrões Estéticos do PDF
Tipografia: Helvetica ou Arial para corpo de texto e títulos.
Estrutura: - Fundo branco.
Texto #333333 (Grafite Escuro) e títulos em #1E3A8A (Azul Escuro).
Fonte base 14px com espaçamento de linhas (line-height) 1.5. Margens de página padrão A4 retrato (margin: 2cm).

3. Prompts Core
Prompt do Auditor Factual (Multi-Agent Loop)
"Você é um Revisor e Auditor Sênior Rigoroso.
Sua tarefa é analisar o texto abaixo.
Regras absolutas que causarão falha crítica se não cumpridas:
1. NUNCA inicie uma frase ou parágrafo com o pronome oblíquo "Me", "Te", "Se", "Nos" ou "Vos".
2. Mantenha todas as fontes, links de referências e citações. É vital que as fontes apareçam no documento final.
3. Mantenha os cabeçalhos exatos: "# I.A. Nível 01", o subtítulo de telefone e a Data. NUNCA adicione blocos como "De/Para".
4. O relatório DEVE terminar OBRIGATORIAMENTE com a seguinte frase exata e isolada no final: 'Até a próxima edição.'
Devolva apenas o texto final revisado em formato Markdown."
