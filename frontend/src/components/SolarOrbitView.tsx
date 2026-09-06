import React, { useState } from 'react';
import { 
  Building2, 
  Sparkles, 
  ChevronRight, 
  Clock, 
  AlertCircle, 
  Zap, 
  Flame, 
  CheckCircle,
  XCircle,
  Award,
  ArrowRight,
  Filter,
  CheckCircle2,
  Calendar
} from 'lucide-react';

interface SolarOrbitViewProps {
  applications: any[];
  onSelectApplication: (app: any) => void;
  onQuickAdvance: (appId: string, targetStatus: string) => void;
}

const STAGES = [
  {
    id: 'all',
    name: 'All Applied Jobs',
    subtitle: 'Full list of every application submitted',
    badge: 'bg-sky-500/20 text-sky-300 border-sky-500/40',
    color: 'from-sky-500/20 to-indigo-600/10 border-sky-500/30 text-sky-400',
    icon: Building2
  },
  {
    id: 'applied',
    name: 'Applied / In Review',
    subtitle: 'Submitted applications under review',
    badge: 'bg-blue-500/20 text-blue-300 border-blue-500/40',
    color: 'from-blue-500/20 to-sky-600/10 border-blue-500/30 text-blue-400',
    icon: Clock
  },
  {
    id: 'interview',
    name: 'Interview Rounds',
    subtitle: 'Technical loops & screening rounds',
    badge: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
    color: 'from-amber-500/20 to-orange-600/10 border-amber-500/30 text-amber-400',
    icon: Zap
  },
  {
    id: 'offer',
    name: 'Offers Received',
    subtitle: 'Active job offers landed',
    badge: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
    color: 'from-emerald-500/20 to-teal-600/10 border-emerald-500/30 text-emerald-400',
    icon: Award
  },
  {
    id: 'rejected',
    name: 'Archived / Passed',
    subtitle: 'Archived for future reference',
    badge: 'bg-rose-500/20 text-rose-300 border-rose-500/40',
    color: 'from-rose-500/20 to-slate-900/40 border-rose-500/30 text-rose-400',
    icon: XCircle
  }
];

export const SolarOrbitView: React.FC<SolarOrbitViewProps> = ({
  applications,
  onSelectApplication,
  onQuickAdvance
}) => {
  const [selectedStage, setSelectedStage] = useState<string>('all');

  const getDaysAgo = (dateStr: string) => {
    if (!dateStr) return 0;
    const diff = new Date().getTime() - new Date(dateStr).getTime();
    return Math.floor(diff / (1000 * 60 * 60 * 24));
  };

  const displayedApplications = selectedStage === 'all' 
    ? applications 
    : applications.filter(a => (a.status || 'applied') === selectedStage);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'interview':
        return { text: 'Interview', bg: 'bg-amber-950/80 text-amber-300 border-amber-700/50' };
      case 'offer':
        return { text: 'Offer', bg: 'bg-emerald-950/80 text-emerald-300 border-emerald-700/50' };
      case 'rejected':
        return { text: 'Rejected', bg: 'bg-rose-950/80 text-rose-300 border-rose-700/50' };
      default:
        return { text: 'Applied', bg: 'bg-sky-950/80 text-sky-300 border-sky-700/50' };
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Visual Solar Core Header */}
      <div className="relative glass-stellar rounded-3xl p-6 overflow-hidden flex flex-col md:flex-row items-center justify-between border border-sky-500/20 shadow-2xl gap-6">
        
        <div className="flex items-center gap-4 relative z-10">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-amber-400 via-orange-500 to-rose-600 flex items-center justify-center shadow-[0_0_40px_rgba(245,158,11,0.5)] border border-amber-300/60 shrink-0">
            <Flame className="w-8 h-8 text-white animate-pulse" />
          </div>
          <div>
            <h2 className="text-xl font-black text-white tracking-tight font-['Plus_Jakarta_Sans',sans-serif]">
              Job Application Command Center
            </h2>
            <p className="text-xs text-slate-300 mt-0.5">
              Tracking <span className="text-sky-400 font-bold">{applications.length}</span> total applications in your pipeline.
            </p>
          </div>
        </div>

        {/* Quick Filter Buttons */}
        <div className="flex flex-wrap items-center gap-2 relative z-10">
          {STAGES.map((stage) => {
            const count = stage.id === 'all' 
              ? applications.length 
              : applications.filter(a => (a.status || 'applied') === stage.id).length;
            const isSelected = selectedStage === stage.id;

            return (
              <button
                key={stage.id}
                onClick={() => setSelectedStage(stage.id)}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
                  isSelected
                    ? 'bg-gradient-to-r from-sky-600 to-indigo-600 text-white shadow-lg shadow-sky-500/25 border border-sky-400/40'
                    : 'bg-slate-900/80 text-slate-400 hover:text-slate-200 border border-slate-800'
                }`}
              >
                <span>{stage.name}</span>
                <span className={`text-[10px] px-1.5 py-0.2 rounded-full font-mono ${isSelected ? 'bg-white/20 text-white' : 'bg-slate-800 text-slate-300'}`}>
                  {count}
                </span>
              </button>
            );
          })}
        </div>

      </div>

      {/* Applications List Header */}
      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
          <Building2 className="w-4 h-4 text-sky-400" />
          {selectedStage === 'all' ? 'All Applications' : STAGES.find(s => s.id === selectedStage)?.name} ({displayedApplications.length})
        </h3>
        <span className="text-xs text-slate-400">Click any card for AI cover letter & follow-up options</span>
      </div>

      {/* Grid of All Applied Applications */}
      {displayedApplications.length === 0 ? (
        <div className="p-12 rounded-3xl border border-dashed border-slate-800 text-center space-y-3 bg-slate-900/40">
          <Building2 className="w-10 h-10 text-slate-600 mx-auto" />
          <h4 className="text-sm font-bold text-slate-300">No applications found in this category</h4>
          <p className="text-xs text-slate-500">Click "AI Job Scanner" at the top to apply to target roles in 1 click.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {displayedApplications.map((app) => {
            const daysAgo = getDaysAgo(app.updatedAt || app.applicationDate);
            const isStale = (app.status === 'applied' || !app.status) && daysAgo >= 5;
            const badge = getStatusBadge(app.status || 'applied');

            return (
              <div
                key={app.id}
                className="planet-card p-5 rounded-3xl cursor-pointer flex flex-col justify-between group relative overflow-hidden border border-slate-800 hover:border-sky-500/40 shadow-lg transition-all"
                onClick={() => onSelectApplication(app)}
              >
                <div>
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div className="flex items-center gap-2.5 min-w-0">
                      <div className="w-9 h-9 rounded-xl bg-slate-800/90 border border-slate-700 flex items-center justify-center text-sky-400 font-bold text-xs group-hover:scale-105 group-hover:border-sky-500 transition-all shrink-0">
                        <Building2 className="w-4 h-4" />
                      </div>
                      <div className="min-w-0">
                        <h4 className="text-sm font-bold text-white truncate group-hover:text-sky-300 transition-colors">
                          {app.company}
                        </h4>
                        <p className="text-xs font-semibold text-slate-300 truncate">{app.role}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-1 shrink-0">
                      <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full border ${badge.bg}`}>
                        {badge.text}
                      </span>
                      {isStale && (
                        <span className="flex items-center gap-1 text-[10px] font-bold bg-amber-950/80 text-amber-300 border border-amber-700/60 px-1.5 py-0.5 rounded-full animate-pulse">
                          <AlertCircle className="w-2.5 h-2.5" /> Nudge
                        </span>
                      )}
                    </div>
                  </div>

                  {app.jobDescription && (
                    <p className="text-xs text-slate-400 line-clamp-2 mb-3 leading-relaxed">
                      {app.jobDescription}
                    </p>
                  )}
                </div>

                {/* Card Footer */}
                <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                  <div className="flex items-center gap-1.5 text-[11px] text-slate-500">
                    <Calendar className="w-3 h-3 text-slate-500" />
                    <span>Applied {daysAgo}d ago</span>
                  </div>

                  <div className="flex items-center gap-1.5" onClick={(e) => e.stopPropagation()}>
                    {app.status === 'applied' && (
                      <button
                        onClick={() => onQuickAdvance(app.id, 'interview')}
                        className="px-2.5 py-1 rounded-xl text-[10px] font-bold uppercase tracking-wider bg-amber-950/80 hover:bg-amber-900 text-amber-300 border border-amber-700/50 flex items-center gap-1 transition-all"
                        title="Move to Interview"
                      >
                        <Zap className="w-3 h-3" /> Interview
                      </button>
                    )}

                    {app.status === 'interview' && (
                      <button
                        onClick={() => onQuickAdvance(app.id, 'offer')}
                        className="px-2.5 py-1 rounded-xl text-[10px] font-bold uppercase tracking-wider bg-emerald-950/80 hover:bg-emerald-900 text-emerald-300 border border-emerald-700/50 flex items-center gap-1 transition-all"
                        title="Move to Offer"
                      >
                        <Award className="w-3 h-3" /> Offer Landed
                      </button>
                    )}

                    <button
                      onClick={() => onSelectApplication(app)}
                      className="p-1 rounded-xl hover:bg-slate-800 text-slate-400 hover:text-sky-300 transition-colors"
                    >
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>

              </div>
            );
          })}
        </div>
      )}

    </div>
  );
};
