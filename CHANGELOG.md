# Changelog & Marco de Maturidade (Golden Baseline)

Todas as alterações notáveis deste projeto serão documentadas neste arquivo.

## [v3.0.0-stable-ai-bulletin] - 2026-10-07

### 🎯 Marco de Maturidade (Baseline de Ouro)
Esta versão consolida a estabilidade operacional definitiva do microserviço **Boletim I.A. — Nível 01**, resolvendo em definitivo problemas reincidentes de datas defasadas, quebras de formatação JSON e links quebrados (erros 404).

### ✨ Novas Funcionalidades e Blindagens
- **Mapeador Determinístico de Citações:** Proibição estrita de alucinação de URLs por parte da LLM. O modelo referencia apenas marcadores estruturados `[FONTE_X]`, os quais são substituídos programaticamente pelas URLs canônicas em tempo de execução.
- **Validador Ativo Anti-404 (`link_validator.py`):** Health-check HTTP assíncrono em paralelo (`HEAD` com fallback para `GET stream`) que resolve redirecionamentos protegidos do Google Search Grounding e descarta qualquer URL com status `>= 400` antes do envio.
- **Sanity Check Pré-Disparo:** O executor `run_ai_bulletin_agent.py` valida a integridade do artigo e do áudio, impedindo disparos vazios ou com tags não substituídas.
- **Suíte de Testes Automatizados (`tests/test_ai_bulletin_pipeline.py`):** 6 testes cobrindo validação de links, deduplicação em SQLite (janela estrita de 24h), integridade de roteiro de áudio da Francisca e substituição de tags.

### 🛡️ Procedimento de Rollback
Caso qualquer alteração futura desestabilize a rotina do Boletim de IA, execute imediatamente:
```bash
git checkout v3.0.0-stable-ai-bulletin
```
