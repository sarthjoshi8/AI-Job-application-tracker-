import React, { useState, useEffect } from 'react';
import { apiRequest } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Navbar } from '../components/Navbar';
import { SolarOrbitView } from '../components/SolarOrbitView';
import { KanbanBoard } from '../components/KanbanBoard';
import { AIJobRadar } from '../components/AIJobRadar';
import { ApplicationModal } from '../components/ApplicationModal';
import { NewApplicationModal } from '../components/NewApplicationModal';
import { ImportModal } from '../components/ImportModal';
import { SettingsModal } from '../components/SettingsModal';
import { 
  RefreshCw, 
  Sparkles, 
  TrendingUp, 
  Clock, 
  Award, 
  Search,
  Orbit,
  Flame,
  Zap,
  Target
} from 'lucide-react';
import confetti from 'canvas-confetti';

export const Dashboard: React.FC = () => {
  const { token, user } = useAuth();
  const [applications, setApplications] = useState<any[]>([]);
  const [nudges, setNudges] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'solar' | 'kanban' | 'radar'>('solar');
  
  // Modals
  const [selectedApp, setSelectedApp] = useState<any | null>(null);
  const [showNewAppModal, setShowNewAppModal] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);

  const fetchNudgesOnly = async () => {
    try {
      const nudgesData = await apiRequest('/nudges?status=pending', { token }).catch(() => []);
      setNudges(nudgesData || []);
    } catch {}
  };

  const fetchData = async () => {
    try {
      setLoading(true);
      const [appsData, nudgesData] = await Promise.all([
        apiRequest('/applications', { token }),
        apiRequest('/nudges?status=pending', { token }).catch(() => [])
      ]);
      setApplications(appsData || []);
      setNudges(nudgesData || []);
    } catch (err: any) {
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [token]);

  const handleStatusChange = async (appId: string, newStatus: string) => {
    try {
      const updated = await apiRequest(`/applications/${appId}/status`, {
        method: 'PATCH',
        token,
        body: JSON.stringify({ status: newStatus })
      });
      setApplications((prev) =>
        prev.map((app) => (app.id === appId ? updated : app))
      );
      if (selectedApp?.id === appId) {
        setSelectedApp(updated);
      }
      
      // Refresh notifications immediately to pick up the new automated update message
      fetchNudgesOnly();

      if (newStatus === 'offer') {
        try {
          confetti({
            particleCount: 120,
            spread: 80,
            origin: { y: 0.6 }
          });
        } catch {}
      }
    } catch (err: any) {
      alert(`Status transition failed: ${err.message}`);
    }
  };

  const handleSelectNudgeApp = (appId: string) => {
    const found = applications.find(a => a.id === appId);
    if (found) {
      setSelectedApp(found);
    } else {
      apiRequest(`/applications/${appId}`, { token }).then(setSelectedApp);
    }
  };

  const filteredApps = applications.filter((app) => {
    const q = searchQuery.toLowerCase();
    return (
      app.company?.toLowerCase().includes(q) ||
      app.role?.toLowerCase().includes(q) ||
      app.jobDescription?.toLowerCase().includes(q)
    );
  });

  const stats = {
    total: applications.length,
    applied: applications.filter(a => a.status === 'applied').length,
    interview: applications.filter(a => a.status === 'interview').length,
    offer: applications.filter(a => a.status === 'offer').length,
  };

  return (
    <div className="min-h-screen space-bg flex flex-col selection:bg-sky-500 selection:text-white">
      
      <Navbar
        viewMode={viewMode}
        setViewMode={setViewMode}
        onOpenNewApp={() => setShowNewAppModal(true)}
        onOpenImport={() => setShowImportModal(true)}
        onOpenSettings={() => setShowSettingsModal(true)}
        onOpenAIQuickTrack={() => setViewMode('radar')}
        nudges={nudges}
        onSelectNudgeApp={handleSelectNudgeApp}
        onRefreshNudges={fetchNudgesOnly}
        totalApps={applications.length}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        
        {/* Metric Bar & Search Bar */}
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          
          {/* Quick HUD Metrics */}
          <div className="flex items-center gap-3 overflow-x-auto w-full md:w-auto pb-1">
            <div className="glass-stellar px-4 py-2 rounded-2xl flex items-center gap-3 border border-sky-500/20 shrink-0">
              <div className="w-8 h-8 rounded-xl bg-sky-950/90 border border-sky-600/40 flex items-center justify-center text-sky-400">
                <TrendingUp className="w-4 h-4" />
              </div>
              <div>
                <span className="text-[10px] uppercase font-black text-slate-400 block tracking-wider">Total Pipeline</span>
                <span className="text-sm font-black text-white">{stats.total}</span>
              </div>
            </div>

            <div className="glass-stellar px-4 py-2 rounded-2xl flex items-center gap-3 border border-amber-500/20 shrink-0">
              <div className="w-8 h-8 rounded-xl bg-amber-950/90 border border-amber-600/40 flex items-center justify-center text-amber-400">
                <Zap className="w-4 h-4" />
              </div>
              <div>
                <span className="text-[10px] uppercase font-black text-slate-400 block tracking-wider">Interviews</span>
                <span className="text-sm font-black text-amber-300">{stats.interview}</span>
              </div>
            </div>

            <div className="glass-stellar px-4 py-2 rounded-2xl flex items-center gap-3 border border-emerald-500/20 shrink-0">
              <div className="w-8 h-8 rounded-xl bg-emerald-950/90 border border-emerald-600/40 flex items-center justify-center text-emerald-400">
                <Award className="w-4 h-4" />
              </div>
              <div>
                <span className="text-[10px] uppercase font-black text-slate-400 block tracking-wider">Offers Landed</span>
                <span className="text-sm font-black text-emerald-300">{stats.offer}</span>
              </div>
            </div>
          </div>

          {/* Search Bar & Manual Reload */}
          <div className="flex items-center gap-2 w-full md:w-auto">
            <div className="relative flex-1 md:w-64">
              <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-2.5" />
              <input
                type="text"
                placeholder="Search company or role..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-900/90 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
              />
            </div>

            <button
              onClick={fetchData}
              className="p-2 rounded-xl bg-slate-900 border border-slate-700 hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
              title="Refresh Pipeline"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-sky-400' : ''}`} />
            </button>
          </div>

        </div>

        {/* View Content Renderer */}
        {loading && applications.length === 0 ? (
          <div className="py-24 text-center">
            <Orbit className="w-10 h-10 animate-spin text-sky-400 mx-auto mb-3" />
            <p className="text-xs uppercase tracking-widest text-slate-400 font-extrabold">Loading Applications...</p>
          </div>
        ) : (
          <>
            {viewMode === 'solar' && (
              <SolarOrbitView
                applications={filteredApps}
                onSelectApplication={setSelectedApp}
                onQuickAdvance={handleStatusChange}
              />
            )}

            {viewMode === 'kanban' && (
              <KanbanBoard
                applications={filteredApps}
                onSelectApplication={setSelectedApp}
                onStatusChange={handleStatusChange}
              />
            )}

            {viewMode === 'radar' && (
              <AIJobRadar
                onSelectApplication={setSelectedApp}
                onRefresh={fetchData}
              />
            )}
          </>
        )}

      </main>

      {/* Modals */}
      {selectedApp && (
        <ApplicationModal
          application={selectedApp}
          onClose={() => setSelectedApp(null)}
          onUpdateStatus={(st) => handleStatusChange(selectedApp.id, st)}
          onRefresh={fetchData}
        />
      )}

      {showNewAppModal && (
        <NewApplicationModal
          onClose={() => setShowNewAppModal(false)}
          onSuccess={fetchData}
        />
      )}

      {showImportModal && (
        <ImportModal
          onClose={() => setShowImportModal(false)}
          onSuccess={fetchData}
        />
      )}

      {showSettingsModal && (
        <SettingsModal
          onClose={() => setShowSettingsModal(false)}
        />
      )}

    </div>
  );
};
