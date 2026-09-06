import React, { useState, useEffect } from 'react';
import { apiRequest } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { 
  X, 
  Sparkles, 
  Send, 
  Building2, 
  History, 
  FileText, 
  Copy, 
  Check, 
  AlertCircle,
  RefreshCw,
  MailCheck,
  Zap,
  Award,
  Flame,
  BrainCircuit,
  Compass
} from 'lucide-react';

interface ApplicationModalProps {
  application: any;
  onClose: () => void;
  onUpdateStatus: (newStatus: string) => Promise<void>;
  onRefresh: () => void;
}

export const ApplicationModal: React.FC<ApplicationModalProps> = ({
  application,
  onClose,
  onUpdateStatus,
  onRefresh
}) => {
  const { token } = useAuth();
  const [drafts, setDrafts] = useState<any[]>([]);
  const [loadingDrafts, setLoadingDrafts] = useState(true);
  const [generatingType, setGeneratingType] = useState<string | null>(null);
  const [copiedDraftId, setCopiedDraftId] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const fetchDrafts = async () => {
    try {
      setLoadingDrafts(true);
      const data = await apiRequest(`/applications/${application.id}/drafts`, { token });
      setDrafts(data || []);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoadingDrafts(false);
    }
  };

  useEffect(() => {
    fetchDrafts();
  }, [application.id]);

  const handleGenerate = async (type: string) => {
    try {
      setGeneratingType(type);
      setErrorMsg(null);
      await apiRequest(`/applications/${application.id}/drafts/generate`, {
        method: 'POST',
        token,
        body: JSON.stringify({ type })
      });
      await fetchDrafts();
    } catch (err: any) {
      setErrorMsg(err.message || 'AI Generation failed.');
    } finally {
      setGeneratingType(null);
    }
  };

  const handleUpdateDraftStatus = async (draftId: string, status: string) => {
    try {
      await apiRequest(`/applications/${application.id}/drafts/${draftId}`, {
        method: 'PATCH',
        token,
        body: JSON.stringify({ status })
      });
      await fetchDrafts();
    } catch (err: any) {
      console.error(err);
    }
  };

  const copyToClipboard = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedDraftId(id);
    setTimeout(() => setCopiedDraftId(null), 2500);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-xl animate-in fade-in duration-150">
      <div className="glass-stellar w-full max-w-4xl max-h-[92vh] rounded-3xl flex flex-col border border-sky-500/30 shadow-2xl overflow-hidden">
        
        {/* Modal Header */}
        <div className="p-6 border-b border-slate-800 flex items-start justify-between bg-slate-900/80 relative">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-sky-600 to-indigo-600 border border-sky-400/30 flex items-center justify-center text-white shrink-0 shadow-lg shadow-sky-500/20">
              <Building2 className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <h2 className="text-xl font-black text-white tracking-tight font-['Plus_Jakarta_Sans',sans-serif]">
                  {application.company}
                </h2>
                <span className="text-xs uppercase tracking-wider font-extrabold px-2.5 py-0.5 rounded-full bg-sky-950 text-sky-300 border border-sky-800">
                  {application.status} Zone
                </span>
              </div>
              <p className="text-xs font-semibold text-slate-300">{application.role}</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white rounded-xl hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {errorMsg && (
            <div className="p-3 rounded-2xl bg-rose-950/60 border border-rose-800/80 text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* Planetary Orbit Status Transition */}
          <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 flex flex-wrap items-center justify-between gap-4">
            <div>
              <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider block mb-1.5">
                Orbital Trajectory State
              </span>
              <div className="flex items-center gap-2">
                {['applied', 'interview', 'offer', 'rejected'].map((st) => (
                  <button
                    key={st}
                    disabled={application.status === st}
                    onClick={() => onUpdateStatus(st)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-bold uppercase tracking-wider transition-all ${
                      application.status === st
                        ? 'bg-gradient-to-r from-sky-600 to-indigo-600 text-white shadow-md shadow-sky-500/30'
                        : 'bg-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-700/80 border border-slate-700/60'
                    }`}
                  >
                    {st}
                  </button>
                ))}
              </div>
            </div>

            {/* AI Generator Buttons */}
            <div className="flex flex-wrap items-center gap-2">
              <button
                disabled={!!generatingType}
                onClick={() => handleGenerate('cover_letter')}
                className="px-3.5 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 text-white shadow-lg shadow-sky-500/20 transition-all flex items-center gap-1.5 disabled:opacity-50"
              >
                {generatingType === 'cover_letter' ? (
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Sparkles className="w-3.5 h-3.5 text-sky-200" />
                )}
                AI Cover Letter
              </button>

              <button
                disabled={!!generatingType}
                onClick={() => handleGenerate('follow_up_email')}
                className="px-3.5 py-2 rounded-xl text-xs font-bold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all flex items-center gap-1.5 disabled:opacity-50"
              >
                {generatingType === 'follow_up_email' ? (
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Send className="w-3.5 h-3.5 text-amber-400" />
                )}
                AI Follow-up
              </button>
            </div>
          </div>

          {/* Job Description */}
          {application.jobDescription && (
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                Job Requirements & Specs
              </h3>
              <div className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800 text-xs text-slate-300 max-h-48 overflow-y-auto leading-relaxed whitespace-pre-wrap font-mono">
                {application.jobDescription}
              </div>
            </div>
          )}

          {/* AI Generated Drafts List */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                <FileText className="w-4 h-4 text-sky-400" /> Generated Artifacts & Transmissions ({drafts.length})
              </h3>
            </div>

            {loadingDrafts ? (
              <div className="py-8 text-center text-xs text-slate-400 flex items-center justify-center gap-2">
                <RefreshCw className="w-4 h-4 animate-spin text-sky-400" /> Loading orbital drafts...
              </div>
            ) : drafts.length === 0 ? (
              <div className="p-8 rounded-2xl border border-dashed border-slate-800 text-center text-xs text-slate-500">
                No drafts generated yet. Click "AI Cover Letter" to craft your first tailored transmission.
              </div>
            ) : (
              <div className="space-y-4">
                {drafts.map((draft) => (
                  <div
                    key={draft.id}
                    className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-md space-y-3"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-sky-300 uppercase">
                          {draft.type === 'cover_letter' ? 'Cover Letter' : 'Follow-up Email'}
                        </span>
                        <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
                          {draft.generationModel || 'Gemini'}
                        </span>
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ${
                          draft.status === 'sent' 
                            ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' 
                            : 'bg-slate-800 text-slate-300'
                        }`}>
                          {draft.status}
                        </span>
                      </div>

                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => copyToClipboard(draft.id, draft.contents)}
                          className="px-2.5 py-1 rounded-xl text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center gap-1 border border-slate-700 transition-colors"
                        >
                          {copiedDraftId === draft.id ? (
                            <>
                              <Check className="w-3 h-3 text-emerald-400" /> Copied
                            </>
                          ) : (
                            <>
                              <Copy className="w-3 h-3" /> Copy
                            </>
                          )}
                        </button>

                        {draft.status !== 'sent' && (
                          <button
                            onClick={() => handleUpdateDraftStatus(draft.id, 'sent')}
                            className="px-2.5 py-1 rounded-xl text-xs bg-emerald-950/80 hover:bg-emerald-900 text-emerald-300 border border-emerald-800 flex items-center gap-1 transition-colors"
                          >
                            <MailCheck className="w-3 h-3" /> Mark Sent
                          </button>
                        )}
                      </div>
                    </div>

                    <div className="p-3.5 rounded-xl bg-slate-950/90 border border-slate-800 text-xs text-slate-200 font-mono whitespace-pre-wrap max-h-60 overflow-y-auto leading-relaxed">
                      {draft.contents}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Timeline History */}
          {application.statusHistory && application.statusHistory.length > 0 && (
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
                <History className="w-3.5 h-3.5 text-slate-500" /> Orbital Transition Log
              </h3>
              <div className="space-y-2">
                {application.statusHistory.map((item: any, idx: number) => (
                  <div key={idx} className="flex items-center gap-3 text-xs text-slate-400">
                    <span className="w-2 h-2 rounded-full bg-sky-400"></span>
                    <span className="font-bold text-slate-200 uppercase">{item.status}</span>
                    <span className="text-[11px] text-slate-500">
                      {item.changedAt ? new Date(item.changedAt).toLocaleString() : ''}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>

      </div>
    </div>
  );
};
