import React, { useState } from 'react';
import { 
  Sparkles, 
  Search, 
  BrainCircuit, 
  Building2, 
  CheckCircle2, 
  ArrowRight, 
  Layers, 
  PlusCircle, 
  Clock, 
  Rocket, 
  CheckSquare, 
  Square,
  RefreshCw
} from 'lucide-react';
import { apiRequest } from '../api/client';
import { useAuth } from '../context/AuthContext';

interface AIJobRadarProps {
  onSelectApplication: (app: any) => void;
  onRefresh: () => void;
}

const AI_OPPORTUNITIES_DATABASE = [
  {
    id: "opp-1",
    company: "Google DeepMind",
    role: "Staff AI Research Engineer — Autonomous Agents",
    tier: "Tier 1 Planetary Frontier",
    matchScore: 98,
    skills: ["Vertex AI", "Gemini 2.5", "Agentic Systems", "Cloud Run"],
    salary: "$280k - $380k",
    description: "Architecting self-evaluating autonomous agent loops, KV cache latency optimization, and multi-tenant reasoning infrastructure."
  },
  {
    id: "opp-2",
    company: "Anthropic",
    role: "Applied AI Systems Architect",
    tier: "Tier 1 Planetary Frontier",
    matchScore: 96,
    skills: ["Claude API", "Python", "Low-Latency Inference", "GCP"],
    salary: "$270k - $360k",
    description: "Scaling high-concurrency tool-use loops, prompt grounding benchmarks, and safety-aligned enterprise evaluation frameworks."
  },
  {
    id: "opp-3",
    company: "OpenAI",
    role: "Distributed Training & Inference Engineer",
    tier: "Tier 1 Planetary Frontier",
    matchScore: 95,
    skills: ["CUDA", "PyTorch", "Kubernetes", "Low Latency"],
    salary: "$290k - $410k",
    description: "Designing high-throughput inference serving clusters, continuous batching engines, and model weight sharding topologies."
  },
  {
    id: "opp-4",
    company: "Stripe",
    role: "Lead Machine Learning & Fraud Platform Engineer",
    tier: "Global Financial Orbit",
    matchScore: 93,
    skills: ["Real-time Inference", "Python", "Spanner", "Pub/Sub"],
    salary: "$240k - $330k",
    description: "Building high-throughput real-time AI decision engines handling millions of global payment transactions per second."
  },
  {
    id: "opp-5",
    company: "Linear",
    role: "Full Stack AI Product Engineer",
    tier: "Fast Moving Satellite",
    matchScore: 91,
    skills: ["TypeScript", "React", "LLM Context Window", "FastAPI"],
    salary: "$190k - $270k",
    description: "Crafting intuitive AI summarization, automatic issue triaging, and real-time collaborative workspace intelligence."
  },
  {
    id: "opp-6",
    company: "Figma",
    role: "Senior AI Canvas & Rendering Architect",
    tier: "Design Technology Orbit",
    matchScore: 90,
    skills: ["WebAssembly", "C++", "Generative Canvas", "TypeScript"],
    salary: "$210k - $300k",
    description: "Integrating intelligent generative design primitives directly into Figma's ultra-low latency WebAssembly vector canvas."
  },
  {
    id: "opp-7",
    company: "Datadog",
    role: "AI Telemetry & Anomaly Detection Engineer",
    tier: "Cloud Observability Orbit",
    matchScore: 89,
    skills: ["Time Series ML", "Go", "Distributed Tracing", "GCP"],
    salary: "$200k - $280k",
    description: "Building automated root-cause analysis engines parsing billions of real-time server telemetry spans."
  },
  {
    id: "opp-8",
    company: "Vercel",
    role: "AI SDK & Edge Compute Engineer",
    tier: "Developer Experience Orbit",
    matchScore: 88,
    skills: ["Next.js", "AI SDK", "Edge Runtime", "Streaming"],
    salary: "$195k - $275k",
    description: "Empowering millions of frontend developers to build streaming AI UI experiences on Vercel's global edge network."
  }
];

export const AIJobRadar: React.FC<AIJobRadarProps> = ({ onSelectApplication, onRefresh }) => {
  const { token } = useAuth();
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [isApplyingBatch, setIsApplyingBatch] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [searchFilter, setSearchFilter] = useState('');

  const filteredOpps = AI_OPPORTUNITIES_DATABASE.filter(opp => 
    opp.company.toLowerCase().includes(searchFilter.toLowerCase()) ||
    opp.role.toLowerCase().includes(searchFilter.toLowerCase()) ||
    opp.skills.some(s => s.toLowerCase().includes(searchFilter.toLowerCase()))
  );

  const toggleSelect = (id: string) => {
    setSelectedIds(prev => 
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  const selectAll = () => {
    if (selectedIds.length === filteredOpps.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(filteredOpps.map(o => o.id));
    }
  };

  const handleApplySingle = async (opp: typeof AI_OPPORTUNITIES_DATABASE[0]) => {
    try {
      await apiRequest('/applications', {
        method: 'POST',
        token,
        body: JSON.stringify({
          company: opp.company,
          role: opp.role,
          jobDescription: opp.description,
          applicationDate: new Date().toISOString().split('T')[0],
          status: 'applied'
        })
      });
      setStatusMessage(`🚀 Added "${opp.company} - ${opp.role}" to your Solar Orbit!`);
      onRefresh();
      setTimeout(() => setStatusMessage(null), 3500);
    } catch (err: any) {
      alert(`Error applying: ${err.message}`);
    }
  };

  const handleApplyBatchQueue = async () => {
    if (selectedIds.length === 0) return;
    try {
      setIsApplyingBatch(true);
      const itemsToApply = AI_OPPORTUNITIES_DATABASE.filter(o => selectedIds.includes(o.id));
      
      for (const item of itemsToApply) {
        await apiRequest('/applications', {
          method: 'POST',
          token,
          body: JSON.stringify({
            company: item.company,
            role: item.role,
            jobDescription: item.description,
            applicationDate: new Date().toISOString().split('T')[0],
            status: 'applied'
          })
        });
      }

      setStatusMessage(`🛰️ Successfully queued & applied to all ${itemsToApply.length} target roles in one batch!`);
      setSelectedIds([]);
      onRefresh();
      setTimeout(() => setStatusMessage(null), 4000);
    } catch (err: any) {
      alert(`Batch application error: ${err.message}`);
    } finally {
      setIsApplyingBatch(false);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Radar Command Header */}
      <div className="glass-stellar p-6 rounded-3xl border border-sky-500/30 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-2xl relative overflow-hidden">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-sky-600 via-indigo-600 to-purple-600 flex items-center justify-center text-white shadow-lg shadow-sky-500/30">
            <BrainCircuit className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-extrabold text-white font-['Plus_Jakarta_Sans',sans-serif]">
                AI Opportunities Queue & Role Match Scanner
              </h2>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-sky-950 text-sky-400 border border-sky-800">
                {AI_OPPORTUNITIES_DATABASE.length} Curated Openings
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Select multiple high-tier AI/ML roles and apply to all of them into your queue simultaneously.
            </p>
          </div>
        </div>

        {/* Batch Application Action Controls */}
        <div className="flex items-center gap-3 w-full md:w-auto justify-between md:justify-end">
          <button
            onClick={selectAll}
            className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 flex items-center gap-1.5 transition-colors"
          >
            {selectedIds.length === filteredOpps.length ? (
              <>
                <CheckSquare className="w-4 h-4 text-sky-400" /> Deselect All
              </>
            ) : (
              <>
                <Square className="w-4 h-4 text-slate-400" /> Select All ({filteredOpps.length})
              </>
            )}
          </button>

          <button
            disabled={selectedIds.length === 0 || isApplyingBatch}
            onClick={handleApplyBatchQueue}
            className="px-4 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-amber-500 via-orange-500 to-rose-600 hover:opacity-95 text-white shadow-lg shadow-amber-500/30 transition-all flex items-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {isApplyingBatch ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Queuing into Orbit...
              </>
            ) : (
              <>
                <Rocket className="w-4 h-4" /> Batch Apply Selected ({selectedIds.length})
              </>
            )}
          </button>
        </div>
      </div>

      {statusMessage && (
        <div className="p-4 rounded-2xl bg-emerald-950/80 border border-emerald-500/50 text-emerald-300 text-xs flex items-center gap-2 animate-in fade-in slide-in-from-top-2 shadow-lg">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{statusMessage}</span>
        </div>
      )}

      {/* Role Search & Filter */}
      <div className="flex items-center justify-between gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-2.5" />
          <input
            type="text"
            placeholder="Filter by company, role, or skill (e.g. PyTorch, Vertex AI)..."
            value={searchFilter}
            onChange={(e) => setSearchFilter(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-900/90 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
          />
        </div>

        <span className="text-xs text-slate-400">
          Showing <span className="text-white font-bold">{filteredOpps.length}</span> matching opportunities
        </span>
      </div>

      {/* Grid of Target AI Opportunities with Multi-Select Queue */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredOpps.map((opp) => {
          const isSelected = selectedIds.includes(opp.id);

          return (
            <div
              key={opp.id}
              onClick={() => toggleSelect(opp.id)}
              className={`planet-card p-5 rounded-3xl border cursor-pointer flex flex-col justify-between space-y-4 shadow-lg transition-all relative overflow-hidden ${
                isSelected
                  ? 'border-sky-400 bg-slate-900/95 shadow-sky-500/20 scale-[1.01]'
                  : 'border-slate-800/80 hover:border-slate-700'
              }`}
            >
              {isSelected && (
                <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-sky-400 via-indigo-500 to-amber-400 animate-pulse"></div>
              )}

              <div>
                <div className="flex items-start justify-between gap-3 mb-2">
                  <div className="flex items-center gap-3">
                    <button
                      type="button"
                      onClick={(e) => { e.stopPropagation(); toggleSelect(opp.id); }}
                      className="text-slate-400 hover:text-white"
                    >
                      {isSelected ? (
                        <CheckSquare className="w-5 h-5 text-sky-400" />
                      ) : (
                        <Square className="w-5 h-5 text-slate-500" />
                      )}
                    </button>

                    <div className="w-8 h-8 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-sky-400 shrink-0">
                      <Building2 className="w-4 h-4" />
                    </div>

                    <div>
                      <h3 className="text-sm font-bold text-white">{opp.company}</h3>
                      <span className="text-[10px] font-semibold text-slate-400">{opp.tier}</span>
                    </div>
                  </div>

                  <div className="text-right">
                    <span className="px-2.5 py-1 rounded-full bg-emerald-950/80 text-emerald-300 border border-emerald-700/50 text-[10px] font-black inline-flex items-center gap-1">
                      <Sparkles className="w-3 h-3 text-emerald-400" /> {opp.matchScore}% Match
                    </span>
                    <span className="block text-[10px] text-slate-400 font-mono mt-1 font-semibold">{opp.salary}</span>
                  </div>
                </div>

                <h4 className="text-xs font-bold text-sky-300 mb-2">{opp.role}</h4>
                <p className="text-xs text-slate-400 leading-relaxed line-clamp-2 mb-3">
                  {opp.description}
                </p>

                <div className="flex flex-wrap gap-1.5">
                  {opp.skills.map((skill, sIdx) => (
                    <span
                      key={sIdx}
                      className="text-[10px] font-mono px-2 py-0.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>

              <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between" onClick={(e) => e.stopPropagation()}>
                <span className="text-[11px] text-slate-500 flex items-center gap-1">
                  <Clock className="w-3 h-3" /> Direct 1-Click Launch
                </span>

                <button
                  onClick={() => handleApplySingle(opp)}
                  className="px-3 py-1.5 rounded-xl text-xs font-bold bg-sky-600 hover:bg-sky-500 text-white shadow-md shadow-sky-600/30 transition-all flex items-center gap-1"
                >
                  <PlusCircle className="w-3.5 h-3.5" />
                  <span>Queue in Orbit</span>
                </button>
              </div>

            </div>
          );
        })}
      </div>

    </div>
  );
};
