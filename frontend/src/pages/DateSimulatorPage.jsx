import React, { useState, useEffect } from 'react';
import { 
  PlayCircle, RefreshCw, Sparkles, HeartHandshake, Brain, MessageSquare, 
  ChevronRight, Play, Pause, RotateCcw, AlertTriangle, CheckCircle, Flame, Shuffle
} from 'lucide-react';
import { api } from '../services/api';

export default function DateSimulatorPage({ initialProfileAId, initialProfileBId, onNavigate }) {
  const [profiles, setProfiles] = useState([]);
  const [profileAId, setProfileAId] = useState(initialProfileAId || '');
  const [profileBId, setProfileBId] = useState(initialProfileBId || '');
  const [forceFresh, setForceFresh] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [simulationResult, setSimulationResult] = useState(null);

  // Playback state
  const [visibleTurnsCount, setVisibleTurnsCount] = useState(999);
  const [isPlaying, setIsPlaying] = useState(false);
  const [recentDates, setRecentDates] = useState([]);

  useEffect(() => {
    loadProfilesAndHistory();
  }, []);

  useEffect(() => {
    if (initialProfileAId) setProfileAId(initialProfileAId);
    if (initialProfileBId) setProfileBId(initialProfileBId);
  }, [initialProfileAId, initialProfileBId]);

  const loadProfilesAndHistory = async () => {
    try {
      const [profs, recents] = await Promise.all([
        api.getProfiles({ limit: 60 }),
        api.getDateHistory(8)
      ]);
      setProfiles(profs);
      setRecentDates(recents);

      // Default select first two if not provided
      if (!profileAId && profs.length > 0) {
        setProfileAId(profs[0].id);
      }
      if (!profileBId && profs.length > 1) {
        setProfileBId(profs[1].id);
      }
    } catch (err) {
      console.error('Failed to load simulator data:', err);
    }
  };

  const handleRandomPair = () => {
    if (profiles.length < 2) return;
    const idxA = Math.floor(Math.random() * profiles.length);
    let idxB = Math.floor(Math.random() * profiles.length);
    while (idxB === idxA) {
      idxB = Math.floor(Math.random() * profiles.length);
    }
    setProfileAId(profiles[idxA].id);
    setProfileBId(profiles[idxB].id);
    setError('');
  };

  const handleSimulate = async () => {
    if (!profileAId || !profileBId) {
      setError('Please select two different profiles.');
      return;
    }
    if (profileAId === profileBId) {
      setError('Cannot simulate a date between the same person.');
      return;
    }

    setLoading(true);
    setError('');
    setIsPlaying(false);

    try {
      const res = await api.simulateDate({
        profile_a_id: parseInt(profileAId),
        profile_b_id: parseInt(profileBId),
        force_fresh: forceFresh,
      });
      setSimulationResult(res);
      setVisibleTurnsCount(res.transcript?.turns?.length || 999);
      // Refresh recent dates
      const updatedRecents = await api.getDateHistory(8);
      setRecentDates(updatedRecents);
    } catch (err) {
      setError(err.message || 'Date simulation failed.');
    } finally {
      setLoading(false);
    }
  };

  // Replay turn by turn
  const handleStartReplay = () => {
    setVisibleTurnsCount(1);
    setIsPlaying(true);
  };

  useEffect(() => {
    let timer;
    if (isPlaying && simulationResult?.transcript?.turns) {
      const total = simulationResult.transcript.turns.length;
      if (visibleTurnsCount < total) {
        timer = setTimeout(() => {
          setVisibleTurnsCount((prev) => prev + 1);
        }, 1800);
      } else {
        setIsPlaying(false);
      }
    }
    return () => clearTimeout(timer);
  }, [isPlaying, visibleTurnsCount, simulationResult]);

  const profileA = profiles.find((p) => p.id === parseInt(profileAId));
  const profileB = profiles.find((p) => p.id === parseInt(profileBId));

  const transcript = simulationResult?.transcript;
  const score = simulationResult?.compatibility_score || 0;

  const getScoreColor = (sc) => {
    if (sc >= 82) return 'from-emerald-500 to-teal-400 text-emerald-400';
    if (sc >= 68) return 'from-rose-500 to-pink-500 text-rose-400';
    if (sc >= 50) return 'from-amber-500 to-yellow-400 text-amber-400';
    return 'from-slate-500 to-slate-400 text-slate-400';
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white font-heading flex items-center gap-2">
            <span>Agent Dating Arena</span>
            <span className="text-rose-500 text-sm">✦</span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Pick two autonomous agents. Claude prompts each persona to simulate a multi-turn conversation and evaluates compatibility.
          </p>
        </div>

        <button
          onClick={handleRandomPair}
          className="px-3.5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs font-semibold border border-slate-800 flex items-center gap-2 transition-colors self-start cursor-pointer"
        >
          <Shuffle className="w-3.5 h-3.5 text-rose-400" />
          <span>Surprise Match (Random Pair)</span>
        </button>
      </div>

      {/* Profile Selectors Arena */}
      <div className="grid grid-cols-1 md:grid-cols-11 gap-4 items-center">
        {/* Agent A Card Selector (5 cols) */}
        <div className="md:col-span-5 glass-panel rounded-2xl p-5 border border-slate-800/90 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono uppercase tracking-wider text-rose-400 font-bold flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-rose-400" />
              Agent A (Persona 1)
            </span>
            {profileA?.source && (
              <span className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                profileA.source === 'synthetic' ? 'bg-violet-500/20 text-violet-300' : 'bg-emerald-500/20 text-emerald-300'
              }`}>
                {profileA.source}
              </span>
            )}
          </div>

          <select
            value={profileAId}
            onChange={(e) => setProfileAId(e.target.value)}
            className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-slate-100 text-sm focus:outline-none focus:border-rose-500"
          >
            {profiles.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} {p.analysis?.occupation ? `— ${p.analysis.occupation}` : ''} ({p.source})
              </option>
            ))}
          </select>

          {profileA && (
            <div className="flex items-start gap-3 p-3 rounded-xl bg-slate-900/60 border border-slate-800/80">
              <img
                src={profileA.avatar_url}
                alt={profileA.name}
                className="w-12 h-12 rounded-xl bg-slate-950 border border-rose-500/30 p-0.5 shrink-0"
              />
              <div className="text-xs space-y-1">
                <div className="font-bold text-white text-sm">{profileA.name}</div>
                <div className="text-slate-400 line-clamp-1">{profileA.analysis?.tagline || profileA.analysis?.occupation}</div>
                <div className="text-slate-500 text-[11px] flex items-center gap-2">
                  <span>Style: <strong className="text-slate-300 font-normal">{profileA.analysis?.communication_style || 'Direct'}</strong></span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* VS Spark in Center (1 col) */}
        <div className="md:col-span-1 flex flex-col items-center justify-center py-2">
          <div className="w-10 h-10 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center text-rose-400 font-bold font-mono text-xs shadow-lg">
            VS
          </div>
        </div>

        {/* Agent B Card Selector (5 cols) */}
        <div className="md:col-span-5 glass-panel rounded-2xl p-5 border border-slate-800/90 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono uppercase tracking-wider text-cyan-400 font-bold flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-cyan-400" />
              Agent B (Persona 2)
            </span>
            {profileB?.source && (
              <span className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                profileB.source === 'synthetic' ? 'bg-violet-500/20 text-violet-300' : 'bg-emerald-500/20 text-emerald-300'
              }`}>
                {profileB.source}
              </span>
            )}
          </div>

          <select
            value={profileBId}
            onChange={(e) => setProfileBId(e.target.value)}
            className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-slate-100 text-sm focus:outline-none focus:border-cyan-500"
          >
            {profiles.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} {p.analysis?.occupation ? `— ${p.analysis.occupation}` : ''} ({p.source})
              </option>
            ))}
          </select>

          {profileB && (
            <div className="flex items-start gap-3 p-3 rounded-xl bg-slate-900/60 border border-slate-800/80">
              <img
                src={profileB.avatar_url}
                alt={profileB.name}
                className="w-12 h-12 rounded-xl bg-slate-950 border border-cyan-500/30 p-0.5 shrink-0"
              />
              <div className="text-xs space-y-1">
                <div className="font-bold text-white text-sm">{profileB.name}</div>
                <div className="text-slate-400 line-clamp-1">{profileB.analysis?.tagline || profileB.analysis?.occupation}</div>
                <div className="text-slate-500 text-[11px] flex items-center gap-2">
                  <span>Style: <strong className="text-slate-300 font-normal">{profileB.analysis?.communication_style || 'Warm'}</strong></span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Action Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-2xl glass-panel border border-slate-800">
        <label className="flex items-center gap-2 text-xs text-slate-400 cursor-pointer select-none">
          <input
            type="checkbox"
            checked={forceFresh}
            onChange={(e) => setForceFresh(e.target.checked)}
            className="rounded border-slate-700 bg-slate-900 text-rose-500 focus:ring-0"
          />
          <span>Force fresh AI simulation (ignore cached date)</span>
        </label>

        {error && <span className="text-xs text-rose-400">{error}</span>}

        <button
          onClick={handleSimulate}
          disabled={loading || !profileAId || !profileBId || profileAId === profileBId}
          className="w-full sm:w-auto px-8 py-3 rounded-xl bg-gradient-to-r from-rose-500 via-pink-500 to-violet-600 hover:from-rose-600 hover:to-violet-700 text-white font-bold text-sm shadow-xl shadow-rose-500/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-all cursor-pointer"
        >
          {loading ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Simulating Conversation via Claude...</span>
            </>
          ) : (
            <>
              <PlayCircle className="w-4 h-4" />
              <span>Simulate Agent Date Now</span>
            </>
          )}
        </button>
      </div>

      {/* Simulation Results Viewport */}
      {simulationResult && transcript && (
        <div className="space-y-6 animate-in fade-in duration-300">
          
          {/* Compatibility Hero Card */}
          <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-slate-800 relative overflow-hidden space-y-6">
            <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 border-b border-slate-800 pb-6">
              
              {/* Score Meter */}
              <div className="flex items-center gap-5">
                <div className="relative w-24 h-24 rounded-2xl bg-slate-900/90 border border-slate-800 flex flex-col items-center justify-center shadow-inner">
                  <span className={`text-4xl font-extrabold font-heading ${getScoreColor(score)}`}>
                    {score}
                  </span>
                  <span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest mt-0.5">
                    / 100
                  </span>
                </div>
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono uppercase tracking-wider text-slate-400">Compatibility Verdict:</span>
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-500/20 text-rose-300 border border-rose-500/40">
                      {transcript.recommendation || 'Promising Spark'}
                    </span>
                  </div>
                  <h3 className="text-xl font-bold text-white font-heading">
                    {transcript.profile_a_name} & {transcript.profile_b_name}
                  </h3>
                  <p className="text-xs text-slate-400 max-w-xl leading-relaxed">
                    {transcript.summary_rationale}
                  </p>
                </div>
              </div>

              {/* Playback Controls */}
              <div className="flex items-center gap-2 self-stretch lg:self-auto justify-end">
                <button
                  onClick={handleStartReplay}
                  className="px-3.5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 text-xs font-medium flex items-center gap-1.5 transition-colors cursor-pointer"
                >
                  <RotateCcw className="w-3.5 h-3.5 text-rose-400" />
                  <span>Replay Live</span>
                </button>
                {isPlaying ? (
                  <button
                    onClick={() => setIsPlaying(false)}
                    className="px-3.5 py-2 rounded-xl bg-amber-500/20 text-amber-300 border border-amber-500/40 text-xs font-medium flex items-center gap-1.5 cursor-pointer"
                  >
                    <Pause className="w-3.5 h-3.5" />
                    <span>Pause</span>
                  </button>
                ) : (
                  <button
                    onClick={() => setVisibleTurnsCount(transcript.turns.length)}
                    className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium cursor-pointer"
                  >
                    <span>Show All Turns</span>
                  </button>
                )}
              </div>
            </div>

            {/* Strengths & Frictions Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 space-y-2">
                <div className="flex items-center gap-1.5 text-emerald-400 font-bold uppercase tracking-wider text-[10px]">
                  <CheckCircle className="w-3.5 h-3.5" />
                  <span>Shared Alignment & Strengths</span>
                </div>
                <ul className="text-slate-300 space-y-1 list-disc list-inside">
                  {transcript.shared_strengths?.map((st, i) => (
                    <li key={i}>{st}</li>
                  ))}
                </ul>
              </div>

              <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 space-y-2">
                <div className="flex items-center gap-1.5 text-amber-400 font-bold uppercase tracking-wider text-[10px]">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  <span>Potential Friction Points</span>
                </div>
                <ul className="text-slate-300 space-y-1 list-disc list-inside">
                  {transcript.potential_friction_points?.map((fr, i) => (
                    <li key={i} className="text-amber-200/90">{fr}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Turn by Turn Dialogue Feed */}
          <div className="space-y-4">
            <div className="flex items-center justify-between text-xs text-slate-400 px-1">
              <span className="font-mono uppercase tracking-wider">Simulated Dialogue Transcript ({Math.min(visibleTurnsCount, transcript.turns.length)} of {transcript.turns.length} turns)</span>
              {isPlaying && <span className="text-rose-400 flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-rose-400 animate-ping" /> Streaming live agent responses...</span>}
            </div>

            <div className="space-y-4">
              {transcript.turns.slice(0, visibleTurnsCount).map((turn, index) => {
                const isSpeakerA = turn.speaker_id === profileA?.id || turn.speaker_name === profileA?.name;
                const speakerProfile = isSpeakerA ? profileA : profileB;

                return (
                  <div
                    key={index}
                    className={`flex gap-3 sm:gap-4 p-4 sm:p-5 rounded-2xl glass-panel border transition-all duration-300 ${
                      isSpeakerA
                        ? 'border-rose-500/20 bg-rose-950/10 ml-0 mr-4 sm:mr-12'
                        : 'border-cyan-500/20 bg-cyan-950/10 ml-4 sm:ml-12 mr-0'
                    }`}
                  >
                    {/* Avatar */}
                    <img
                      src={speakerProfile?.avatar_url || `https://api.dicebear.com/7.x/notionists/svg?seed=${turn.speaker_name}`}
                      alt={turn.speaker_name}
                      className={`w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-slate-900 border shrink-0 p-0.5 ${
                        isSpeakerA ? 'border-rose-500/40' : 'border-cyan-500/40'
                      }`}
                    />

                    {/* Content */}
                    <div className="flex-1 space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className={`font-bold text-sm ${isSpeakerA ? 'text-rose-300' : 'text-cyan-300'}`}>
                            {turn.speaker_name}
                          </span>
                          <span className="text-[10px] font-mono text-slate-500">
                            Agent Turn #{index + 1}
                          </span>
                        </div>
                        {turn.stage && (
                          <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded-full bg-slate-900 text-slate-400 border border-slate-800">
                            {turn.stage}
                          </span>
                        )}
                      </div>

                      {/* Spoken Message */}
                      <p className="text-slate-200 text-sm leading-relaxed">
                        "{turn.message}"
                      </p>

                      {/* Agent Inner Thought Bubble */}
                      {turn.inner_thought && (
                        <div className="mt-2.5 p-2.5 rounded-xl bg-slate-950/70 border border-slate-800/80 flex items-start gap-2 text-xs">
                          <Brain className="w-3.5 h-3.5 text-violet-400 shrink-0 mt-0.5" />
                          <div className="space-y-0.5">
                            <span className="text-[10px] font-mono text-violet-400 uppercase tracking-wider block">
                              Agent Internal Thought / Compatibility Calculation:
                            </span>
                            <p className="text-slate-400 italic text-[11px] leading-normal">
                              {turn.inner_thought}
                            </p>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Recent Date Simulations History Carousel */}
      {recentDates.length > 0 && (
        <div className="pt-6 border-t border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white font-heading">Recent Simulated Dates</h3>
            <span className="text-xs text-slate-500">{recentDates.length} recorded</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {recentDates.map((item) => {
              const trans = item.transcript;
              return (
                <div
                  key={item.id}
                  onClick={() => {
                    setProfileAId(item.profile_a_id);
                    setProfileBId(item.profile_b_id);
                    setSimulationResult(item);
                    setVisibleTurnsCount(trans?.turns?.length || 999);
                  }}
                  className="glass-panel glass-panel-hover rounded-xl p-4 border border-slate-800/80 space-y-2 cursor-pointer group"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-200 group-hover:text-rose-400 transition-colors">
                      {trans?.profile_a_name} & {trans?.profile_b_name}
                    </span>
                    <span className="text-xs font-mono font-bold text-rose-400">
                      {item.compatibility_score}%
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
                    {item.summary_rationale}
                  </p>
                  <div className="text-[10px] text-slate-500 font-mono">
                    {trans?.turns?.length || 0} turns simulated
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
