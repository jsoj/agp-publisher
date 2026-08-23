from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import json

from registry.db import get_db, init_db
from engines.whatsapp_engine import WhatsAppEngine
from engines.email_engine import EmailEngine
from engines.pdf_engine import PDFEngine
from templates.html_template import render_dolar_newsletter
from templates.ai_bulletin_template import render_ai_bulletin_html

app = FastAPI(
    title="AGP Publisher Core API",
    description="Plataforma de Publicação Autônoma Multi-Canal (B2B2C)",
    version="2.0.0"
)

wa_engine = WhatsAppEngine()
email_engine = EmailEngine()

class SubscriberCreate(BaseModel):
    tenant_id: str
    bulletin_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    preferred_channels: List[str]

class DispatchDolarRequest(BaseModel):
    cotacao: str
    variacao: str
    min_val: str
    max_val: str
    date_str: str
    items: List[dict]
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/health")
async def health_check():
    return {"status": "ok", "app": "agp-publisher-core", "version": "2.0.0"}

@app.get("/bulletins")
async def list_bulletins():
    db = await get_db()
    try:
        async with db.execute("SELECT * FROM bulletins WHERE is_active = 1") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    finally:
        await db.close()

@app.post("/subscribers")
async def add_subscriber(sub: SubscriberCreate):
    db = await get_db()
    try:
        await db.execute("""
            INSERT INTO subscribers (tenant_id, bulletin_id, name, email, phone_number, preferred_channels)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (sub.tenant_id, sub.bulletin_id, sub.name, sub.email, sub.phone_number, json.dumps(sub.preferred_channels)))
        await db.commit()
        return {"status": "success", "message": "Assinante cadastrado com sucesso!"}
    finally:
        await db.close()

@app.post("/dispatch/dolar")
async def dispatch_dolar_report(payload: DispatchDolarRequest, bg_tasks: BackgroundTasks):
    """Dispara o Boletim do Dólar para os canais cadastrados ou pontuais."""
    
    # 1. Monta HTML e Texto
    html_body = render_dolar_newsletter(
        date_str=payload.date_str,
        cotacao=payload.cotacao,
        variacao=payload.variacao,
        min_val=payload.min_val,
        max_val=payload.max_val,
        items=payload.items
    )
    
    text_sp = f"BOLETIM DO DÓLAR & MERCADO - {payload.date_str}\n\nCOTAÇÃO: {payload.cotacao} ({payload.variacao})\nFaixa: Mín {payload.min_val} | Máx {payload.max_val}\n\nProjeto Brasil 2050"

    results = {}

    # Disparo por e-mail se especificado
    if payload.recipient_email:
        res_html = email_engine.send_html_newsletter(
            payload.recipient_email,
            f"Projeto Brasil 2050 | Boletim Câmbio e Mercado - {payload.date_str}",
            html_body
        )
        res_sp = email_engine.send_sharepoint_text(
            payload.recipient_email,
            f"[SharePoint] Boletim Econômico - {payload.date_str}",
            text_sp
        )
        results["email_html"] = res_html
        results["email_sharepoint"] = res_sp

    # Disparo por WhatsApp se especificado
    if payload.recipient_phone:
        wa_text = f"*{payload.cotacao} ({payload.variacao})*\nMínima: {payload.min_val} | Máxima: {payload.max_val}\n\nFechamento do Câmbio - Projeto Brasil 2050."
        res_wa = await wa_engine.send_text(payload.recipient_phone, wa_text)
        results["whatsapp"] = res_wa

    return {"status": "dispatched", "results": results}
