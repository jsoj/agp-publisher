import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from engines.dolar_produtiva_service import publish_informe_dolar_produtiva
from engines.ai_bulletin_service import publish_informe_ia
import sys

scheduler = AsyncIOScheduler()

async def job_ai_bulletin_0800():
    """Boletim Diário I.A. Nível 01 - 08:00 BRT (Todos os dias)"""
    print("⏰ [Scheduler] Executando Boletim I.A. — Nível 01 (08:00 BRT)...")

async def job_dolar_matinal_1130():
    """Informe Dólar Produtiva - 11:30 BRT (Seg-Sex)"""
    print("⏰ [Scheduler] Executando Informe Dólar Produtiva (11:30 BRT)...")

async def job_dolar_fechamento_1715():
    """Informe Dólar Produtiva - 17:15 BRT (Seg-Sex)"""
    print("⏰ [Scheduler] Executando Informe Dólar Produtiva (17:15 BRT)...")

def start_scheduler():
    # 1. Boletim I.A. Nível 01 (Diário às 08:00 da manhã)
    scheduler.add_job(job_ai_bulletin_0800, CronTrigger(hour=8, minute=0, timezone='America/Sao_Paulo'), id='ai_bulletin_0800')
    
    # 2. Informe Dólar Produtiva (Seg-Sex às 11:30 e 17:15)
    scheduler.add_job(job_dolar_matinal_1130, CronTrigger(day_of_week='mon-fri', hour=11, minute=30, timezone='America/Sao_Paulo'), id='dolar_produtiva_1130')
    scheduler.add_job(job_dolar_fechamento_1715, CronTrigger(day_of_week='mon-fri', hour=17, minute=15, timezone='America/Sao_Paulo'), id='dolar_produtiva_1715')
    
    scheduler.start()
    print("🚀 [Portable Scheduler] Agendamentos ativos: I.A. (08:00 diário) | Dólar (11:30 e 17:15 Seg-Sex).")

if __name__ == "__main__":
    start_scheduler()
    asyncio.get_event_loop().run_forever()
