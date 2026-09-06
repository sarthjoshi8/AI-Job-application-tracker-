import React, { useState, useEffect } from 'react';
import { apiRequest } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { 
  X, 
  User, 
  CheckCircle2, 
  AlertCircle, 
  Sparkles, 
  Clock, 
  Cpu, 
  Key, 
  Save 
} from 'lucide-react';

interface SettingsModalProps {
  onClose: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({ onClose }) => {
  const { token, user } = useAuth();
  const [profile, setProfile] = useState<any>({
    name: '',
    resumeSummary: '',
    keySkills: [],
    nudgeCadenceDays: 5
  });
  const [skillsText, setSkillsText] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    const loadProfile = async () => {
      try {
        setLoading(true);
        const data = await apiRequest('/user/profile', { token });
        setProfile(data);
        setSkillsText((data.keySkills || []).join(', '));
      } catch (err: any) {
        setErrorMsg(err.message || 'Could not load profile.');
      } finally {
        setLoading(false);
      }
    };
    loadProfile();
  }, [token]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      setErrorMsg(null);
      setSuccessMsg(false);

      const parsedSkills = skillsText
        .split(',')
        .map(s => s.trim())
        .filter(Boolean);

      const updated = await apiRequest('/user/profile', {
        method: 'PUT',
        token,
        body: JSON.stringify({
          name: profile.name,
          resumeSummary: profile.resumeSummary,
          keySkills: parsedSkills,
          nudgeCadenceDays: Number(profile.nudgeCadenceDays) || 5
        })
      });

      setProfile(updated);
      setSuccessMsg(true);
      setTimeout(() => setSuccessMsg(false), 3000);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to save settings.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
      <div className="glass-panel w-full max-w-xl rounded-2xl flex flex-col border border-slate-700 shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-900/60">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-sky-600/20 text-sky-400 border border-sky-500/30">
              <User className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Profile & AI Co-Pilot Context</h3>
              <p className="text-xs text-slate-400">Context fed into Gemini for tailored cover letters</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white p-1 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSave} className="p-6 space-y-4 max-h-[75vh] overflow-y-auto">
          {errorMsg && (
            <div className="p-3 rounded-xl bg-rose-950/60 border border-rose-800/80 text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {successMsg && (
            <div className="p-3 rounded-xl bg-emerald-950/60 border border-emerald-800/80 text-emerald-300 text-xs flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>Profile context saved successfully!</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              Candidate Full Name
            </label>
            <input
              type="text"
              value={profile.name || ''}
              onChange={(e) => setProfile({ ...profile, name: e.target.value })}
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-sm focus:outline-none focus:border-sky-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              Core Skills & Tech Stack (comma separated)
            </label>
            <input
              type="text"
              value={skillsText}
              onChange={(e) => setSkillsText(e.target.value)}
              placeholder="Python, FastAPI, TypeScript, React, GCP, BigQuery"
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-sm focus:outline-none focus:border-sky-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              Resume & Career Summary
            </label>
            <textarea
              rows={4}
              value={profile.resumeSummary || ''}
              onChange={(e) => setProfile({ ...profile, resumeSummary: e.target.value })}
              placeholder="Summary of experience, key achievements, leadership responsibilities..."
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white placeholder-slate-500 text-xs focus:outline-none focus:border-sky-500 font-mono leading-relaxed"
            />
          </div>

          <div className="pt-2 border-t border-slate-800">
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1 flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-amber-400" /> Nudge Cadence (Days of Inactivity)
            </label>
            <p className="text-[11px] text-slate-400 mb-2">
              Cloud Scheduler triggers nudges via Pub/Sub when an application remains in "Applied" status with no updates for this many days.
            </p>
            <input
              type="number"
              min={1}
              max={30}
              value={profile.nudgeCadenceDays || 5}
              onChange={(e) => setProfile({ ...profile, nudgeCadenceDays: e.target.value })}
              className="w-24 px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-sm focus:outline-none focus:border-sky-500"
            />
          </div>

          <div className="pt-4 flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-5 py-2 rounded-xl text-xs font-semibold bg-sky-600 hover:bg-sky-500 text-white shadow-lg shadow-sky-600/30 transition-all flex items-center gap-2 disabled:opacity-50"
            >
              <Save className="w-3.5 h-3.5" />
              {saving ? 'Saving...' : 'Save Context'}
            </button>
          </div>
        </form>

      </div>
    </div>
  );
};
