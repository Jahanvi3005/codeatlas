import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Settings, Database, Globe, Save, Loader2, CheckCircle } from 'lucide-react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export default function SettingsModal({ isOpen, onClose }) {
  const [config, setConfig] = useState({ ollama_url: '', ollama_model: '' });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchSettings();
    }
  }, [isOpen]);

  const fetchSettings = async () => {
    setLoading(true);
    try {
      const { data } = await axios.get(`${API_BASE}/settings/`);
      setConfig(data);
    } catch (err) {
      console.error("Failed to fetch settings", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await axios.put(`${API_BASE}/settings/`, config);
      setSaved(true);
      setTimeout(() => {
        setSaved(false);
        onClose();
      }, 2000);
    } catch (err) {
      alert("Failed to save settings");
    } finally {
      setSaving(false);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div 
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100]"
          />
          <motion.div 
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-card border border-border shadow-2xl rounded-2xl z-[101] overflow-hidden"
          >
            <div className="p-6 border-b border-border flex items-center justify-between bg-background/50">
              <div className="flex items-center gap-3">
                <Settings className="w-5 h-5 text-accent" />
                <h2 className="text-xl font-bold">Platform Settings</h2>
              </div>
              <button onClick={onClose} className="p-2 hover:bg-white/5 rounded-full transition-colors">
                <X className="w-5 h-5 text-muted-foreground" />
              </button>
            </div>

            <form onSubmit={handleSave} className="p-6 space-y-6">
              {loading ? (
                <div className="py-12 flex flex-col items-center justify-center">
                  <Loader2 className="w-8 h-8 text-accent animate-spin" />
                  <p className="mt-4 text-sm text-muted-foreground">Fetching current configuration...</p>
                </div>
              ) : (
                <>
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-foreground flex items-center gap-2">
                        <Globe className="w-4 h-4 text-muted-foreground"/> Ollama API URL
                      </label>
                      <input 
                        type="url"
                        value={config.ollama_url}
                        onChange={(e) => setConfig({...config, ollama_url: e.target.value})}
                        className="w-full px-4 py-2 bg-background border border-border rounded-xl outline-none focus:border-accent transition-colors"
                        placeholder="http://localhost:11434"
                        required
                      />
                      <p className="text-[11px] text-muted-foreground">The local endpoint where your Ollama daemon is listening.</p>
                    </div>

                    <div className="space-y-2">
                      <label className="text-sm font-medium text-foreground flex items-center gap-2">
                        <Database className="w-4 h-4 text-muted-foreground"/> Active LLM Model
                      </label>
                      <input 
                        type="text"
                        value={config.ollama_model}
                        onChange={(e) => setConfig({...config, ollama_model: e.target.value})}
                        className="w-full px-4 py-2 bg-background border border-border rounded-xl outline-none focus:border-accent transition-colors"
                        placeholder="llama3.2"
                        required
                      />
                      <p className="text-[11px] text-muted-foreground">Specify the exact name of the model you have pulled in Ollama.</p>
                    </div>
                  </div>

                  <div className="pt-4 flex gap-3">
                    <button 
                      type="button" onClick={onClose}
                      className="flex-1 px-4 py-2 bg-white/5 hover:bg-white/10 text-foreground rounded-xl transition-colors font-medium"
                    >
                      Cancel
                    </button>
                    <button 
                      type="submit" disabled={saving || saved}
                      className={`flex-1 px-4 py-2 flex items-center justify-center gap-2 rounded-xl font-medium transition-all ${
                        saved ? 'bg-green-600 text-white' : 'bg-accent text-white hover:bg-accent/90'
                      }`}
                    >
                      {saving ? <Loader2 className="w-4 h-4 animate-spin"/> : saved ? <CheckCircle className="w-4 h-4"/> : <Save className="w-4 h-4"/>}
                      {saved ? 'Saved!' : 'Save Changes'}
                    </button>
                  </div>
                </>
              )}
            </form>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
