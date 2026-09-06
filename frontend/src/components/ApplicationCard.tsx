import React from 'react';
import { 
  Building2, 
  Calendar, 
  Sparkles, 
  ChevronRight, 
  Clock, 
  FileText,
  AlertCircle
} from 'lucide-react';

interface ApplicationCardProps {
  application: any;
  onClick: () => void;
  onQuickTransition?: (newStatus: string) => void;
}

export const ApplicationCard: React.FC<ApplicationCardProps> = ({
  application,
  onClick,
  onQuickTransition
}) => {
  const getDaysSince = (dateStr: string) => {
    if (!dateStr) return 0;
    const diff = new Date().getTime() - new Date(dateStr).getTime();
    return Math.floor(diff / (1000 * 60 * 60 * 24));
  };

  const daysSinceApplied = getDaysSince(application.applicationDate);
  const daysSinceUpdated = getDaysSince(application.updatedAt);
  const isStale = application.status === 'applied' && daysSinceUpdated >= 5;

  return (
    <div
      onClick={onClick}
      className="glass-card p-4 rounded-xl hover:border-sky-500/50 hover:bg-slate-800/80 transition-all cursor-pointer group shadow-sm hover:shadow-lg hover:shadow-sky-500/5 flex flex-col justify-between"
    >
      <div>
        {/* Company & Stale Warning Badge */}
        <div className="flex items-start justify-between gap-2 mb-2">
          <div className="flex items-center gap-2 min-w-0">
            <div className="w-7 h-7 rounded-lg bg-slate-800 border border-slate-700/80 flex items-center justify-center text-slate-300 group-hover:text-sky-400 group-hover:border-sky-500/40 transition-all shrink-0">
              <Building2 className="w-4 h-4" />
            </div>
            <h4 className="text-sm font-semibold text-white truncate group-hover:text-sky-300 transition-colors">
              {application.company}
            </h4>
          </div>

          {isStale && (
            <span className="shrink-0 flex items-center gap-1 text-[10px] font-semibold bg-amber-950/70 text-amber-300 border border-amber-800/60 px-2 py-0.5 rounded-full animate-pulse">
              <AlertCircle className="w-2.5 h-2.5" /> Follow-up
            </span>
          )}
        </div>

        {/* Role Title */}
        <p className="text-xs font-medium text-slate-300 line-clamp-1 mb-2">
          {application.role}
        </p>

        {/* Snippet / tags */}
        {application.jobDescription && (
          <p className="text-[11px] text-slate-400 line-clamp-2 mb-3 leading-relaxed">
            {application.jobDescription}
          </p>
        )}
      </div>

      <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
        <div className="flex items-center gap-1.5">
          <Calendar className="w-3 h-3 text-slate-500" />
          <span>{application.applicationDate ? new Date(application.applicationDate).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : 'Recent'}</span>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[10px] text-slate-500 flex items-center gap-1">
            <Clock className="w-2.5 h-2.5" /> {daysSinceUpdated}d ago
          </span>
          <ChevronRight className="w-3.5 h-3.5 text-slate-600 group-hover:text-sky-400 group-hover:translate-x-0.5 transition-all" />
        </div>
      </div>
    </div>
  );
};
