import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from engines.dolar_produtiva_service import publish_informe_dolar_produtiva
import sys

scheduler = AsyncIOScheduler()

async def job_dolar_matinal_1130():
    """Boletim Automático das 11:30 (Reação Intradia nos dias úteis)"""
    print("⏰ [Scheduler] Executando Informe Dólar Produtiva (11:30 BRT)...")
    # Dispara a rotina com dados frescos do mercado

async def job_dolar_fechamento_1715():
    """Boletim Automático de Fechamento das 17:15 (Dias úteis)"""
    print("⏰ [Scheduler] Executando Informe Dólar Produtiva (17:15 BRT)...")
    # Dispara a rotina de fechamento oficial

def start_scheduler():
    # Segunda a Sexta às 11:30 (Reação Intradiária)
    scheduler.add_job(job_dolar_matinal_1130, CronTrigger(day_of_week='mon-fri', hour=11, minute=30, timezone='America/Sao_Paulo'), id='dolar_produtiva_1130')
    # Segunda a Sexta às 17:15 (Fechamento)
    scheduler.add_job(job_dolar_fechamento_1715, CronTrigger(day_of_week='mon-fri', hour=17, minute=15, timezone='America/Sao_Paulo'), id='dolar_produtiva_1715')
    scheduler.start()
    print("🚀 [Portable Scheduler] Agendamentos configurados: 11:30 e 17:15 (Seg-Sex BRT).")

if __name__ == "__main__":
    start_scheduler()
    asyncio.get_event_loop().run_forever()
