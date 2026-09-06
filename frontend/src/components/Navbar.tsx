import React, { useState } from 'react';
import { 
  Sparkles, 
  Orbit, 
  LayoutGrid, 
  Plus, 
  UploadCloud, 
  User as UserIcon, 
  Bell, 
  Radio, 
  Flame,
  CheckCheck,
  Check,
  Info,
  Zap,
  Award,
  XCircle
} from 'lucide-react';
import { apiRequest } from '../api/client';
import { useAuth } from '../context/AuthContext';

interface NavbarProps {
  viewMode: 'solar' | 'kanban' | 'radar';
  setViewMode: (mode: 'solar' | 'kanban' | 'radar') => void;
  onOpenNewApp: () => void;
  onOpenImport: () => void;
  onOpenSettings: () => void;
  onOpenAIQuickTrack: () => void;
  nudges: any[];
  onSelectNudgeApp: (appId: string) => void;
  onRefreshNudges: () => void;
  totalApps: number;
}

export const Navbar: React.FC<NavbarProps> = ({
  viewMode,
  setViewMode,
  onOpenNewApp,
  onOpenImport,
  onOpenSettings,
  onOpenAIQuickTrack,
  nudges,
  onSelectNudgeApp,
  onRefreshNudges,
  totalApps
}) => {
  const { token } = useAuth();
  const [showNudgesDropdown, setShowNudgesDropdown] = useState(false);
  const [markingAll, setMarkingAll] = useState(false);

  const pendingNudges = nudges.filter(n => n.status === 'pending');

  const handleMarkAllAsRead = async () => {
    try {
      setMarkingAll(true);
      await apiRequest('/nudges/mark-all-read', {
        method: 'POST',
        token
      });
      onRefreshNudges();
    } catch (err: any) {
      console.error('Error marking all notifications as read:', err);
    } finally {
      setMarkingAll(false);
    }
  };

  const handleMarkSingleRead = async (nudgeId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await apiRequest(`/nudges/${nudgeId}`, {
        method: 'PATCH',
        token,
        body: JSON.stringify({ status: 'read' })
      });
      onRefreshNudges();
    } catch (err: any) {
      console.error(err);
    }
  };

  return (
    <header className="glass-stellar sticky top-0 z-50 border-b border-sky-500/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand Logo */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-amber-500 via-orange-500 to-sky-600 flex items-center justify-center shadow-lg shadow-amber-500/20">
            <Flame className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-lg tracking-tight text-white font-['Plus_Jakarta_Sans',sans-serif]">
                AstroTrack<span className="text-sky-400">.ai</span>
              </span>
              <span className="px-2 py-0.5 text-[10px] font-bold bg-amber-950/80 text-amber-300 border border-amber-500/40 rounded-full flex items-center gap-1">
                <Sparkles className="w-2.5 h-2.5 text-amber-400" /> AI Job Tracker
              </span>
            </div>
            <p className="text-[11px] text-slate-400">Gemini Powered Career Co-Pilot</p>
          </div>
        </div>

        {/* View Switcher */}
        <div className="hidden md:flex items-center p-1 rounded-xl bg-slate-900/90 border border-slate-700/80 shadow-inner">
          <button
            onClick={() => setViewMode('solar')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all ${
              viewMode === 'solar'
                ? 'bg-gradient-to-r from-sky-600 to-indigo-600 text-white shadow-md shadow-sky-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Orbit className="w-3.5 h-3.5" />
            <span>Overview</span>
          </button>

          <button
            onClick={() => setViewMode('kanban')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all ${
              viewMode === 'kanban'
                ? 'bg-gradient-to-r from-sky-600 to-indigo-600 text-white shadow-md shadow-sky-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <LayoutGrid className="w-3.5 h-3.5" />
            <span>Kanban Board</span>
          </button>

          <button
            onClick={() => setViewMode('radar')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all ${
              viewMode === 'radar'
                ? 'bg-gradient-to-r from-sky-600 to-indigo-600 text-white shadow-md shadow-sky-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Radio className="w-3.5 h-3.5 text-rose-400" />
            <span>AI Opportunities Queue</span>
          </button>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-2.5">
          <button
            onClick={onOpenAIQuickTrack}
            className="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-gradient-to-r from-amber-500 via-rose-500 to-indigo-600 text-white shadow-lg shadow-amber-500/25 hover:opacity-95 transition-all flex items-center gap-1.5 animate-pulse"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">AI Job Scanner</span>
          </button>

          <button
            onClick={onOpenNewApp}
            className="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-sky-600 hover:bg-sky-500 text-white shadow-md shadow-sky-600/30 transition-all flex items-center gap-1"
          >
            <Plus className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">+ Log Job</span>
          </button>

          <button
            onClick={onOpenImport}
            className="p-2 rounded-xl text-slate-300 hover:text-white hover:bg-slate-800/80 border border-slate-700/80 transition-all"
            title="Bulk Upload (PDF, Word, Images, CSV)"
          >
            <UploadCloud className="w-4 h-4" />
          </button>

          {/* Follow-up & Status Notifications Bell */}
          <div className="relative">
            <button
              onClick={() => setShowNudgesDropdown(!showNudgesDropdown)}
              className="p-2 rounded-xl text-slate-300 hover:text-white hover:bg-slate-800/80 border border-slate-700/80 transition-all relative"
              title="Notifications"
            >
              <Bell className="w-4 h-4" />
              {pendingNudges.length > 0 && (
                <span className="absolute -top-1 -right-1 w-4 h-4 bg-rose-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center animate-pulse">
                  {pendingNudges.length}
                </span>
              )}
            </button>

            {showNudgesDropdown && (
              <div className="absolute right-0 mt-2 w-80 sm:w-96 glass-stellar rounded-3xl shadow-2xl p-4 border border-sky-500/30 z-50 animate-in fade-in slide-in-from-top-2 duration-200">
                <div className="flex items-center justify-between pb-3 mb-2 border-b border-slate-800">
                  <div className="flex items-center gap-2">
                    <Bell className="w-4 h-4 text-sky-400" />
                    <span className="text-xs font-bold text-slate-200">
                      Notifications ({pendingNudges.length})
                    </span>
                  </div>

                  {pendingNudges.length > 0 && (
                    <button
                      onClick={handleMarkAllAsRead}
                      disabled={markingAll}
                      className="text-[11px] font-semibold text-sky-400 hover:text-sky-300 hover:underline flex items-center gap-1 transition-colors"
                    >
                      <CheckCheck className="w-3.5 h-3.5" />
                      <span>Mark all as read</span>
                    </button>
                  )}
                </div>

                {pendingNudges.length === 0 ? (
                  <div className="py-6 text-center text-xs text-slate-400">
                    <CheckCheck className="w-8 h-8 text-emerald-400 mx-auto mb-2 opacity-80" />
                    All notifications are read and up to date!
                  </div>
                ) : (
                  <div className="space-y-2.5 max-h-72 overflow-y-auto pr-1">
                    {pendingNudges.map(n => (
                      <div
                        key={n.id}
                        onClick={() => {
                          onSelectNudgeApp(n.applicationId);
                          setShowNudgesDropdown(false);
                        }}
                        className="p-3 rounded-2xl bg-slate-900/90 border border-slate-800 hover:border-sky-500/50 cursor-pointer transition-all flex flex-col justify-between space-y-2 group"
                      >
                        <div className="flex justify-between items-start">
                          <div>
                            <span className="text-xs font-bold text-sky-300 group-hover:text-sky-200">
                              {n.company || "Job Update"}
                            </span>
                            {n.role && (
                              <span className="text-[10px] text-slate-400 block">{n.role}</span>
                            )}
                          </div>

                          <button
                            onClick={(e) => handleMarkSingleRead(n.id, e)}
                            className="p-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-emerald-400 transition-colors"
                            title="Mark as read"
                          >
                            <Check className="w-3 h-3" />
                          </button>
                        </div>

                        <p className="text-[11px] text-slate-300 leading-relaxed">{n.message}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          <button
            onClick={onOpenSettings}
            className="p-2 rounded-xl text-slate-300 hover:text-white hover:bg-slate-800/80 border border-slate-700/80 transition-all"
            title="Profile & AI Settings"
          >
            <UserIcon className="w-4 h-4" />
          </button>
        </div>

      </div>
    </header>
  );
};
