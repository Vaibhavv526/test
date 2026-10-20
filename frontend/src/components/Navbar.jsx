import React from 'react';
import { Sparkles, Heart, Users, PlayCircle, BarChart3, Bot, ShieldCheck } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, systemStatus }) {
  const tabs = [
    { id: 'intake', label: 'Intake & Seed', icon: Bot, badge: null },
    { id: 'profiles', label: 'Candidate Profiles', icon: Users, badge: systemStatus?.stats?.total_profiles },
    { id: 'dates', label: 'Date Simulator', icon: PlayCircle, badge: systemStatus?.stats?.simulated_dates || null },
    { id: 'rankings', label: 'Compatibility Rankings', icon: BarChart3, badge: null },
  ];

  const hasApiKey = systemStatus?.llm_engine?.has_api_key;
  const modelName = systemStatus?.llm_engine?.model || 'claude-3-5-sonnet';

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <div 
            className="flex items-center gap-3 cursor-pointer group"
            onClick={() => setActiveTab('intake')}
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-rose-500 via-pink-500 to-violet-600 p-[1.5px] glow-rose group-hover:scale-105 transition-transform">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <Heart className="w-5 h-5 text-rose-400 fill-rose-500/20 group-hover:fill-rose-500 transition-colors" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold tracking-tight text-white font-heading">
                  Aura<span className="text-gradient-rose">Match</span>
                </span>
                <span className="text-[10px] font-mono uppercase tracking-widest px-1.5 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20">
                  Agentic AI
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block">
                Simulating romantic chemistry with Claude agents
              </p>
            </div>
          </div>

          {/* Nav Tabs */}
          <nav className="flex items-center space-x-1 sm:space-x-2">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-3 sm:px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 relative ${
                    isActive
                      ? 'bg-rose-500/15 text-rose-400 border border-rose-500/30 shadow-sm'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800/60 border border-transparent'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-rose-400' : 'text-slate-400'}`} />
                  <span className="hidden md:inline">{tab.label}</span>
                  {tab.badge !== null && tab.badge !== undefined && (
                    <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded-full ${
                      isActive ? 'bg-rose-500/30 text-rose-300' : 'bg-slate-800 text-slate-400'
                    }`}>
                      {tab.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>

          {/* Engine Status Pill */}
          <div className="hidden lg:flex items-center gap-2 pl-3 border-l border-slate-800">
            <div className="flex items-center gap-2 px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-xs">
              <span className={`w-2 h-2 rounded-full ${hasApiKey ? 'bg-emerald-400 animate-pulse' : 'bg-violet-400'}`} />
              <span className="text-slate-400 font-mono text-[11px]">
                {hasApiKey ? 'Live Claude' : 'Simulation Mode'}
              </span>
              <span className="text-slate-500 text-[10px]">({modelName.replace('claude-3-5-', '')})</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
