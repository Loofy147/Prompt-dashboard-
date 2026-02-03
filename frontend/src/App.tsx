import React, { useState, useEffect } from 'react';
import { Zap, Palette, Layers, ShieldCheck, Download, History, LayoutDashboard } from 'lucide-react';
import PromptEditor from './components/PromptEditor';
import ResearchDashboard from './components/ResearchDashboard';

interface Prompt {
  id: number;
  text: string;
  tags: string[];
  Q_score: number;
  version: number;
  parent_id: number | null;
  created_at: string;
}

const PromptCard: React.FC<{ prompt: Prompt; onEdit: (p: Prompt) => void }> = ({ prompt, onEdit }) => {
  const getLevelColor = (q: number) => {
    if (q >= 0.9) return 'bg-green-100 text-green-800 border-green-200';
    if (q >= 0.8) return 'bg-blue-100 text-blue-800 border-blue-200';
    if (q >= 0.7) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    return 'bg-red-100 text-red-800 border-red-200';
  };

  return (
    <div
      className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm hover:shadow-xl hover:shadow-palette-primary/5 transition-all cursor-pointer group"
      onClick={() => onEdit(prompt)}
    >
      <div className="flex justify-between items-start mb-3">
        <div className="flex gap-2">
          <span className={`px-2 py-0.5 rounded-lg text-[10px] font-black border ${getLevelColor(prompt.Q_score)}`}>
            Q: {prompt.Q_score.toFixed(4)}
          </span>
          <span className="px-2 py-0.5 bg-gray-50 text-gray-400 rounded-lg text-[10px] font-bold border border-gray-100 flex items-center gap-1">
            <History size={8} /> v{prompt.version}
          </span>
        </div>
        <span className="text-[10px] text-gray-300 font-mono">#{prompt.id}</span>
      </div>
      <p className="text-sm text-gray-700 line-clamp-3 mb-4 h-15">
        {prompt.text}
      </p>
      <div className="flex flex-wrap gap-1 mt-auto">
        {prompt.tags.map(tag => (
          <span key={tag} className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-[10px]">
            {tag}
          </span>
        ))}
      </div>
    </div>
  );
};

const App: React.FC = () => {
  const [view, setView] = useState<'library' | 'editor' | 'insights'>('editor');
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [loading, setLoading] = useState(false);
  const [editingPrompt, setEditingPrompt] = useState<Prompt | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [isFetchingMore, setIsFetchingMore] = useState(false);

  useEffect(() => {
    if (view === 'library') {
      setPage(1);
      fetchPrompts(1, false);
    }
  }, [view]);

  const fetchPrompts = async (pageNum = 1, append = false) => {
    if (pageNum === 1 && !append) setLoading(true);
    else setIsFetchingMore(true);

    try {
      const response = await fetch(`/api/prompts?page=${pageNum}&per_page=12`);
      const data = await response.json();

      if (append) {
        setPrompts(prev => [...prev, ...data.prompts]);
      } else {
        setPrompts(data.prompts);
      }

      setHasMore(data.page < data.pages);
      setPage(data.page);
    } catch (error) {
      console.error('Failed to fetch prompts:', error);
    } finally {
      setLoading(false);
      setIsFetchingMore(false);
    }
  };

  const handleExport = async (format: 'json' | 'csv') => {
    const url = `/api/prompts/export?format=${format}`;
    window.open(url, '_blank');
  };

  return (
    <div className="min-h-screen bg-palette-light font-sans">
      <nav className="bg-palette-dark text-white p-4 shadow-xl border-b border-palette-primary/20">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-3 group">
            <div className="w-10 h-10 bg-gradient-to-br from-palette-primary to-palette-secondary rounded-xl flex items-center justify-center shadow-lg transform group-hover:scale-110 transition-transform">
              <Zap className="text-white w-6 h-6 fill-current text-bolt-light" />
            </div>
            <div>
              <h1 className="text-xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
                PROMPT <span className="text-palette-primary">ARCHITECT</span>
              </h1>
              <div className="flex items-center gap-1 text-[10px] uppercase tracking-widest text-gray-500 font-bold">
                <ShieldCheck size={10} className="text-accent" /> ROBUST ENGINE | <Zap size={10} className="text-bolt" /> BOLT v2.0
              </div>
            </div>
          </div>
          <div className="flex gap-2 bg-gray-900/50 p-1 rounded-xl border border-white/5">
            <button
              onClick={() => setView('library')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${view === 'library' ? 'bg-palette-primary text-white shadow-lg shadow-palette-primary/30' : 'text-gray-400 hover:text-white hover:bg-white/5'}`}
            >
              <Layers size={16} /> Library
            </button>
            <button
              onClick={() => setView('editor')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${view === 'editor' ? 'bg-palette-primary text-white shadow-lg shadow-palette-primary/30' : 'text-gray-400 hover:text-white hover:bg-white/5'}`}
            >
              <Palette size={16} /> Designer
            </button>
            <button
              onClick={() => setView('insights')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${view === 'insights' ? 'bg-palette-primary text-white shadow-lg shadow-palette-primary/30' : 'text-gray-400 hover:text-white hover:bg-white/5'}`}
            >
              <LayoutDashboard size={16} /> Insights
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto p-6">
        {view === 'insights' ? (
          <ResearchDashboard />
        ) : view === 'editor' ? (
          <div className="bg-white p-8 rounded-3xl shadow-2xl shadow-palette-dark/5 border border-gray-100">
            <div className="mb-8">
              <h2 className="text-3xl font-black text-palette-dark tracking-tighter">
                {editingPrompt ? 'REFINE VERSION' : 'PROMPT DESIGNER'}
              </h2>
              <p className="text-gray-400 font-medium mt-1">
                {editingPrompt ? `Iterating on prompt #${editingPrompt.id} (v${editingPrompt.version})` : 'Crafting high-performance machine directives.'}
              </p>
            </div>
            <PromptEditor
              initialText={editingPrompt?.text}
              initialTags={editingPrompt?.tags}
              parentId={editingPrompt?.id}
              onSave={() => {
                setEditingPrompt(null);
                setView('library');
              }}
              onCancel={() => {
                setEditingPrompt(null);
                setView('library');
              }}
            />
          </div>
        ) : (
          <div>
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
              <div>
                <h2 className="text-3xl font-black text-palette-dark tracking-tighter uppercase">ARCHIVE</h2>
                <p className="text-gray-400 font-medium mt-1">History of computational directives.</p>
              </div>
              <div className="flex gap-2">
                <div className="flex bg-white rounded-xl shadow-sm border border-gray-100 p-1">
                  <button
                    onClick={() => handleExport('json')}
                    className="p-2 hover:bg-gray-50 text-gray-400 hover:text-palette-primary transition-colors flex items-center gap-2 text-xs font-bold"
                  >
                    <Download size={14} /> JSON
                  </button>
                  <div className="w-px h-4 bg-gray-100 self-center"></div>
                  <button
                    onClick={() => handleExport('csv')}
                    className="p-2 hover:bg-gray-50 text-gray-400 hover:text-palette-primary transition-colors flex items-center gap-2 text-xs font-bold"
                  >
                    <Download size={14} /> CSV
                  </button>
                </div>
                <button
                  onClick={() => {
                    setEditingPrompt(null);
                    setView('editor');
                  }}
                  className="px-6 py-2 bg-palette-primary text-white rounded-xl hover:bg-palette-primary/90 font-bold shadow-lg shadow-palette-primary/20 transition-all flex items-center gap-2"
                >
                  <Zap size={16} /> NEW DIRECTIVE
                </button>
              </div>
            </div>

            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
                {[1, 2, 3, 4, 5, 6].map(i => (
                  <div key={i} className="h-40 bg-gray-200 rounded-lg"></div>
                ))}
              </div>
            ) : prompts.length > 0 ? (
              <div className="space-y-8">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {prompts.map(prompt => (
                    <PromptCard
                      key={prompt.id}
                      prompt={prompt}
                      onEdit={(p) => {
                        setEditingPrompt(p);
                        setView('editor');
                      }}
                    />
                  ))}
                </div>
                {hasMore && (
                  <div className="flex justify-center pb-8">
                    <button
                      onClick={() => fetchPrompts(page + 1, true)}
                      disabled={isFetchingMore}
                      className="px-10 py-4 bg-white border-2 border-palette-primary text-palette-primary rounded-2xl hover:bg-palette-primary hover:text-white transition-all font-black uppercase text-xs tracking-widest shadow-xl shadow-palette-primary/10 disabled:opacity-50 flex items-center gap-3"
                    >
                      {isFetchingMore ? (
                        <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <Zap size={16} />
                      )}
                      {isFetchingMore ? 'FETCHING...' : 'LOAD MORE DIRECTIVES'}
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-20 bg-white rounded-2xl border-2 border-dashed border-gray-200">
                <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                  <span className="text-gray-400 text-2xl">?</span>
                </div>
                <h3 className="text-lg font-medium text-gray-900">No prompts yet</h3>
                <p className="text-gray-500 mt-1">Start by creating your first optimized prompt.</p>
                <button
                  onClick={() => setView('editor')}
                  className="mt-6 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                  Go to Editor
                </button>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default App;
