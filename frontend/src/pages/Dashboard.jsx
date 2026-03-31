import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { repoApi, scrapeApi } from '../services/api';
import { 
  Loader2, CheckCircle2, XCircle, FolderOpen, ArrowRight, LayoutDashboard, 
  Search, Settings, Cpu, Layers, GitBranch, Terminal, MessageSquare, ListCheck, Link
} from 'lucide-react';
import SettingsModal from '../components/SettingsModal';
import FileTreeModal from '../components/FileTreeModal';
import MermaidChart from '../components/MermaidChart';
import DashboardQA from '../components/DashboardQA';

export default function Dashboard() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [repo, setRepo] = useState(null);
  const [summary, setSummary] = useState(null);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isTreeOpen, setIsTreeOpen] = useState(false);
  const [scrapeUrl, setScrapeUrl] = useState('');
  const [scraping, setScraping] = useState(false);
  const [scrapeSuccess, setScrapeSuccess] = useState(false);
  
  // Polling for status
  useEffect(() => {
    let interval;
    const fetchStatus = async () => {
      try {
        const { data } = await repoApi.getStatus(id);
        setRepo(data);
        
        if (data.status === 'COMPLETED') {
          fetchSummary();
        } else if (data.status === 'FAILED') {
          clearInterval(interval);
        }
      } catch (err) {
        console.error(err);
      }
    };

    fetchStatus();
    interval = setInterval(fetchStatus, 5000); // 5s is gentler for local LLM runs
    return () => clearInterval(interval);
  }, [id]);

  useEffect(() => {
    // If we have a summary and it's fully populated with deep info, we can stop polling status
    // But for now, we'll let the user refresh or rely on the status interval.
    // Let's add a secondary interval just for summary if deep fields are missing.
    let summaryInterval;
    if (repo?.status === 'COMPLETED' && (!summary || !summary.flow_chart)) {
      summaryInterval = setInterval(fetchSummary, 5000);
    }
    return () => clearInterval(summaryInterval);
  }, [repo?.status, summary?.flow_chart]);

  const fetchSummary = async () => {
    try {
      const { data } = await repoApi.getSummary(id);
      setSummary(data);
    } catch (err) {}
  };

  const handleScrape = async (e) => {
    e.preventDefault();
    if (!scrapeUrl.trim() || scraping) return;

    setScraping(true);
    try {
      await scrapeApi.scrapeDocs(id, scrapeUrl);
      setScrapeSuccess(true);
      setScrapeUrl('');
      setTimeout(() => setScrapeSuccess(false), 3000);
      // Refresh summary to see if new data affected metrics (optional)
      fetchSummary();
    } catch (err) {
      alert("Failed to scrape URL.");
    } finally {
      setScraping(false);
    }
  };

  const statusMessages = {
    PENDING: "Initializing...",
    CLONING: "Cloning repository objects...",
    PARSING: "Parsing and chunking source files...",
    INDEXING: "Generating vector embeddings...",
    COMPLETED: "Ingestion complete.",
    FAILED: "Failed to ingest repository."
  };

  return (
    <div className="min-h-screen flex bg-background">
      {/* Sidebar Placeholder */}
      <aside className="w-64 border-r border-border bg-card hidden md:flex flex-col flex-shrink-0">
        <div className="p-6 border-b border-border">
          <h2 className="text-xl font-bold tracking-tight">CodeAtlas</h2>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <a className="flex items-center gap-3 px-3 py-2 text-foreground bg-white/5 rounded-md text-sm font-medium"><LayoutDashboard className="w-4 h-4"/> Dashboard</a>
          <a 
            onClick={() => setIsSettingsOpen(true)}
            className="flex items-center gap-3 px-3 py-2 text-muted-foreground hover:bg-white/5 rounded-md text-sm font-medium transition-colors cursor-pointer"
          >
            <Settings className="w-4 h-4"/> Settings
          </a>
        </nav>
      </aside>

      <SettingsModal isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
      <FileTreeModal isOpen={isTreeOpen} onClose={() => setIsTreeOpen(false)} repoId={id} />

      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center overflow-y-auto">
        <div className="w-full max-w-5xl p-8 mt-12 pb-24">
          
          <div className="mb-8 p-8 rounded-3xl bg-card border border-border shadow-xl relative overflow-hidden">
            <div className="absolute top-0 right-0 p-8 opacity-5">
              <Cpu className="w-32 h-32" />
            </div>
            <div className="relative z-10">
              <h1 className="text-4xl font-black mb-3 tracking-tight">{repo?.name || 'Repository'}</h1>
              <a href={repo?.url} target="_blank" rel="noreferrer" className="text-muted-foreground hover:text-accent transition-colors flex items-center gap-2 text-sm font-medium">
                <GitBranch className="w-3 h-3" /> {repo?.url}
              </a>
            </div>
          </div>

          {!repo || !['COMPLETED', 'FAILED'].includes(repo.status) ? (
            <motion.div 
              initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              className="flex flex-col items-center justify-center p-24 rounded-3xl bg-card border border-border shadow-2xl"
            >
              <div className="relative">
                <div className="absolute inset-0 bg-accent/20 blur-2xl rounded-full scale-150 animate-pulse" />
                <Loader2 className="w-16 h-16 text-accent animate-spin mb-8 relative z-10" />
              </div>
              <h2 className="text-2xl font-bold mb-3 tracking-tight">{repo ? statusMessages[repo.status] : "Loading status..."}</h2>
              <p className="text-muted-foreground text-center max-w-md text-sm leading-relaxed">
                We are performing a deep structural audit of your codebase. This includes semantic chunking, vector indexing, and architectural mapping.
              </p>
            </motion.div>
          ) : repo.status === 'FAILED' ? (
            <div className="flex flex-col items-center justify-center p-16 rounded-3xl bg-red-950/10 border border-red-500/20 shadow-2xl">
              <XCircle className="w-16 h-16 text-red-500 mb-6" />
              <h2 className="text-2xl font-bold mb-2">Ingestion Failed</h2>
              <p className="text-sm text-red-400/80">{repo.error_message || "An unknown error occurred during clonal scan."}</p>
            </div>
          ) : (
            <AnimatePresence>
              <motion.div 
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-8"
              >
                {/* Top Statistics & Entry Action */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Basic Stats */}
                  <div className="lg:col-span-2 p-8 rounded-3xl bg-card border border-border shadow-xl space-y-6">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-2xl bg-green-500/10 flex items-center justify-center text-green-500">
                        <CheckCircle2 className="w-6 h-6" />
                      </div>
                      <div>
                        <h2 className="text-xl font-bold leading-tight tracking-tight">Intelligence Verified</h2>
                        <p className="text-xs text-muted-foreground uppercase tracking-wider font-semibold">Repository fully indexed</p>
                      </div>
                    </div>
                    
                    {summary && (
                      <div className="grid grid-cols-3 gap-6">
                        <div className="space-y-1">
                          <div className="text-3xl font-black text-foreground">{summary.file_count}</div>
                          <div className="text-[10px] text-muted-foreground uppercase tracking-widest font-bold">Source Files</div>
                        </div>
                        <div className="space-y-1">
                          <div className="text-3xl font-black text-foreground">{(summary.total_size_bytes / 1024).toFixed(1)}</div>
                          <div className="text-[10px] text-muted-foreground uppercase tracking-widest font-bold">Total (KB)</div>
                        </div>
                        <div className="space-y-1">
                          <div className="text-3xl font-black text-foreground">{Object.keys(summary.language_counts || {}).length}</div>
                          <div className="text-[10px] text-muted-foreground uppercase tracking-widest font-bold">Languages</div>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Primary Call to Action */}
                  <div className="p-8 rounded-3xl bg-foreground text-background shadow-2xl flex flex-col justify-between group cursor-pointer hover:scale-[1.02] transition-all duration-300"
                    onClick={() => navigate(`/repo/${id}/workspace`)}
                  >
                    <div>
                      <Search className="w-8 h-8 mb-4 opacity-50 transition-transform group-hover:rotate-12" />
                      <h3 className="text-2xl font-black tracking-tight leading-none mb-2">Dive into<br/>Workspace</h3>
                    </div>
                    <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest opacity-80">
                      Explore Citations <ArrowRight className="w-4 h-4" />
                    </div>
                  </div>
                </div>

                {/* Deep Intelligence Sections */}
                {summary && summary.deep_summary && (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 animate-in fade-in slide-in-from-bottom-6 duration-700">
                    
                    {/* Deep Summary */}
                    <div className="lg:col-span-2 p-8 rounded-3xl bg-card border border-border shadow-xl">
                      <h3 className="text-xl font-black mb-4 flex items-center gap-3">
                        <MessageSquare className="w-5 h-5 text-accent" />
                        Executive Intelligence
                      </h3>
                      <div className="prose prose-invert max-w-none text-muted-foreground/90 leading-relaxed text-[15px]">
                        {summary.deep_summary.split('\n\n').map((p, i) => <p key={i} className="mb-4">{p}</p>)}
                      </div>
                    </div>

                    {/* Architecture overview */}
                    <div className="p-8 rounded-3xl bg-card border border-border shadow-xl">
                      <h3 className="text-xl font-black mb-4 flex items-center gap-3">
                        <Layers className="w-5 h-5 text-accent" />
                        Architecture
                      </h3>
                      <p className="text-[15px] font-medium leading-relaxed mb-6">
                        {summary.architecture || "Not detected"}
                      </p>
                      
                      <h3 className="text-sm font-bold uppercase tracking-widest text-muted-foreground mb-4">Core Tech Stack</h3>
                      <div className="flex flex-wrap gap-2">
                        {summary.tech_stack?.map((tag, i) => (
                          <span key={i} className="px-3 py-1.5 rounded-xl bg-white/5 border border-white/5 text-xs font-bold hover:border-accent/40 transition-colors">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Mermaid Visual Flow - Now Full Width */}
                    <div className="lg:col-span-2 p-8 rounded-3xl bg-card border border-border shadow-xl flex flex-col">
                      <h3 className="text-xl font-black mb-4 flex items-center gap-3">
                        <Terminal className="w-5 h-5 text-accent" />
                        Logic Flow Diagram
                      </h3>
                      <div className="flex-1 flex items-center justify-center overflow-hidden w-full">
                        {summary.flow_chart && summary.flow_chart !== "graph TD\n  Repo --> Index" ? (
                          <div className="w-full">
                            <MermaidChart chart={summary.flow_chart} />
                          </div>
                        ) : (
                          <div className="flex flex-col items-center justify-center gap-4 py-20 w-full border-2 border-dashed border-border/50 rounded-3xl bg-background/20">
                            <div className="flex gap-2">
                              <div className="w-2 h-2 rounded-full bg-accent animate-bounce [animation-delay:-0.3s]"></div>
                              <div className="w-2 h-2 rounded-full bg-accent animate-bounce [animation-delay:-0.15s]"></div>
                              <div className="w-2 h-2 rounded-full bg-accent animate-bounce"></div>
                            </div>
                            <div className="text-sm font-medium text-muted-foreground">
                              {summary.flow_chart === "graph TD\n  Repo --> Index" 
                                ? "Waiting for deep intelligence to initialize..." 
                                : "Generating deep architectural visualization..."}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Inline Actions */}
                    <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div 
                           onClick={() => setIsTreeOpen(true)}
                           className="p-6 rounded-2xl bg-card/60 border border-border hover:border-accent/40 transition-all cursor-pointer flex items-center justify-between group shadow-lg"
                        >
                          <div className="flex items-center gap-3">
                            <FolderOpen className="text-muted-foreground group-hover:text-accent transition-colors" />
                            <span className="font-bold text-sm tracking-tight">Browse Tree</span>
                          </div>
                          <ArrowRight className="w-4 h-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-all font-black" />
                        </div>

                        {/* Enrich Knowledge Card */}
                        <div className="md:col-span-2 p-6 rounded-2xl bg-card/60 border border-border shadow-lg">
                          <div className="flex items-center gap-3 mb-4">
                            <div className="w-8 h-8 rounded-xl bg-accent/10 flex items-center justify-center text-accent">
                                <Link className="w-4 h-4" />
                            </div>
                            <div>
                                <h4 className="font-bold text-sm tracking-tight">Enrich Knowledge</h4>
                                <p className="text-[10px] text-muted-foreground uppercase tracking-wider font-bold">Inject external documentation</p>
                            </div>
                          </div>
                          <form onSubmit={handleScrape} className="flex gap-2">
                            <input 
                              type="url"
                              value={scrapeUrl}
                              onChange={(e) => setScrapeUrl(e.target.value)}
                              placeholder="https://docs.example.com"
                              className="flex-1 px-4 py-2.5 bg-background border border-border rounded-xl text-xs outline-none focus:border-accent transition-all shadow-inner"
                              required
                            />
                            <button 
                              type="submit" disabled={scraping || !scrapeUrl.trim()}
                              className={`px-5 py-2.5 rounded-xl transition-all flex items-center gap-2 text-xs font-black shadow-lg ${
                                scrapeSuccess ? 'bg-green-600 text-white' : 'bg-foreground text-background hover:bg-white/90'
                              }`}
                            >
                              {scraping ? <Loader2 className="w-4 h-4 animate-spin"/> : scrapeSuccess ? <CheckCircle2 className="w-4 h-4"/> : <ArrowRight className="w-4 h-4"/>}
                              {scrapeSuccess ? 'Scraped!' : 'Add Docs'}
                            </button>
                          </form>
                        </div>
                    </div>

                  </div>
                )}

                {/* Dashboard Q&A Section */}
                {summary && summary.deep_summary && (
                  <DashboardQA repoId={id} />
                )}

              </motion.div>
            </AnimatePresence>
          )}

        </div>
      </main>
    </div>
  );
}
