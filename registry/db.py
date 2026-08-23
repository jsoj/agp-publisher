import aiosqlite
import os
from pathlib import Path

DB_PATH = os.getenv("AGP_DB_PATH", "/root/agp-publisher/data/agp_publisher.db")

async def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode = WAL;")
    await db.execute("PRAGMA foreign_keys = ON;")
    return db

async def init_db():
    db = await get_db()
    try:
        # 1. Tenants (Organizações / Clientes)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS tenants (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            domain TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 2. Bulletins (Configurações dos Boletins)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS bulletins (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            title TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            schedule_cron TEXT NOT NULL,
            channels TEXT NOT NULL, -- JSON array: ['whatsapp', 'email_html', 'email_text', 'pdf']
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        );
        """)

        # 3. Subscribers (Assinantes Multi-Canal)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id TEXT NOT NULL,
            bulletin_id TEXT NOT NULL,
            name TEXT,
            email TEXT,
            phone_number TEXT,
            preferred_channels TEXT NOT NULL, -- JSON array
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tenant_id) REFERENCES tenants (id),
            FOREIGN KEY (bulletin_id) REFERENCES bulletins (id)
        );
        """)

        # 4. Publication Logs (Auditoria & Rastreabilidade)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS publication_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bulletin_id TEXT NOT NULL,
            channel TEXT NOT NULL,
            recipient TEXT NOT NULL,
            status TEXT NOT NULL, -- 'SENT', 'FAILED', 'RETRY'
            payload_summary TEXT,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bulletin_id) REFERENCES bulletins (id)
        );
        """)

        # Popula dados iniciais dos tenants e boletins se vazios
        await db.execute("""
        INSERT OR IGNORE INTO tenants (id, name, domain) 
        VALUES ('brasil2050', 'Projeto Brasil 2050', 'projetobrasil2050.site');
        """)

        await db.execute("""
        INSERT OR IGNORE INTO bulletins (id, tenant_id, title, slug, schedule_cron, channels)
        VALUES 
        ('dolar_report', 'brasil2050', 'Boletim Diário do Câmbio', 'dolar', 'mon-fri:11:00,17:15', '[\"whatsapp\", \"email_html\", \"email_text\"]'),
        ('ai_report', 'brasil2050', 'Boletim I.A. Nível 01', 'ai-level-01', 'daily:08:00', '[\"whatsapp_group\", \"pdf\", \"email_html\"]');
        """)

        await db.commit()
        print("💾 [Database] Banco de dados SQLite Multi-Tenant inicializado com modo WAL!")
    finally:
        await db.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(init_db())
