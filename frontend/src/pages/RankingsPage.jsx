import React, { useState, useEffect } from 'react';
import { 
  BarChart3, Trophy, HeartHandshake, Sparkles, AlertTriangle, 
  CheckCircle2, ArrowRight, UserCheck, Bot, RefreshCw, Flame
} from 'lucide-react';
import { api } from '../services/api';

export default function RankingsPage({ initialPersonId, onSimulatePair, onNavigate }) {
  const [profiles, setProfiles] = useState([]);
  const [selectedPersonId, setSelectedPersonId] = useState(initialPersonId || '');
  const [rankings, setRankings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadProfiles();
  }, []);

  useEffect(() => {
    if (initialPersonId) {
      setSelectedPersonId(initialPersonId);
    }
  }, [initialPersonId]);

  useEffect(() => {
    if (selectedPersonId) {
      loadRankings(selectedPersonId);
    }
  }, [selectedPersonId]);

  const loadProfiles = async () => {
    try {
      const data = await api.getProfiles({ limit: 60 });
      setProfiles(data);
      if (!selectedPersonId && data.length > 0) {
        setSelectedPersonId(data[0].id);
      }
    } catch (err) {
      console.error('Failed to load profiles:', err);
    }
  };

  const loadRankings = async (personId) => {
    setLoading(true);
    setError('');
    try {
      const data = await api.getRankings(personId);
      setRankings(data);
    } catch (err) {
      setError(err.message || 'Failed to load rankings.');
    } finally {
      setLoading(false);
    }
  };

  const targetPerson = profiles.find((p) => p.id === parseInt(selectedPersonId));

  const getRankBadge = (index) => {
    if (index === 0) return { label: '#1 Top Match', color: 'bg-amber-500/20 text-amber-300 border-amber-500/40' };
    if (index === 1) return { label: '#2 Match', color: 'bg-slate-300/20 text-slate-200 border-slate-300/40' };
    if (index === 2) return { label: '#3 Match', color: 'bg-amber-700/20 text-amber-400 border-amber-700/40' };
    return { label: `#${index + 1}`, color: 'bg-slate-800 text-slate-400 border-slate-700' };
  };

  const getScoreBadge = (score) => {
    if (score >= 85) return 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10';
    if (score >= 70) return 'text-rose-400 border-rose-500/30 bg-rose-500/10';
    if (score >= 55) return 'text-amber-400 border-amber-500/30 bg-amber-500/10';
    return 'text-slate-400 border-slate-700 bg-slate-900';
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white font-heading flex items-center gap-2">
            <Trophy className="w-7 h-7 text-amber-400" />
            <span>Compatibility Rankings</span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Autonomous compatibility rankings for any participant against all other candidates.
          </p>
        </div>

        {/* Person Selector Dropdown */}
        <div className="flex items-center gap-3">
          <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 whitespace-nowrap">
            Rank For:
          </label>
          <select
            value={selectedPersonId}
            onChange={(e) => setSelectedPersonId(e.target.value)}
            className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-700 text-slate-100 text-sm focus:outline-none focus:border-rose-500"
          >
            {profiles.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.source})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Target Person Hero Banner */}
      {targetPerson && (
        <div className="glass-panel rounded-2xl p-6 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-gradient-to-r from-slate-900/90 via-slate-900/60 to-rose-950/20">
          <div className="flex items-center gap-4">
            <img
              src={targetPerson.avatar_url}
              alt={targetPerson.name}
              className="w-16 h-16 rounded-2xl bg-slate-950 border border-rose-500/30 p-0.5 shrink-0"
            />
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-bold text-white font-heading">{targetPerson.name}</h2>
                <span className={`px-2 py-0.5 rounded text-[10px] font-mono uppercase ${
                  targetPerson.source === 'synthetic'
                    ? 'bg-violet-500/20 text-violet-300 border border-violet-500/30'
                    : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                }`}>
                  {targetPerson.source}
                </span>
              </div>
              <p className="text-xs text-slate-400">
                {targetPerson.analysis?.age ? `${targetPerson.analysis.age} yo • ` : ''}
                {targetPerson.analysis?.occupation || 'Creative'} • {targetPerson.analysis?.location || 'Global'}
              </p>
              {targetPerson.analysis?.tagline && (
                <p className="text-xs italic text-slate-300">"{targetPerson.analysis.tagline}"</p>
              )}
            </div>
          </div>

          <div className="text-right sm:border-l sm:border-slate-800 sm:pl-6">
            <span className="text-xs text-slate-500 uppercase tracking-wider block font-mono">Comparing against</span>
            <span className="text-2xl font-bold text-white font-heading">{rankings.length} candidates</span>
          </div>
        </div>
      )}

      {/* Rankings List */}
      {loading ? (
        <div className="py-20 text-center space-y-3">
          <RefreshCw className="w-8 h-8 animate-spin text-rose-500 mx-auto" />
          <p className="text-slate-400 text-sm">Evaluating psychological compatibility and ranking matches...</p>
        </div>
      ) : error ? (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm">
          {error}
        </div>
      ) : rankings.length === 0 ? (
        <div className="text-center py-16 glass-panel rounded-2xl border border-slate-800">
          <p className="text-slate-400 text-sm">No other candidates to rank against. Seed synthetic profiles to begin!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {rankings.map((match, idx) => {
            const badge = getRankBadge(idx);
            const partner = match.match_profile;
            const analysis = partner.analysis || {};

            return (
              <div
                key={partner.id}
                className="glass-panel glass-panel-hover rounded-2xl p-5 sm:p-6 border border-slate-800/90 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 transition-all duration-200"
              >
                {/* Left: Rank & Profile details */}
                <div className="flex items-start gap-4 flex-1">
                  {/* Rank Badge */}
                  <div className="flex flex-col items-center justify-center shrink-0">
                    <span className={`px-2.5 py-1 rounded-xl text-xs font-mono font-bold border ${badge.color}`}>
                      {badge.label}
                    </span>
                  </div>

                  {/* Avatar */}
                  <img
                    src={partner.avatar_url}
                    alt={partner.name}
                    className="w-14 h-14 rounded-2xl bg-slate-900 border border-slate-700/80 p-0.5 shrink-0"
                  />

                  {/* Info */}
                  <div className="space-y-2 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="font-bold text-white text-lg font-heading">{partner.name}</h3>
                      <span className="text-xs text-slate-400 font-normal">
                        ({analysis.age || 'Age open'}, {analysis.occupation || 'Creative'})
                      </span>
                      <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded uppercase ${
                        partner.source === 'synthetic'
                          ? 'bg-violet-500/20 text-violet-300'
                          : 'bg-emerald-500/20 text-emerald-300'
                      }`}>
                        {partner.source}
                      </span>
                      {match.has_date_run && (
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/40">
                          Date Simulated
                        </span>
                      )}
                    </div>

                    {/* One-Line Rationale */}
                    <p className="text-xs sm:text-sm text-slate-300 leading-relaxed font-medium">
                      "{match.summary_rationale}"
                    </p>

                    {/* Shared Strengths Chips */}
                    <div className="flex flex-wrap items-center gap-1.5 pt-1">
                      {match.shared_strengths?.slice(0, 2).map((st, i) => (
                        <span key={i} className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 text-[11px] flex items-center gap-1">
                          <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                          <span>{st}</span>
                        </span>
                      ))}
                      {match.potential_friction_points && match.potential_friction_points.length > 0 && (
                        <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20 text-[11px] flex items-center gap-1">
                          <AlertTriangle className="w-3 h-3 text-amber-400" />
                          <span className="line-clamp-1">{match.potential_friction_points[0]}</span>
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Right: Score Gauge & Action */}
                <div className="flex items-center gap-4 w-full lg:w-auto justify-between lg:justify-end border-t lg:border-t-0 border-slate-800/80 pt-4 lg:pt-0">
                  <div className="text-center">
                    <div className={`px-3.5 py-2 rounded-2xl border font-mono font-bold text-xl ${getScoreBadge(match.compatibility_score)}`}>
                      {match.compatibility_score}%
                    </div>
                    <span className="text-[10px] font-mono text-slate-500 uppercase tracking-wider block mt-1">
                      {match.recommendation}
                    </span>
                  </div>

                  <button
                    onClick={() => onSimulatePair && onSimulatePair(targetPerson.id, partner.id)}
                    className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-rose-500 to-pink-600 hover:from-rose-600 hover:to-pink-700 text-white font-semibold text-xs flex items-center gap-1.5 shadow-md shadow-rose-500/20 transition-all cursor-pointer"
                  >
                    <HeartHandshake className="w-4 h-4" />
                    <span>{match.has_date_run ? 'View Date Transcript' : 'Simulate Date Now'}</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
