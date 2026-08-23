import React from 'react';
import { Radio, Send, Users, FileText, CheckCircle2, Clock } from 'lucide-react';

export default function DashboardPage() {
  return (
    <main className="min-h-screen bg-[#061325] text-slate-100 flex flex-col">
      {/* HEADER INSTITUCIONAL */}
      <header className="border-b border-slate-800 bg-[#081b33]/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-18 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-[#0c2340] to-[#0f5132] border border-[#c99a2c]/40 flex items-center justify-center font-bold text-[#c99a2c] shadow-md">
              2050
            </div>
            <div>
              <span className="text-xs font-bold uppercase tracking-widest text-[#c99a2c] block">
                Projeto Brasil 2050
              </span>
              <h1 className="text-sm font-semibold text-slate-200">
                Plataforma Autônoma de Publicação (AGP Publisher)
              </h1>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-950/60 border border-emerald-500/30 text-emerald-400">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              Motores Ativos &bull; 24/7
            </span>
          </div>
        </div>
      </header>

      {/* CONTEÚDO PRINCIPAL */}
      <div className="max-w-7xl mx-auto px-6 py-8 flex-1 w-full space-y-8">
        
        {/* CARDS DE STATUS */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div className="bg-[#0c2340]/60 border border-slate-800 rounded-xl p-5 shadow-lg relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-[#c99a2c]/5 rounded-full blur-2xl"></div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Boletins Registrados</span>
              <FileText className="w-5 h-5 text-[#c99a2c]" />
            </div>
            <div className="text-3xl font-extrabold text-white">2 Ativos</div>
            <div className="text-xs text-slate-400 mt-2">Dólar & Mercado &bull; I.A. Nível 01</div>
          </div>

          <div className="bg-[#0c2340]/60 border border-slate-800 rounded-xl p-5 shadow-lg relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/5 rounded-full blur-2xl"></div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Canais de Entrega</span>
              <Send className="w-5 h-5 text-emerald-400" />
            </div>
            <div className="text-3xl font-extrabold text-white">4 Canais</div>
            <div className="text-xs text-slate-400 mt-2">WhatsApp PTT, E-mail HTML, SharePoint, PDF</div>
          </div>

          <div className="bg-[#0c2340]/60 border border-slate-800 rounded-xl p-5 shadow-lg relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-blue-500/5 rounded-full blur-2xl"></div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Próximo Disparo</span>
              <Clock className="w-5 h-5 text-blue-400" />
            </div>
            <div className="text-3xl font-extrabold text-white">11:00 BRT</div>
            <div className="text-xs text-slate-400 mt-2">Abertura do Câmbio (Segunda a Sexta)</div>
          </div>
        </div>

        {/* TABELA DE BOLETINS E GESTÃO */}
        <div className="bg-[#0c2340]/40 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
          <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-[#081b33]/40">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Radio className="w-4 h-4 text-[#c99a2c]" />
              Painel de Orquestração dos Boletins
            </h2>
          </div>

          <div className="divide-y divide-slate-800">
            {/* Boletim 1 */}
            <div className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-slate-800/30 transition-colors">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-white">Boletim Diário de Câmbio & Mercado</span>
                  <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-emerald-950 text-emerald-400 border border-emerald-800">PRODUÇÃO</span>
                </div>
                <p className="text-xs text-slate-400">
                  Horários: 11:00 (Abertura) e 17:15 (Fechamento) &bull; Dias Úteis
                </p>
                <div className="flex gap-2 pt-1 text-[11px] text-slate-300">
                  <span className="bg-[#061325] px-2 py-0.5 rounded border border-slate-700">WhatsApp Evolution</span>
                  <span className="bg-[#061325] px-2 py-0.5 rounded border border-slate-700">E-mail HTML 2050</span>
                  <span className="bg-[#061325] px-2 py-0.5 rounded border border-slate-700">SharePoint Texto</span>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <button className="px-4 py-2 text-xs font-semibold rounded-lg bg-[#0f5132] hover:bg-[#13653f] text-white transition-all shadow-md">
                  Disparar Agora
                </button>
              </div>
            </div>

            {/* Boletim 2 */}
            <div className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-slate-800/30 transition-colors">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-white">Boletim I.A. Nível 01</span>
                  <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-emerald-950 text-emerald-400 border border-emerald-800">PRODUÇÃO</span>
                </div>
                <p className="text-xs text-slate-400">
                  Horário: 08:00 BRT &bull; Diário Matinal
                </p>
                <div className="flex gap-2 pt-1 text-[11px] text-slate-300">
                  <span className="bg-[#061325] px-2 py-0.5 rounded border border-slate-700">WhatsApp Grupo (@g.us)</span>
                  <span className="bg-[#061325] px-2 py-0.5 rounded border border-slate-700">PDF Diagramado A4</span>
                  <span className="bg-[#061325] px-2 py-0.5 rounded border border-slate-700">Newsletter HTML</span>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <button className="px-4 py-2 text-xs font-semibold rounded-lg bg-[#0f5132] hover:bg-[#13653f] text-white transition-all shadow-md">
                  Disparar Agora
                </button>
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* FOOTER */}
      <footer className="border-t border-slate-800/80 py-4 text-center text-xs text-slate-500">
        Projeto Brasil 2050 &bull; Ecossistema de Publicação Autônoma B2B2C &bull; VPS Hostinger
      </footer>
    </main>
  );
}
