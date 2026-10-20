import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import IntakePage from './pages/IntakePage';
import ProfilesPage from './pages/ProfilesPage';
import DateSimulatorPage from './pages/DateSimulatorPage';
import RankingsPage from './pages/RankingsPage';
import { api } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('profiles');
  const [systemStatus, setSystemStatus] = useState(null);

  // Cross-page navigation state
  const [dateProfileAId, setDateProfileAId] = useState(null);
  const [dateProfileBId, setDateProfileBId] = useState(null);
  const [rankingsPersonId, setRankingsPersonId] = useState(null);

  useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    try {
      const data = await api.getStatus();
      setSystemStatus(data);
    } catch (err) {
      console.warn('Backend status check:', err);
    }
  };

  const handleProfileCreated = (newProfile) => {
    fetchStatus();
    if (newProfile?.id) {
      setRankingsPersonId(newProfile.id);
      setActiveTab('profiles');
    }
  };

  const handleSelectForDate = (profileId) => {
    setDateProfileAId(profileId);
    setActiveTab('dates');
  };

  const handleSelectForRankings = (personId) => {
    setRankingsPersonId(personId);
    setActiveTab('rankings');
  };

  const handleSimulatePair = (personAId, personBId) => {
    setDateProfileAId(personAId);
    setDateProfileBId(personBId);
    setActiveTab('dates');
  };

  const handleNavigate = (tab, params = {}) => {
    if (params.personId) {
      setRankingsPersonId(params.personId);
    }
    setActiveTab(tab);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-rose-500 selection:text-white">
      {/* Top Navigation */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        systemStatus={systemStatus}
      />

      {/* Main Content Area */}
      <main className="flex-1 pb-16">
        {activeTab === 'intake' && (
          <IntakePage
            onProfileCreated={handleProfileCreated}
            onNavigate={handleNavigate}
          />
        )}

        {activeTab === 'profiles' && (
          <ProfilesPage
            onNavigate={handleNavigate}
            onSelectForDate={handleSelectForDate}
            onSelectForRankings={handleSelectForRankings}
          />
        )}

        {activeTab === 'dates' && (
          <DateSimulatorPage
            initialProfileAId={dateProfileAId}
            initialProfileBId={dateProfileBId}
            onNavigate={handleNavigate}
          />
        )}

        {activeTab === 'rankings' && (
          <RankingsPage
            initialPersonId={rankingsPersonId}
            onSimulatePair={handleSimulatePair}
            onNavigate={handleNavigate}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-8 px-4 text-center text-xs text-slate-500 space-y-2">
        <p className="flex items-center justify-center gap-1.5">
          <span>AuraMatch Agentic Dating Simulation</span>
          <span>•</span>
          <span className="text-slate-400">Powered by Anthropic Claude API</span>
          <span>•</span>
          <span>Zero Web Scraping Policy (Consenting & Synthetic Data Only)</span>
        </p>
        <p className="text-[11px] text-slate-600 font-mono">
          FastAPI + SQLite + React + Vite + Tailwind CSS
        </p>
      </footer>
    </div>
  );
}
