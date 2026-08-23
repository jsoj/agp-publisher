import React from 'react';
import { ShieldCheck, Cpu, Database, Activity, Terminal, RefreshCw, Send, CheckCircle2 } from 'lucide-react';

export default function AdminPortalPage() {
  return (
    <main className="min-h-screen bg-[#061325] text-slate-100 p-4 md:p-8 space-y-6">
      {/* HEADER RESPONSIVO */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#0c2340] to-[#0f5132] border border-[#c99a2c]/50 flex items-center justify-center text-[#c99a2c] shadow-lg">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <span className="text-[10px] font-extrabold uppercase tracking-widest text-[#c99a2c]">Super Admin Core</span>
            <h1 className="text-xl font-bold text-white">Painel Geral de Infraestrutura & Motores</h1>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-950/80 border border-emerald-500/40 text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            Orquestrador VPS 24/7
          </span>
        </div>
      </div>

      {/* METRICAS DO SISTEMA */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-[#0c2340]/60 border border-slate-800 rounded-xl p-4 shadow-md">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
            <span>MEMÓRIA RAM</span>
            <Cpu className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-white">24 GB <span className="text-xs text-slate-400 font-normal">/ 31 GB Livres</span></div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full mt-3 overflow-hidden">
            <div className="bg-emerald-500 h-full w-[25%]"></div>
          </div>
        </div>

        <div className="bg-[#0c2340]/60 border border-slate-800 rounded-xl p-4 shadow-md">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
            <span>BANCO DE DADOS</span>
            <Database className="w-4 h-4 text-[#c99a2c]" />
          </div>
          <div className="text-2xl font-bold text-white">SQLite WAL</div>
          <div className="text-xs text-emerald-400 mt-2 flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" /> Multi-Tenant Ativo
          </div>
        </div>

        <div className="bg-[#0c2340]/60 border border-slate-800 rounded-xl p-4 shadow-md">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
            <span>WHATSAPP EVOLUTION</span>
            <Activity className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-white">Online</div>
          <div className="text-xs text-slate-400 mt-2">Voz Edge-TTS (Francisca)</div>
        </div>

        <div className="bg-[#0c2340]/60 border border-slate-800 rounded-xl p-4 shadow-md">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
            <span>MAILCOW POSTFIX</span>
            <Send className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-white">IPv4 TLS</div>
          <div className="text-xs text-slate-400 mt-2">projetobrasil2050.site</div>
        </div>
      </div>

      {/* CONTROLE DOS MOTORES */}
      <div className="bg-[#0c2340]/40 border border-slate-800 rounded-xl p-5 shadow-lg space-y-4">
        <h2 className="text-sm font-bold text-white uppercase tracking-wider text-[#c99a2c] flex items-center gap-2">
          <Terminal className="w-4 h-4" />
          Status dos Agendamentos & Disparos Automáticos
        </h2>
        <div className="divide-y divide-slate-800">
          <div className="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <div className="text-sm font-bold text-white">Boletim Câmbio & Dólar (Abertura 11:00 / Fechamento 17:15)</div>
              <div className="text-xs text-slate-400">Canais: WhatsApp PTT, E-mail HTML, SharePoint Texto</div>
            </div>
            <span className="px-3 py-1 text-xs font-semibold rounded bg-emerald-950 text-emerald-400 border border-emerald-800 w-fit">
              APScheduler Ativo
            </span>
          </div>
          <div className="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <div className="text-sm font-bold text-white">Boletim I.A. Nível 01 (Matinal 08:00)</div>
              <div className="text-xs text-slate-400">Canais: WhatsApp Grupo, PDF A4 Diagramado, Newsletter HTML</div>
            </div>
            <span className="px-3 py-1 text-xs font-semibold rounded bg-emerald-950 text-emerald-400 border border-emerald-800 w-fit">
              APScheduler Ativo
            </span>
          </div>
        </div>
      </div>
    </main>
  );
}
