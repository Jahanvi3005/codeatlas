import { useState, useRef, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { chatApi, scrapeApi } from '../services/api';
import { 
  Send, Loader2, Bot, User, Code2, Link, FileText, ChevronRight, X, Settings 
} from 'lucide-react';
import SettingsModal from '../components/SettingsModal';

export default function RepoWorkspace() {
  const { id } = useParams();
  const [messages, setMessages] = useState([{
    role: 'assistant',
    text: "Hi! I'm CodeAtlas. I've indexed your repository. Start asking questions like 'Where is authentication handled?' or 'How does the routing work?'"
  }]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeSource, setActiveSource] = useState(null);
  const [scrapeUrl, setScrapeUrl] = useState('');
  const [scraping, setScraping] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const endOfMessagesRef = useRef(null);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = { role: 'user', text: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const { data } = await chatApi.query(id, userMessage.text);
      setMessages(prev => [...prev, {
        role: 'assistant',
        text: data.answer,
        sources: data.sources
      }]);
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        text: "I encountered an error trying to process your query."
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleScrape = async (e) => {
    e.preventDefault();
    if (!scrapeUrl.trim() || scraping) return;

    setScraping(true);
    try {
      await scrapeApi.scrapeDocs(id, scrapeUrl);
      setMessages(prev => [...prev, {
        role: 'assistant',
        text: `Successfully initiated a scrape for: ${scrapeUrl}. This content is now being vectorized and will be included in subsequent answers.`
      }]);
      setScrapeUrl('');
    } catch (err) {
      alert("Failed to scrape URL.");
    } finally {
      setScraping(false);
    }
  };

  return (
    <div className="h-screen flex bg-background relative overflow-hidden">
      
      {/* Sidebar Content Panel */}
      <aside className="w-80 border-r border-border bg-card hidden md:flex flex-col flex-shrink-0 z-20">
        <div className="p-4 border-b border-border">
          <h2 className="text-lg font-bold tracking-tight mb-1">CodeAtlas Workspace</h2>
          <p className="text-xs text-muted-foreground">ID: {id?.substring(0,8)}...</p>
        </div>

        {/* Enrichment Panel */}
        <div className="p-4 border-b border-border space-y-3">
          <div className="flex items-center gap-2 mb-2">
            <Link className="w-4 h-4 text-accent"/>
            <h3 className="text-sm font-semibold">Enrich Context</h3>
          </div>
          <p className="text-xs text-muted-foreground leading-relaxed">
            Add full external URLs (like library docs or project wiki) to append to the vector index.
          </p>
          <form onSubmit={handleScrape} className="flex gap-2">
            <input 
              type="url"
              value={scrapeUrl}
              onChange={(e) => setScrapeUrl(e.target.value)}
              placeholder="https://docs.example.com"
              className="flex-1 px-3 py-1.5 bg-background border border-border rounded-md text-sm outline-none focus:border-accent"
              required
            />
            <button 
              type="submit" disabled={scraping}
              className="px-3 py-1.5 bg-foreground text-background rounded-md disabled:opacity-50"
            >
              {scraping ? <Loader2 className="w-4 h-4 animate-spin"/> : <ChevronRight className="w-4 h-4"/>}
            </button>
          </form>
        </div>

        <div className="mt-auto p-4 border-t border-border">
          <button 
            onClick={() => setIsSettingsOpen(true)}
            className="w-full flex items-center gap-3 px-3 py-2 text-muted-foreground hover:bg-white/5 rounded-md text-sm font-medium transition-colors"
          >
            <Settings className="w-4 h-4"/> Settings
          </button>
        </div>
      </aside>

      <SettingsModal isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />

      {/* Main Chat Interface */}
      <main className="flex-1 flex flex-col min-w-0 bg-[#0a0a0a]">
        
        {/* Chat History */}
        <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6">
          {messages.map((msg, idx) => (
            <motion.div 
              key={idx}
              initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
              className={`flex gap-4 max-w-4xl mx-auto ${msg.role === 'user' ? 'justify-end' : ''}`}
            >
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center text-accent flex-shrink-0">
                  <Bot className="w-4 h-4" />
                </div>
              )}
              
              <div className={`space-y-4 max-w-[85%] ${msg.role === 'user' ? 'bg-accent text-white px-5 py-3 rounded-2xl rounded-tr-none' : ''}`}>
                
                {msg.role === 'user' ? (
                  <p className="whitespace-pre-wrap text-[15px]">{msg.text}</p>
                ) : (
                  <div className="prose prose-invert max-w-none text-[15px] leading-relaxed">
                    {/* Render text simply. In production, use react-markdown */}
                    <p className="whitespace-pre-wrap text-foreground/90">{msg.text}</p>
                  </div>
                )}
                
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-border/50">
                    <p className="text-xs font-medium text-muted-foreground uppercase tracking-widest mb-3 flex items-center gap-2">
                      <Code2 className="w-3 h-3" /> Cited Sources
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {msg.sources.map((s, i) => (
                        <button 
                          key={i}
                          onClick={() => setActiveSource(s)}
                          className="px-3 py-1.5 rounded-lg bg-card border border-white/5 hover:bg-white/5 text-xs font-medium text-foreground transition-all flex items-center gap-2"
                        >
                          {s.type === 'external_doc' ? <Link className="w-3 h-3 text-accent" /> : <FileText className="w-3 h-3 text-muted-foreground" />}
                          {s.path.split('/').pop()}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              
              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center text-white flex-shrink-0">
                  <User className="w-4 h-4" />
                </div>
              )}
            </motion.div>
          ))}
          {loading && (
            <div className="flex gap-4 max-w-4xl mx-auto">
               <div className="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center text-accent flex-shrink-0">
                  <Bot className="w-4 h-4" />
                </div>
                <div className="flex items-center py-2 px-1">
                  <motion.div animate={{ opacity: [0.3, 1, 0.3] }} transition={{ repeat: Infinity, duration: 1.5 }} className="w-2 h-2 rounded-full bg-accent mr-1"/>
                  <motion.div animate={{ opacity: [0.3, 1, 0.3] }} transition={{ repeat: Infinity, duration: 1.5, delay: 0.2 }} className="w-2 h-2 rounded-full bg-accent mr-1"/>
                  <motion.div animate={{ opacity: [0.3, 1, 0.3] }} transition={{ repeat: Infinity, duration: 1.5, delay: 0.4 }} className="w-2 h-2 rounded-full bg-accent"/>
                </div>
            </div>
          )}
          <div ref={endOfMessagesRef} />
        </div>

        {/* Input Form */}
        <div className="p-4 md:px-8 max-w-4xl mx-auto w-full">
          <form onSubmit={handleSend} className="relative flex items-end bg-card border border-border rounded-2xl shadow-xl overflow-hidden focus-within:ring-1 focus-within:ring-accent transition-all">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend(e);
                }
              }}
              placeholder="Ask anything about the codebase..."
              className="w-full max-h-48 min-h-[60px] p-4 bg-transparent outline-none resize-none text-[15px]"
              rows={1}
            />
            <div className="p-3 bg-transparent">
              <button 
                type="submit" disabled={!input.trim() || loading}
                className="w-10 h-10 rounded-xl bg-accent text-white flex items-center justify-center disabled:opacity-50 hover:bg-accent/90 transition-colors shadow-lg"
              >
                <Send className="w-4 h-4 -ml-0.5" />
              </button>
            </div>
          </form>
          <div className="text-center mt-3 text-[11px] text-muted-foreground uppercase tracking-wider">
            CodeAtlas generates representations based on localized vector context.
          </div>
        </div>
      </main>

      {/* Source Citation Overlay */}
      <AnimatePresence>
        {activeSource && (
          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="absolute top-4 right-4 bottom-4 w-96 bg-card border border-border shadow-2xl rounded-2xl flex flex-col z-50 overflow-hidden"
          >
            <div className="p-4 border-b border-border flex items-center justify-between bg-background/50">
              <h3 className="font-semibold text-sm truncate pr-4">{activeSource.path}</h3>
              <button onClick={() => setActiveSource(null)} className="p-1 hover:bg-white/10 rounded-md transition-colors text-muted-foreground">
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-4 bg-[#0a0a0a]">
              <pre className="text-xs text-foreground/80 font-mono whitespace-pre-wrap leading-relaxed">
                {activeSource.snippet}
              </pre>
            </div>
            <div className="p-3 border-t border-border bg-background">
              <span className="text-xs text-muted-foreground px-2 py-1 rounded-md bg-white/5 border border-white/5 uppercase font-medium">
                {activeSource.type}
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
