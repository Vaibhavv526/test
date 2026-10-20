import React, { useState, useEffect } from 'react';
import { Search, Filter, Sparkles, HeartHandshake, Eye, BarChart3, AlertTriangle, MessageSquare, Compass, Shield, User, X, FileText } from 'lucide-react';
import { api } from '../services/api';

export default function ProfilesPage({ onNavigate, onSelectForDate, onSelectForRankings }) {
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [sourceFilter, setSourceFilter] = useState('all');
  const [selectedProfile, setSelectedProfile] = useState(null);

  useEffect(() => {
    loadProfiles();
  }, [sourceFilter]);

  const loadProfiles = async () => {
    setLoading(true);
    try {
      const params = {};
      if (sourceFilter !== 'all') {
        params.source = sourceFilter;
      }
      const data = await api.getProfiles(params);
      setProfiles(data);
    } catch (err) {
      console.error('Failed to load profiles:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredProfiles = profiles.filter((p) => {
    if (!search.trim()) return true;
    const term = search.toLowerCase();
    return (
      p.name.toLowerCase().includes(term) ||
      (p.analysis?.occupation && p.analysis.occupation.toLowerCase().includes(term)) ||
      (p.analysis?.location && p.analysis.location.toLowerCase().includes(term)) ||
      (p.analysis?.tagline && p.analysis.tagline.toLowerCase().includes(term))
    );
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Directory Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white font-heading">
            Candidate Directory
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Browse extracted psychological profiles, romantic needs, and dealbreakers.
          </p>
        </div>

        {/* Search & Filter Controls */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          {/* Search Box */}
          <div className="relative min-w-[240px]">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search name or profession..."
              className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-rose-500 transition-colors"
            />
          </div>

          {/* Source Tabs */}
          <div className="flex items-center p-1 rounded-xl bg-slate-900 border border-slate-800 text-xs">
            <button
              onClick={() => setSourceFilter('all')}
              className={`px-3 py-1.5 rounded-lg transition-colors font-medium ${
                sourceFilter === 'all'
                  ? 'bg-slate-800 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              All ({profiles.length})
            </button>
            <button
              onClick={() => setSourceFilter('self-reported')}
              className={`px-3 py-1.5 rounded-lg transition-colors font-medium flex items-center gap-1.5 ${
                sourceFilter === 'self-reported'
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              Self-Reported
            </button>
            <button
              onClick={() => setSourceFilter('synthetic')}
              className={`px-3 py-1.5 rounded-lg transition-colors font-medium flex items-center gap-1.5 ${
                sourceFilter === 'synthetic'
                  ? 'bg-violet-500/20 text-violet-300 border border-violet-500/40'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <span className="w-1.5 h-1.5 rounded-full bg-violet-400" />
              Synthetic
            </button>
          </div>
        </div>
      </div>

      {/* Grid of Profile Cards */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((n) => (
            <div key={n} className="glass-panel rounded-2xl p-6 border border-slate-800/80 animate-pulse h-80 space-y-4">
              <div className="flex gap-4">
                <div className="w-14 h-14 rounded-2xl bg-slate-800" />
                <div className="flex-1 space-y-2">
                  <div className="w-3/4 h-4 bg-slate-800 rounded" />
                  <div className="w-1/2 h-3 bg-slate-800 rounded" />
                </div>
              </div>
              <div className="h-12 bg-slate-800/60 rounded" />
              <div className="space-y-2">
                <div className="h-6 bg-slate-800/40 rounded" />
                <div className="h-6 bg-slate-800/40 rounded" />
              </div>
            </div>
          ))}
        </div>
      ) : filteredProfiles.length === 0 ? (
        <div className="text-center py-16 glass-panel rounded-2xl border border-slate-800 space-y-4">
          <p className="text-slate-400 text-sm">No profiles found matching your query.</p>
          <button
            onClick={() => onNavigate && onNavigate('intake')}
            className="px-4 py-2 rounded-xl bg-rose-500 hover:bg-rose-600 text-white text-xs font-semibold"
          >
            Go to Intake / Seed Profiles
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProfiles.map((profile) => {
            const analysis = profile.analysis || {};
            const isSynthetic = profile.source === 'synthetic';

            return (
              <div
                key={profile.id}
                className="glass-panel glass-panel-hover rounded-2xl p-6 border border-slate-800/90 flex flex-col justify-between space-y-5 relative group"
              >
                {/* Source Badge */}
                <div className="absolute top-5 right-5">
                  {isSynthetic ? (
                    <span className="px-2 py-0.5 rounded-full bg-violet-500/15 text-violet-300 border border-violet-500/30 text-[10px] font-mono tracking-wider uppercase font-semibold">
                      Synthetic
                    </span>
                  ) : (
                    <span className="px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 text-[10px] font-mono tracking-wider uppercase font-semibold flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                      Self-Reported
                    </span>
                  )}
                </div>

                {/* Profile Header */}
                <div className="space-y-4">
                  <div className="flex items-start gap-4 pr-16">
                    <img
                      src={profile.avatar_url || `https://api.dicebear.com/7.x/notionists/svg?seed=${profile.name}`}
                      alt={profile.name}
                      className="w-14 h-14 rounded-2xl bg-slate-900 border border-slate-700/80 p-0.5 shrink-0 object-cover"
                    />
                    <div>
                      <h3 className="font-bold text-white text-lg font-heading leading-tight group-hover:text-rose-400 transition-colors">
                        {profile.name}
                      </h3>
                      <p className="text-xs text-slate-400 mt-0.5">
                        {analysis.age ? `${analysis.age} yo • ` : ''}
                        {analysis.occupation || 'Creative'}
                      </p>
                      {analysis.location && (
                        <p className="text-[11px] text-slate-500">{analysis.location}</p>
                      )}
                    </div>
                  </div>

                  {/* 1-Line Tagline */}
                  {analysis.tagline && (
                    <p className="text-xs italic text-slate-300 line-clamp-2 bg-slate-900/60 p-2.5 rounded-xl border border-slate-800/80">
                      "{analysis.tagline}"
                    </p>
                  )}

                  {/* Extracted Traits Pills */}
                  <div className="space-y-3 pt-1">
                    {/* Core Values */}
                    <div>
                      <span className="text-[10px] uppercase font-bold tracking-wider text-violet-400 block mb-1">
                        Core Values
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {analysis.values?.slice(0, 3).map((val, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-0.5 rounded-md bg-violet-500/10 text-violet-300 border border-violet-500/20 text-[11px]"
                          >
                            {val}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Hobbies / Passions */}
                    <div>
                      <span className="text-[10px] uppercase font-bold tracking-wider text-rose-400 block mb-1">
                        Hobbies & Craft
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {analysis.hobbies?.slice(0, 3).map((hob, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-0.5 rounded-md bg-rose-500/10 text-rose-300 border border-rose-500/20 text-[11px]"
                          >
                            {hob}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Dealbreakers */}
                    {analysis.dealbreakers && analysis.dealbreakers.length > 0 && (
                      <div>
                        <span className="text-[10px] uppercase font-bold tracking-wider text-amber-400 block mb-1 flex items-center gap-1">
                          <AlertTriangle className="w-3 h-3 text-amber-400" />
                          Dealbreaker Red Flag
                        </span>
                        <div className="text-[11px] text-slate-400 bg-amber-500/5 border border-amber-500/20 px-2 py-1 rounded-md line-clamp-1">
                          {analysis.dealbreakers[0]}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Card Action Footer */}
                <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between gap-2">
                  <button
                    onClick={() => setSelectedProfile(profile)}
                    className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs font-medium border border-slate-800 flex items-center gap-1.5 transition-colors cursor-pointer"
                  >
                    <Eye className="w-3.5 h-3.5 text-slate-400" />
                    <span>Deep Profile</span>
                  </button>

                  <div className="flex items-center gap-1.5">
                    <button
                      onClick={() => onSelectForRankings && onSelectForRankings(profile.id)}
                      title="View Compatibility Rankings"
                      className="p-2 rounded-xl bg-slate-900 hover:bg-violet-500/20 hover:text-violet-300 text-slate-400 border border-slate-800 transition-colors cursor-pointer"
                    >
                      <BarChart3 className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => onSelectForDate && onSelectForDate(profile.id)}
                      className="px-3 py-1.5 rounded-xl bg-rose-500/15 hover:bg-rose-500 text-rose-300 hover:text-white border border-rose-500/30 text-xs font-semibold flex items-center gap-1 transition-all cursor-pointer"
                    >
                      <HeartHandshake className="w-3.5 h-3.5" />
                      <span>Simulate Date</span>
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Deep Profile Inspection Modal */}
      {selectedProfile && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 sm:p-8 space-y-6 shadow-2xl relative">
            {/* Close Button */}
            <button
              onClick={() => setSelectedProfile(null)}
              className="absolute top-6 right-6 p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>

            {/* Modal Header */}
            <div className="flex items-start gap-4">
              <img
                src={selectedProfile.avatar_url}
                alt={selectedProfile.name}
                className="w-18 h-18 rounded-2xl bg-slate-950 border border-slate-700 p-1"
              />
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <h2 className="text-2xl font-bold text-white font-heading">{selectedProfile.name}</h2>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-mono uppercase ${
                    selectedProfile.source === 'synthetic'
                      ? 'bg-violet-500/20 text-violet-300 border border-violet-500/30'
                      : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                  }`}>
                    {selectedProfile.source}
                  </span>
                </div>
                <p className="text-sm text-slate-300">
                  {selectedProfile.analysis?.occupation || 'Creative'} • {selectedProfile.analysis?.location || 'Global'}
                </p>
                {selectedProfile.analysis?.dating_intentions && (
                  <p className="text-xs text-rose-400 font-medium">
                    Intention: {selectedProfile.analysis.dating_intentions}
                  </p>
                )}
              </div>
            </div>

            {selectedProfile.analysis?.tagline && (
              <p className="text-sm italic text-slate-200 bg-slate-950/60 p-3 rounded-xl border border-slate-800">
                "{selectedProfile.analysis.tagline}"
              </p>
            )}

            {/* Deep Trait Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
                <h4 className="font-bold text-violet-400 uppercase tracking-wider text-[11px]">Core Needs</h4>
                <ul className="text-slate-300 space-y-1 list-disc list-inside">
                  {selectedProfile.analysis?.needs?.map((need, idx) => (
                    <li key={idx}>{need}</li>
                  ))}
                </ul>
              </div>

              <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
                <h4 className="font-bold text-rose-400 uppercase tracking-wider text-[11px]">Core Values</h4>
                <div className="flex flex-wrap gap-1.5">
                  {selectedProfile.analysis?.values?.map((val, idx) => (
                    <span key={idx} className="px-2 py-0.5 rounded bg-violet-500/10 text-violet-300 border border-violet-500/20">
                      {val}
                    </span>
                  ))}
                </div>
              </div>

              <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
                <h4 className="font-bold text-emerald-400 uppercase tracking-wider text-[11px]">Communication Style</h4>
                <p className="text-slate-300 leading-relaxed">
                  {selectedProfile.analysis?.communication_style || 'Direct and reflective'}
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
                <h4 className="font-bold text-amber-400 uppercase tracking-wider text-[11px]">Dealbreakers</h4>
                <ul className="text-slate-300 space-y-1 list-disc list-inside">
                  {selectedProfile.analysis?.dealbreakers?.map((deal, idx) => (
                    <li key={idx} className="text-amber-200/90">{deal}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Raw Input Text Preview */}
            <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
              <div className="flex items-center gap-2 text-xs font-semibold text-slate-400">
                <FileText className="w-4 h-4 text-slate-500" />
                <span>Original Raw Bio Text (Input to Claude)</span>
              </div>
              <p className="text-xs text-slate-400 font-mono leading-relaxed bg-slate-900 p-3 rounded-lg border border-slate-800/80 max-h-36 overflow-y-auto">
                {selectedProfile.raw_input}
              </p>
            </div>

            {/* Modal Actions */}
            <div className="pt-2 flex items-center justify-end gap-3">
              <button
                onClick={() => {
                  setSelectedProfile(null);
                  onSelectForRankings && onSelectForRankings(selectedProfile.id);
                }}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold cursor-pointer"
              >
                Find Best Ranked Matches
              </button>
              <button
                onClick={() => {
                  setSelectedProfile(null);
                  onSelectForDate && onSelectForDate(selectedProfile.id);
                }}
                className="px-4 py-2 rounded-xl bg-rose-500 hover:bg-rose-600 text-white text-xs font-semibold cursor-pointer"
              >
                Simulate Date With Someone
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
