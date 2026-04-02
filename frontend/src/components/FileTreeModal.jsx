import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Folder, File, ChevronRight, ChevronDown, Loader2, FolderOpen } from 'lucide-react';
import { repoApi } from '../services/api';

const TreeItem = ({ item, level = 0 }) => {
  const [isOpen, setIsOpen] = useState(false);
  const isDirectory = item.type === 'directory';

  return (
    <div className="select-none">
      <div 
        onClick={() => isDirectory && setIsOpen(!isOpen)}
        className={`flex items-center gap-2 py-1.5 px-2 rounded-lg cursor-pointer transition-colors hover:bg-white/5 ${level === 0 ? 'mt-1' : ''}`}
        style={{ paddingLeft: `${level * 16 + 8}px` }}
      >
        {isDirectory ? (
          <>
            {isOpen ? <ChevronDown className="w-3.5 h-3.5 text-muted-foreground" /> : <ChevronRight className="w-3.5 h-3.5 text-muted-foreground" />}
            <Folder className={`w-4 h-4 ${isOpen ? 'text-accent' : 'text-muted-foreground'}`} />
          </>
        ) : (
          <>
            <div className="w-3.5" />
            <File className="w-4 h-4 text-muted-foreground/60" />
          </>
        )}
        <span className="text-sm font-medium text-foreground/90">{item.name}</span>
      </div>
      
      {isDirectory && isOpen && item.children && (
        <div className="border-l border-white/5 ml-4">
          {item.children.map((child, i) => (
            <TreeItem key={i} item={child} level={level + 1} />
          ))}
        </div>
      )}
    </div>
  );
};

export default function FileTreeModal({ isOpen, onClose, repoId }) {
  const [tree, setTree] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen && repoId) {
      fetchTree();
    }
  }, [isOpen, repoId]);

  const fetchTree = async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await repoApi.getTree(repoId);
      if (data && data.tree) {
        setTree(data.tree);
      } else {
        setTree([]);
      }
    } catch (err) {
      console.error("Failed to fetch tree", err);
      setError(err.response?.data?.detail || err.message || "Failed to load repository tree");
    } finally {
      setLoading(false);
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
            className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-2xl h-[70vh] bg-card border border-border shadow-2xl rounded-2xl z-[101] overflow-hidden flex flex-col"
          >
            <div className="p-6 border-b border-border flex items-center justify-between bg-background/50 flex-shrink-0">
              <div className="flex items-center gap-3">
                <FolderOpen className="w-5 h-5 text-accent" />
                <h2 className="text-xl font-bold">Repository Explorer</h2>
              </div>
              <button onClick={onClose} className="p-2 hover:bg-white/5 rounded-full transition-colors">
                <X className="w-5 h-5 text-muted-foreground" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 bg-[#0a0a0a]/50 custom-scrollbar">
              {loading ? (
                <div className="h-full flex flex-col items-center justify-center opacity-50">
                  <Loader2 className="w-8 h-8 text-accent animate-spin" />
                  <p className="mt-4 text-sm font-medium tracking-wide">Mapping codebase structure...</p>
                </div>
              ) : error ? (
                <div className="h-full flex flex-col items-center justify-center text-red-500/80 p-8 text-center">
                  <X className="w-12 h-12 mb-4 opacity-20" />
                  <p className="text-sm font-medium">{error}</p>
                  <button 
                    onClick={fetchTree}
                    className="mt-4 px-4 py-2 bg-white/5 hover:bg-white/10 rounded-lg text-xs font-semibold text-white transition-colors"
                  >
                    Try Again
                  </button>
                </div>
              ) : tree && tree.length > 0 ? (
                <div className="pb-8">
                  {tree.map((item, i) => (
                    <TreeItem key={i} item={item} />
                  ))}
                </div>
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-muted-foreground">
                  <Folder className="w-12 h-12 mb-4 opacity-10" />
                  <p className="text-sm">No files were indexed for this repository.</p>
                </div>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
