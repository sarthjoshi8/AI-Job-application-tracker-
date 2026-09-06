import React, { useState } from 'react';
import { apiRequest } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { 
  X, 
  UploadCloud, 
  CheckCircle2, 
  AlertCircle, 
  RefreshCw,
  FileCode,
  FileText,
  FileType,
  Image as ImageIcon,
  Sparkles
} from 'lucide-react';

interface ImportModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

export const ImportModal: React.FC<ImportModalProps> = ({ onClose, onSuccess }) => {
  const { token } = useAuth();
  const [activeTab, setActiveTab] = useState<'postings' | 'drafts'>('postings');
  const [file, setFile] = useState<File | null>(null);
  const [rawText, setRawText] = useState('');
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<any | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const samplePostingsCsv = `id,company,role,date,jobDescription
post-1,Google DeepMind,Staff AI Research Engineer,2026-08-20,Designing autonomous reasoning agents, Vertex AI context grounding, and multi-tenant LLM evaluation loops.
post-2,Anthropic,Distributed Systems & AI Architect,2026-08-22,Building low-latency inference clusters, GPU/TPU interconnects, and prompt evaluation benchmarks.
post-3,Stripe,Lead ML Platform Engineer,2026-08-25,Real-time transaction fraud intelligence, distributed Python/Go microservices, and Spanner infrastructure.`;

  const sampleDraftsCsv = `id,jobId,type,contents,status
draft-1,post-1,cover_letter,I am eager to contribute my Vertex AI & agentic workflow architecture experience to the DeepMind frontier team.,draft
draft-2,post-2,cover_letter,My extensive background in high-throughput cloud infrastructure and low-latency inference aligns with Anthropic.,draft`;

  const handleImport = async () => {
    try {
      setLoading(true);
      setErrorMsg(null);
      setReport(null);

      const endpoint = activeTab === 'postings' ? '/import/postings' : '/import/drafts';
      let options: any = { method: 'POST', token };

      if (file) {
        const formData = new FormData();
        formData.append('file', file);
        options.body = formData;
      } else {
        if (!rawText.trim()) {
          throw new Error('Please select a file or paste CSV/JSON/Document text.');
        }
        options.body = rawText;
        options.headers = { 'Content-Type': rawText.trim().startsWith('[') ? 'application/json' : 'text/csv' };
      }

      const res = await apiRequest(endpoint, options);
      setReport(res);
      onSuccess();
    } catch (err: any) {
      setErrorMsg(err.message || 'Import failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-xl">
      <div className="glass-stellar w-full max-w-2xl rounded-3xl flex flex-col border border-sky-500/30 shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-900/80">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-2xl bg-gradient-to-tr from-sky-600 to-indigo-600 text-white shadow-lg shadow-sky-500/20">
              <UploadCloud className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white font-['Plus_Jakarta_Sans',sans-serif]">
                Multi-Format Ingestion Engine
              </h3>
              <p className="text-xs text-slate-400">
                Supports <span className="text-sky-300 font-semibold">PDF, DOC, DOCX, Images, CSV, and JSON</span>
              </p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white p-1 rounded-xl">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Selection */}
        <div className="flex border-b border-slate-800 bg-slate-950/60 px-6 pt-3">
          <button
            onClick={() => { setActiveTab('postings'); setReport(null); }}
            className={`pb-2.5 px-4 text-xs font-bold uppercase tracking-wider transition-all border-b-2 ${
              activeTab === 'postings'
                ? 'border-sky-500 text-sky-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            Job Postings & Roles
          </button>
          <button
            onClick={() => { setActiveTab('drafts'); setReport(null); }}
            className={`pb-2.5 px-4 text-xs font-bold uppercase tracking-wider transition-all border-b-2 ${
              activeTab === 'drafts'
                ? 'border-sky-500 text-sky-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            Drafts & Cover Letters
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-4 max-h-[72vh] overflow-y-auto">
          {errorMsg && (
            <div className="p-3 rounded-2xl bg-rose-950/60 border border-rose-800/80 text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* Ingestion Report Banner */}
          {report && (
            <div className="p-4 rounded-2xl bg-emerald-950/70 border border-emerald-500/40 text-emerald-300 space-y-2">
              <div className="flex items-center gap-2 font-bold text-xs text-emerald-200">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Document Ingested Into Orbit Successfully
              </div>
              <div className="grid grid-cols-4 gap-2 text-center text-xs">
                <div className="p-2 rounded-xl bg-emerald-900/40 border border-emerald-800/40">
                  <span className="block text-slate-200 font-black">{report.rows_received}</span>
                  <span className="text-[10px] text-emerald-400">Processed</span>
                </div>
                <div className="p-2 rounded-xl bg-emerald-900/40 border border-emerald-800/40">
                  <span className="block text-emerald-300 font-black">{report.rows_created}</span>
                  <span className="text-[10px] text-emerald-400">Created</span>
                </div>
                <div className="p-2 rounded-xl bg-emerald-900/40 border border-emerald-800/40">
                  <span className="block text-sky-300 font-black">{report.rows_updated}</span>
                  <span className="text-[10px] text-sky-400">Updated</span>
                </div>
                <div className="p-2 rounded-xl bg-emerald-900/40 border border-emerald-800/40">
                  <span className="block text-amber-300 font-black">{report.rows_flagged}</span>
                  <span className="text-[10px] text-amber-400">Flagged</span>
                </div>
              </div>
            </div>
          )}

          {/* Supported Formats Visual Badge */}
          <div className="p-3 rounded-2xl bg-slate-900/80 border border-slate-800 flex items-center justify-around text-xs text-slate-400">
            <span className="flex items-center gap-1 text-rose-400 font-medium">
              <FileType className="w-3.5 h-3.5" /> PDF (.pdf)
            </span>
            <span className="flex items-center gap-1 text-sky-400 font-medium">
              <FileText className="w-3.5 h-3.5" /> Word (.doc, .docx)
            </span>
            <span className="flex items-center gap-1 text-amber-400 font-medium">
              <ImageIcon className="w-3.5 h-3.5" /> Images (.png, .jpg)
            </span>
            <span className="flex items-center gap-1 text-emerald-400 font-medium">
              <FileCode className="w-3.5 h-3.5" /> CSV & JSON
            </span>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
              Select Document or Spreadsheet
            </label>
            <input
              type="file"
              accept=".pdf,.doc,.docx,.png,.jpg,.jpeg,.csv,.json,.txt"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="block w-full text-xs text-slate-400 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-sky-950 file:text-sky-300 hover:file:bg-sky-900 border border-slate-700/80 rounded-2xl p-2 bg-slate-900/60"
            />
          </div>

          <div className="relative flex py-1 items-center">
            <div className="flex-grow border-t border-slate-800"></div>
            <span className="flex-shrink mx-4 text-[10px] uppercase tracking-wider text-slate-500 font-bold">Or Paste Text Directly</span>
            <div className="flex-grow border-t border-slate-800"></div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-1.5">
              <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider">
                Raw Content / Document Text
              </label>
              <button
                type="button"
                onClick={() => setRawText(activeTab === 'postings' ? samplePostingsCsv : sampleDraftsCsv)}
                className="text-[11px] text-sky-400 hover:underline flex items-center gap-1 font-semibold"
              >
                <FileCode className="w-3 h-3" /> Load Sample Postings
              </button>
            </div>
            <textarea
              rows={5}
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              placeholder="Paste job descriptions, resume text, or CSV/JSON rows here..."
              className="w-full px-3.5 py-2.5 rounded-2xl bg-slate-900 border border-slate-700 text-white placeholder-slate-500 text-xs font-mono focus:outline-none focus:border-sky-500 leading-relaxed"
            />
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 flex justify-end gap-2 bg-slate-900/80">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
          >
            Close
          </button>
          <button
            onClick={handleImport}
            disabled={loading}
            className="px-5 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 text-white shadow-lg shadow-sky-600/30 transition-all flex items-center gap-2 disabled:opacity-50"
          >
            {loading ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Ingesting Document...
              </>
            ) : (
              <>
                <UploadCloud className="w-3.5 h-3.5" /> Start Ingestion
              </>
            )}
          </button>
        </div>

      </div>
    </div>
  );
};
