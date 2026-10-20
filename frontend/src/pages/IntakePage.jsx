import React, { useState } from 'react';
import { Bot, UserCheck, Sparkles, Send, ShieldAlert, CheckCircle2, RefreshCw, Zap, ArrowRight, Info } from 'lucide-react';
import { api } from '../services/api';

const SAMPLE_BIOS = [
  {
    title: "Venture Architect & Climber",
    name: "Aiden Cross",
    bio: "Founding partner at an early-stage climate tech studio in SF. Weekdays are pitches, unit economics, and clean energy modeling. Weekends: Trad bouldering in Yosemite or tinkering with single-origin pour-overs. I prize radical transparency, self-awareness, and emotional vulnerability. Looking for someone with equal ambition and curiosity who loves spontaneous road trips and quiet reading hours."
  },
  {
    title: "Neuroscientist & Jazz Pianist",
    name: "Dr. Maya Lin",
    bio: "Postdoc researcher mapping hippocampus synaptic plasticity. Outside the brain lab, I play post-bop jazz piano at neighborhood speakeasies and brew kombucha in my kitchen. Deeply allergic to superficial small talk and passive aggression. Need someone who enjoys lively intellectual sparring, deep empathy, and shared quiet mornings."
  },
  {
    title: "Documentary Filmmaker",
    name: "Samir Vance",
    bio: "Freelance investigative filmmaker exploring urban soundscapes and oral histories. Based in Brooklyn with my rescue pitbull mix. Big fan of 35mm film cameras, street tacos at 1 AM, and vinyl record shops. Seeking an authentic, joyful co-pilot who loves honest conversations over wine."
  }
];

export default function IntakePage({ onProfileCreated, onNavigate }) {
  // Intake state
  const [name, setName] = useState('');
  const [bioText, setBioText] = useState('');
  const [loadingIntake, setLoadingIntake] = useState(false);
  const [intakeSuccess, setIntakeSuccess] = useState(null);
  const [intakeError, setIntakeError] = useState('');

  // Synthetic generator state
  const [syntheticCount, setSyntheticCount] = useState(5);
  const [loadingSynthetic, setLoadingSynthetic] = useState(false);
  const [loadingSeed, setLoadingSeed] = useState(false);
  const [syntheticSuccess, setSyntheticSuccess] = useState('');
  const [syntheticError, setSyntheticError] = useState('');

  const handleSampleClick = (sample) => {
    setName(sample.name);
    setBioText(sample.bio);
    setIntakeError('');
    setIntakeSuccess(null);
  };

  const handleSubmitIntake = async (e) => {
    e.preventDefault();
    if (!bioText.trim() || bioText.trim().length < 15) {
      setIntakeError('Please provide at least a couple of sentences of bio text (min 15 characters).');
      return;
    }

    setLoadingIntake(true);
    setIntakeError('');
    setIntakeSuccess(null);

    try {
      const result = await api.submitIntake({
        name: name.trim() || undefined,
        raw_input: bioText.trim(),
        source: 'self-reported',
      });
      setIntakeSuccess(result);
      if (onProfileCreated) onProfileCreated(result);
    } catch (err) {
      setIntakeError(err.message || 'Failed to analyze and create profile.');
    } finally {
      setLoadingIntake(false);
    }
  };

  const handleGenerateSynthetic = async () => {
    setLoadingSynthetic(true);
    setSyntheticError('');
    setSyntheticSuccess('');

    try {
      const results = await api.generateSynthetic(syntheticCount);
      setSyntheticSuccess(`Successfully generated ${results.length} synthetic profiles!`);
      if (onProfileCreated) onProfileCreated();
    } catch (err) {
      setSyntheticError(err.message || 'Failed to generate synthetic profiles.');
    } finally {
      setLoadingSynthetic(false);
    }
  };

  const handleSeedCurated = async () => {
    setLoadingSeed(true);
    setSyntheticError('');
    setSyntheticSuccess('');

    try {
      const res = await api.seedProfiles();
      setSyntheticSuccess(res.message || 'Seeded 25 diverse curated synthetic profiles!');
      if (onProfileCreated) onProfileCreated();
    } catch (err) {
      setSyntheticError(err.message || 'Failed to seed profiles.');
    } finally {
      setLoadingSeed(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-3xl glass-panel p-8 sm:p-10 border border-slate-800">
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-96 h-96 bg-rose-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-1/3 -mb-20 w-80 h-80 bg-violet-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-medium">
            <Sparkles className="w-3.5 h-3.5" />
            Consenting & Synthetic Data Only — Zero Web Scraping
          </div>
          <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white font-heading">
            Teach Your AI Agent <br />
            <span className="text-gradient-rose">How You Truly Date</span>
          </h1>
          <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
            In our agentic dating simulation, your personal AI agent acts on your behalf.
            Paste your bio text to extract your genuine needs, values, and dealbreakers,
            or generate synthetic fictional candidates to experience autonomous date simulations.
          </p>
        </div>
      </div>

      {/* Two Column Grid: Self-Reported vs Synthetic */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Left Column: Self-Reported Intake Form (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-slate-800 space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                  <UserCheck className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-white font-heading">Self-Reported Participant Intake</h2>
                  <p className="text-xs text-slate-400">Opt-in only. Stored explicitly as <code className="text-emerald-400 font-mono">source: self-reported</code></p>
                </div>
              </div>
            </div>

            {/* Quick Sample Bios */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>Fast test? Try a sample bio:</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {SAMPLE_BIOS.map((sample, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleSampleClick(sample)}
                    className="px-2.5 py-1 text-xs rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 hover:bg-slate-800/70 text-slate-300 transition-colors flex items-center gap-1.5"
                  >
                    <Zap className="w-3 h-3 text-amber-400" />
                    <span>{sample.title}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmitIntake} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1.5">
                  Your Name / Pseudonym <span className="text-slate-500 font-normal">(optional — Claude extracts if omitted)</span>
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Jordan Rivera"
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-900/90 border border-slate-800 focus:border-rose-500 focus:ring-1 focus:ring-rose-500 text-slate-100 placeholder-slate-500 text-sm outline-none transition-all"
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
                    Raw Bio & Personality Text <span className="text-rose-400">*</span>
                  </label>
                  <span className="text-[11px] text-slate-500">LinkedIn "About", Instagram bio, or free-form notes</span>
                </div>
                <textarea
                  rows={6}
                  value={bioText}
                  onChange={(e) => setBioText(e.target.value)}
                  placeholder="Paste your raw text here... e.g.:&#10;Software engineer in Seattle who loves backcountry camping and film photography. Looking for someone with high curiosity, deep empathy, and who can debate philosophy over tacos. Dealbreakers: poor communication and flakiness..."
                  className="w-full px-4 py-3 rounded-xl bg-slate-900/90 border border-slate-800 focus:border-rose-500 focus:ring-1 focus:ring-rose-500 text-slate-100 placeholder-slate-500 text-sm outline-none transition-all resize-y"
                  required
                />
              </div>

              {intakeError && (
                <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
                  <ShieldAlert className="w-4 h-4 shrink-0 text-rose-400" />
                  <span>{intakeError}</span>
                </div>
              )}

              <button
                type="submit"
                disabled={loadingIntake || !bioText.trim()}
                className="w-full py-3 px-6 rounded-xl bg-gradient-to-r from-rose-500 via-pink-500 to-rose-600 hover:from-rose-600 hover:to-pink-600 text-white font-semibold text-sm shadow-lg shadow-rose-500/25 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-all cursor-pointer"
              >
                {loadingIntake ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Analyzing Persona via Claude...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Analyze & Create Autonomous Agent</span>
                  </>
                )}
              </button>
            </form>

            {/* Extracted Profile Preview if just created */}
            {intakeSuccess && (
              <div className="p-5 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <img 
                      src={intakeSuccess.avatar_url} 
                      alt={intakeSuccess.name}
                      className="w-12 h-12 rounded-xl bg-slate-900 border border-emerald-500/40 p-0.5" 
                    />
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-white text-base">{intakeSuccess.name}</span>
                        {intakeSuccess.age && <span className="text-slate-400 text-xs font-mono">({intakeSuccess.age})</span>}
                        <span className="px-2 py-0.5 rounded-md bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-[10px] font-mono uppercase">
                          Self-Reported
                        </span>
                      </div>
                      <p className="text-xs text-slate-300">{intakeSuccess.analysis?.occupation || 'Creative Professional'} • {intakeSuccess.analysis?.location || 'Global'}</p>
                    </div>
                  </div>
                  <CheckCircle2 className="w-6 h-6 text-emerald-400" />
                </div>

                {intakeSuccess.analysis?.tagline && (
                  <p className="text-xs italic text-slate-300 bg-slate-900/60 p-2.5 rounded-lg border border-slate-800">
                    "{intakeSuccess.analysis.tagline}"
                  </p>
                )}

                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="p-2.5 rounded-lg bg-slate-900/70 border border-slate-800/80">
                    <span className="text-[10px] uppercase font-bold tracking-wider text-rose-400 block mb-1">Core Needs</span>
                    <ul className="text-slate-300 space-y-0.5 list-disc list-inside text-[11px]">
                      {intakeSuccess.analysis?.needs?.slice(0, 3).map((n, i) => <li key={i}>{n}</li>)}
                    </ul>
                  </div>
                  <div className="p-2.5 rounded-lg bg-slate-900/70 border border-slate-800/80">
                    <span className="text-[10px] uppercase font-bold tracking-wider text-violet-400 block mb-1">Key Values</span>
                    <div className="flex flex-wrap gap-1">
                      {intakeSuccess.analysis?.values?.slice(0, 3).map((v, i) => (
                        <span key={i} className="px-1.5 py-0.5 rounded bg-violet-500/10 text-violet-300 text-[10px] border border-violet-500/20">
                          {v}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="pt-2 flex items-center justify-between border-t border-emerald-500/20">
                  <span className="text-[11px] text-emerald-300">Profile saved to SQLite database. Ready for simulation!</span>
                  <button
                    onClick={() => onNavigate && onNavigate('rankings', { personId: intakeSuccess.id })}
                    className="px-3 py-1.5 rounded-lg bg-emerald-500 text-slate-950 font-bold text-xs flex items-center gap-1 hover:bg-emerald-400 transition-colors cursor-pointer"
                  >
                    <span>View Rankings</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Synthetic Persona Generator (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-slate-800 space-y-6">
            <div className="flex items-center gap-3 border-b border-slate-800/80 pb-4">
              <div className="w-10 h-10 rounded-xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center text-violet-400">
                <Bot className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-white font-heading">Synthetic Persona Factory</h2>
                <p className="text-xs text-slate-400">Generate diverse candidates via Claude (zero real data)</p>
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-300 space-y-2">
              <div className="flex items-start gap-2">
                <Info className="w-4 h-4 text-violet-400 shrink-0 mt-0.5" />
                <p className="text-[11px] leading-relaxed text-slate-300">
                  Synthetic profiles allow simulating 25+ rich personas spanning diverse professions (cellists, hardware builders, bioethicists, marine filmmakers), values, and styles without requiring 25 real people to sign up.
                </p>
              </div>
            </div>

            {/* Quick 1-Click Seed Curated Button */}
            <div className="p-4 rounded-xl bg-gradient-to-br from-violet-950/40 to-slate-900 border border-violet-500/30 space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-white">1-Click Full Demo Seed</h3>
                  <p className="text-xs text-slate-400">Populate the database with 25 distinct archetypes</p>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-violet-500/20 text-violet-300 border border-violet-500/40">
                  Instant
                </span>
              </div>
              <button
                type="button"
                onClick={handleSeedCurated}
                disabled={loadingSeed}
                className="w-full py-2.5 px-4 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-medium text-xs shadow-md shadow-violet-600/20 disabled:opacity-50 flex items-center justify-center gap-2 transition-all cursor-pointer"
              >
                {loadingSeed ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Seeding 25 Profiles...</span>
                  </>
                ) : (
                  <>
                    <Zap className="w-3.5 h-3.5" />
                    <span>Seed ~25 Diverse Profiles Now</span>
                  </>
                )}
              </button>
            </div>

            {/* Custom Batch Generator */}
            <div className="space-y-4 pt-2">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2">
                  Generate Custom Profiles via Claude
                </label>
                <div className="flex items-center gap-2">
                  {[3, 5, 10, 15].map((cnt) => (
                    <button
                      key={cnt}
                      type="button"
                      onClick={() => setSyntheticCount(cnt)}
                      className={`flex-1 py-1.5 rounded-lg text-xs font-mono transition-colors ${
                        syntheticCount === cnt
                          ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40 font-bold'
                          : 'bg-slate-900 text-slate-400 border border-slate-800 hover:bg-slate-800'
                      }`}
                    >
                      +{cnt}
                    </button>
                  ))}
                </div>
              </div>

              <button
                type="button"
                onClick={handleGenerateSynthetic}
                disabled={loadingSynthetic}
                className="w-full py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-medium text-xs disabled:opacity-50 flex items-center justify-center gap-2 transition-all cursor-pointer"
              >
                {loadingSynthetic ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin text-rose-400" />
                    <span>Generating {syntheticCount} Personas...</span>
                  </>
                ) : (
                  <>
                    <Bot className="w-3.5 h-3.5 text-rose-400" />
                    <span>Generate {syntheticCount} New Profiles</span>
                  </>
                )}
              </button>
            </div>

            {/* Notification messages */}
            {syntheticSuccess && (
              <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>{syntheticSuccess}</span>
                </div>
                <button
                  onClick={() => onNavigate && onNavigate('profiles')}
                  className="underline text-emerald-200 text-xs hover:text-white cursor-pointer"
                >
                  View Directory &rarr;
                </button>
              </div>
            )}

            {syntheticError && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
                {syntheticError}
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
