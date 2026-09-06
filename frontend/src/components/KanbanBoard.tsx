import React from 'react';
import { ApplicationCard } from './ApplicationCard';
import { CheckCircle, Clock, Award, XCircle } from 'lucide-react';

interface KanbanBoardProps {
  applications: any[];
  onSelectApplication: (app: any) => void;
  onStatusChange: (appId: string, newStatus: string) => void;
}

const COLUMNS = [
  { 
    id: 'applied', 
    title: 'Applied', 
    color: 'border-sky-500/40 text-sky-400 bg-sky-950/20',
    icon: Clock,
    description: 'Submitted applications'
  },
  { 
    id: 'interview', 
    title: 'Interview', 
    color: 'border-amber-500/40 text-amber-400 bg-amber-950/20',
    icon: Award,
    description: 'Screening & Technical loops'
  },
  { 
    id: 'offer', 
    title: 'Offer', 
    color: 'border-emerald-500/40 text-emerald-400 bg-emerald-950/20',
    icon: CheckCircle,
    description: 'Offers received'
  },
  { 
    id: 'rejected', 
    title: 'Rejected', 
    color: 'border-rose-500/40 text-rose-400 bg-rose-950/20',
    icon: XCircle,
    description: 'Archived / Passed'
  }
];

export const KanbanBoard: React.FC<KanbanBoardProps> = ({
  applications,
  onSelectApplication,
  onStatusChange
}) => {
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent, targetStatus: string) => {
    e.preventDefault();
    const appId = e.dataTransfer.getData('text/plain');
    if (appId) {
      onStatusChange(appId, targetStatus);
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
      {COLUMNS.map((col) => {
        const IconComponent = col.icon;
        const columnApps = applications.filter((app) => (app.status || 'applied') === col.id);

        return (
          <div
            key={col.id}
            onDragOver={handleDragOver}
            onDrop={(e) => handleDrop(e, col.id)}
            className="flex flex-col h-full rounded-2xl glass-panel p-3.5 border border-slate-800"
          >
            {/* Column Header */}
            <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-800/80 px-1">
              <div className="flex items-center gap-2">
                <div className={`p-1.5 rounded-lg border ${col.color}`}>
                  <IconComponent className="w-3.5 h-3.5" />
                </div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                  {col.title}
                </h3>
              </div>
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-800/80 text-slate-300 border border-slate-700/60">
                {columnApps.length}
              </span>
            </div>

            {/* Application Cards List */}
            <div className="flex-1 space-y-3 overflow-y-auto max-h-[calc(100vh-250px)] pr-1">
              {columnApps.length === 0 ? (
                <div className="h-32 border-2 border-dashed border-slate-800/60 rounded-xl flex items-center justify-center text-xs text-slate-500 font-medium">
                  No applications here
                </div>
              ) : (
                columnApps.map((app) => (
                  <div
                    key={app.id}
                    draggable
                    onDragStart={(e) => {
                      e.dataTransfer.setData('text/plain', app.id);
                    }}
                  >
                    <ApplicationCard
                      application={app}
                      onClick={() => onSelectApplication(app)}
                    />
                  </div>
                ))
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};
