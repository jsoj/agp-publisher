import React from 'react';
import { Send, FileText, PlusCircle, CheckCircle, Users, BellRing, Sparkles } from 'lucide-react';

export default function PublicadorPortalPage() {
  return (
    <main className="min-h-screen bg-[#061325] text-slate-100 p-4 md:p-8 space-y-6">
      {/* HEADER RESPONSIVO */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#0c2340] to-[#0f5132] border border-[#c99a2c]/50 flex items-center justify-center text-[#c99a2c] shadow-lg">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <span className="text-[10px] font-extrabold uppercase tracking-widest text-[#c99a2c]">Portal do Publicador</span>
            <h1 className="text-xl font-bold text-white">Gestão Editorial & Envio de Boletins</h1>
          </div>
        </div>
        <button className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-[#0f5132] to-[#13653f] hover:brightness-110 text-white text-xs font-bold shadow-lg transition-all">
          <PlusCircle className="w-4 h-4" />
          Novo Boletim
        </button>
      </div>

      {/* CARDS DE AÇÃO */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Card Dólar */}
        <div className="bg-[#0c2340]/60 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="px-2.5 py-1 text-[10px] font-extrabold rounded-full bg-emerald-950/80 text-emerald-400 border border-emerald-700">
              ECONOMIA & CÂMBIO
            </span>
            <span className="text-xs text-slate-400 font-semibold">2x ao dia (Dias Úteis)</span>
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">Boletim Diário de Câmbio & Mercado</h2>
            <p className="text-xs text-slate-300 mt-1">
              Disparos automáticos às 11:00 (Abertura) e 17:15 (Fechamento) via WhatsApp, Newsletter HTML e SharePoint.
            </p>
          </div>
          <div className="bg-[#061325]/80 rounded-xl p-3.5 border border-slate-800 flex items-center justify-between">
            <div>
              <div className="text-[10px] text-slate-400 font-bold uppercase">Última Cotação Enviada</div>
              <div className="text-xl font-extrabold text-white">R$ 5,1440 <span className="text-xs text-emerald-400 font-bold">-0,93%</span></div>
            </div>
            <button className="px-4 py-2 rounded-lg bg-[#0c2340] hover:bg-slate-800 border border-slate-700 text-xs font-bold text-white transition-all">
              Disparar Manual
            </button>
          </div>
        </div>

        {/* Card IA */}
        <div className="bg-[#0c2340]/60 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="px-2.5 py-1 text-[10px] font-extrabold rounded-full bg-blue-950/80 text-blue-400 border border-blue-700">
              TECNOLOGIA & IA
            </span>
            <span className="text-xs text-slate-400 font-semibold">Diário Matinal (08:00)</span>
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">Boletim I.A. Nível 01</h2>
            <p className="text-xs text-slate-300 mt-1">
              Compilado diário com as principais inovações em Inteligência Artificial, PDF A4 diagramado e envio para grupos.
            </p>
          </div>
          <div className="bg-[#061325]/80 rounded-xl p-3.5 border border-slate-800 flex items-center justify-between">
            <div>
              <div className="text-[10px] text-slate-400 font-bold uppercase">Edição Atual</div>
              <div className="text-xl font-extrabold text-white">Edição #143 <span className="text-xs text-slate-400 font-normal">PDF Gerado</span></div>
            </div>
            <button className="px-4 py-2 rounded-lg bg-[#0c2340] hover:bg-slate-800 border border-slate-700 text-xs font-bold text-white transition-all">
              Baixar PDF
            </button>
          </div>
        </div>
      </div>
    </main>
  );
}
