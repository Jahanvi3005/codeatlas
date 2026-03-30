import { useState } from 'react';
import { Send, Loader2, Bot, User } from 'lucide-react';
import { chatApi } from '../services/api';

export default function DashboardQA({ repoId }) {
  const [query, setQuery] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim() || loading) return;

    setLoading(true);
    try {
      const { data } = await chatApi.query(repoId, query);
      setAnswer(data.answer);
    } catch (err) {
      setAnswer("Sorry, I couldn't process that question right now.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-12 p-8 rounded-3xl bg-card border border-border shadow-2xl relative overflow-hidden group">
      <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:scale-110 transition-transform duration-500">
        <Bot className="w-24 h-24 text-accent" />
      </div>
      
      <div className="relative z-10">
        <h2 className="text-2xl font-bold mb-2 flex items-center gap-3 italic">
          <Bot className="w-6 h-6 text-accent" />
          Ask CodeAtlas Anything
        </h2>
        <p className="text-muted-foreground text-sm mb-6 max-w-xl">
          Need a quick answer about this specific repository? Ask here without entering the full workspace.
        </p>

        <form onSubmit={handleSubmit} className="flex gap-4 mb-6">
          <input 
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. How does the database connection work?"
            className="flex-1 px-6 py-4 bg-background border border-border rounded-2xl outline-none focus:border-accent transition-all shadow-inner text-sm"
          />
          <button 
            type="submit" disabled={!query.trim() || loading}
            className="px-6 py-4 bg-foreground text-background rounded-2xl font-bold flex items-center gap-2 disabled:opacity-50 hover:bg-white/90 transition-all shadow-lg"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
            Ask
          </button>
        </form>

        {answer && (
          <div className="p-6 rounded-2xl bg-background/50 border border-white/5 animate-in fade-in slide-in-from-top-4 duration-500">
            <div className="flex gap-4">
              <div className="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center text-accent flex-shrink-0">
                <Bot className="w-4 h-4" />
              </div>
              <div className="text-sm leading-relaxed text-foreground/90 whitespace-pre-wrap">
                {answer}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
