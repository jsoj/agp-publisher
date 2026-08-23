import React from 'react';
import { Mail, MessageSquare, Check, Sparkles, Shield, Bell } from 'lucide-react';

export default function AssinantePortalPage() {
  return (
    <main className="min-h-screen bg-[#061325] text-slate-100 flex items-center justify-center p-4 md:p-8">
      <div className="w-full max-w-lg bg-[#0c2340]/70 border border-slate-800 rounded-3xl p-6 md:p-8 shadow-2xl space-y-6 relative overflow-hidden backdrop-blur-xl">
        <div className="absolute top-0 right-0 w-32 h-32 bg-[#c99a2c]/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-32 h-32 bg-[#0f5132]/20 rounded-full blur-3xl"></div>

        {/* CABEÇALHO */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-extrabold bg-[#061325] border border-[#c99a2c]/40 text-[#c99a2c] uppercase tracking-widest">
            <Sparkles className="w-3 h-3" /> Projeto Brasil 2050
          </div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">Central do Assinante</h1>
          <p className="text-xs text-slate-300">
            Personalize seus canais e receba inteligência de mercado e tecnologia no seu formato favorito.
          </p>
        </div>

        {/* FORMULÁRIO */}
        <form className="space-y-4">
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-300">Seu Nome Completo</label>
            <input 
              type="text" 
              placeholder="Ex: José Junior" 
              className="w-full bg-[#061325] border border-slate-700 rounded-xl px-4 py-3 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-[#c99a2c] transition-all"
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-300">Seu Melhor E-mail</label>
            <input 
              type="email" 
              placeholder="jose.junior@exemplo.com" 
              className="w-full bg-[#061325] border border-slate-700 rounded-xl px-4 py-3 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-[#c99a2c] transition-all"
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-300">WhatsApp (com DDD)</label>
            <input 
              type="tel" 
              placeholder="(43) 98859-7348" 
              className="w-full bg-[#061325] border border-slate-700 rounded-xl px-4 py-3 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-[#c99a2c] transition-all"
            />
          </div>

          {/* SELEÇÃO DE CANAIS */}
          <div className="space-y-2 pt-2">
            <label className="text-xs font-bold text-slate-300 block">Canais Preferidos de Entrega</label>
            
            <label className="flex items-center gap-3 bg-[#061325]/80 border border-slate-800 rounded-xl p-3 cursor-pointer hover:border-slate-700 transition-all">
              <input type="checkbox" defaultChecked className="rounded accent-[#0f5132] w-4 h-4" />
              <div className="flex-1 text-xs">
                <div className="font-bold text-white flex items-center gap-1.5">
                  <Mail className="w-3.5 h-3.5 text-blue-400" /> Newsletter Executiva HTML
                </div>
                <div className="text-[11px] text-slate-400">Design de redação de banco de investimento</div>
              </div>
            </label>

            <label className="flex items-center gap-3 bg-[#061325]/80 border border-slate-800 rounded-xl p-3 cursor-pointer hover:border-slate-700 transition-all">
              <input type="checkbox" defaultChecked className="rounded accent-[#0f5132] w-4 h-4" />
              <div className="flex-1 text-xs">
                <div className="font-bold text-white flex items-center gap-1.5">
                  <MessageSquare className="w-3.5 h-3.5 text-emerald-400" /> WhatsApp Direto & Áudio
                </div>
                <div className="text-[11px] text-slate-400">Cotação sucinta no topo com 4 casas decimais</div>
              </div>
            </label>
          </div>

          <button 
            type="button" 
            className="w-full py-3.5 rounded-xl bg-gradient-to-r from-[#0f5132] via-[#13653f] to-[#0c2340] text-white text-xs font-bold uppercase tracking-wider shadow-xl hover:brightness-110 transition-all mt-4"
          >
            Salvar Preferências
          </button>
        </form>

        <div className="text-center text-[10px] text-slate-400 flex items-center justify-center gap-1">
          <Shield className="w-3 h-3 text-[#c99a2c]" /> Seus dados estão 100% protegidos com isolamento LGPD
        </div>
      </div>
    </main>
  );
}
