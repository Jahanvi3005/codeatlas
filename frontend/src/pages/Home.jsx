import { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { GitBranch, Database, Search, ArrowRight, Loader2 } from 'lucide-react';
import { repoApi } from '../services/api';

export default function Home() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleIngest = async (e) => {
    e.preventDefault();
    if (!url) return;
    
    setLoading(true);
    setError('');
    
    try {
      const { data } = await repoApi.ingest(url);
      navigate(`/repo/${data.id}`);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Failed to ingest repository. Please try again.");
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden bg-[#0a0a0a]">
      {/* Background gradients */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[400px] bg-accent/20 blur-[100px] rounded-full pointer-events-none" />
      
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="z-10 w-full max-w-4xl px-4 flex flex-col items-center text-center"
      >
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-card border border-border mb-8">
          <span className="w-2 h-2 rounded-full bg-accent animate-pulse" />
          <span className="text-sm font-medium text-muted-foreground">CodeAtlas v1.0 is live</span>
        </div>
        
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 text-transparent bg-clip-text bg-gradient-to-br from-white to-white/40">
          Understand Any Codebase.<br /> Instantly.
        </h1>
        
        <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mb-12">
          Paste a public Git URL, and let CodeAtlas index the repositories. 
          Use semantic search to ask questions and instantly navigate massive code architectures.
        </p>

        <form onSubmit={handleIngest} className="w-full max-w-xl relative flex items-center group mb-4">
          <div className="absolute inset-0 bg-accent/20 blur-xl transition-all duration-500 group-hover:bg-accent/30 rounded-full" />
          <div className="relative flex w-full p-2 bg-card/80 backdrop-blur-md border border-white/10 rounded-full shadow-2xl">
            <GitBranch className="absolute left-6 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
            <input 
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://github.com/fastapi/fastapi"
              required
              className="w-full bg-transparent pl-14 pr-4 py-3 outline-none text-foreground placeholder:text-muted-foreground/60 rounded-full"
            />
            <button 
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-foreground text-background font-medium rounded-full hover:bg-white/90 transition-colors flex items-center gap-2 disabled:opacity-50"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Ingest Repo'}
            </button>
          </div>
        </form>
        {error && <p className="text-red-500 text-sm mt-2">{error}</p>}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-20 w-full text-left">
          <div className="p-6 rounded-2xl bg-card border border-white/5 space-y-4">
            <div className="w-10 h-10 rounded-lg bg-accent/20 flex items-center justify-center text-accent">
              <Database className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-medium text-foreground">Deep Indexing</h3>
            <p className="text-muted-foreground text-sm">We clone, parse, and chunk the codebase semantically into vector embeddings.</p>
          </div>
          <div className="p-6 rounded-2xl bg-card border border-white/5 space-y-4">
            <div className="w-10 h-10 rounded-lg bg-accent/20 flex items-center justify-center text-accent">
              <Search className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-medium text-foreground">Semantic Q&A</h3>
            <p className="text-muted-foreground text-sm">Ask natural questions and get precisely cited code snippets in return.</p>
          </div>
          <div className="p-6 rounded-2xl bg-card border border-white/5 space-y-4">
            <div className="w-10 h-10 rounded-lg bg-accent/20 flex items-center justify-center text-accent">
              <ArrowRight className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-medium text-foreground">Web Scraping</h3>
            <p className="text-muted-foreground text-sm">Enrich the context by scraping linked markdown resources and docs.</p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
