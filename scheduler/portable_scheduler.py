import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from engines.whatsapp_engine import WhatsAppEngine
from engines.email_engine import EmailEngine
from templates.html_template import render_dolar_newsletter

scheduler = AsyncIOScheduler()
wa_engine = WhatsAppEngine()
email_engine = EmailEngine()

async def job_dolar_morning():
    """Boletim Matinal de Abertura do Câmbio - 11:00 (Dias Úteis)"""
    print("⏰ [Scheduler] Disparando Boletim do Dólar (Abertura - 11:00)...")

async def job_dolar_evening():
    """Boletim de Fechamento do Câmbio - 17:15 (Dias Úteis)"""
    print("⏰ [Scheduler] Disparando Boletim do Dólar (Fechamento - 17:15)...")

def start_scheduler():
    # Segunda a Sexta às 11:00
    scheduler.add_job(job_dolar_morning, CronTrigger(day_of_week='mon-fri', hour=11, minute=0, timezone='America/Sao_Paulo'), id='dolar_morning')
    # Segunda a Sexta às 17:15
    scheduler.add_job(job_dolar_evening, CronTrigger(day_of_week='mon-fri', hour=17, minute=15, timezone='America/Sao_Paulo'), id='dolar_evening')
    scheduler.start()
    print("🚀 [Portable Scheduler] Agendador APScheduler iniciado para dias úteis (11:00 e 17:15 BRT).")

if __name__ == "__main__":
    start_scheduler()
    asyncio.get_event_loop().run_forever()
