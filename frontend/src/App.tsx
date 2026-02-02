import React, { useState, useEffect } from 'react';
import { Zap, Palette, Layers, ShieldCheck } from 'lucide-react';
import PromptEditor from './components/PromptEditor';

interface Prompt {
  id: number;
  text: string;
  tags: string[];
  Q_score: number;
  created_at: string;
}

const PromptCard: React.FC<{ prompt: Prompt }> = ({ prompt }) => {
  const getLevelColor = (q: number) => {
    if (q >= 0.9) return 'bg-green-100 text-green-800 border-green-200';
    if (q >= 0.8) return 'bg-blue-100 text-blue-800 border-blue-200';
    if (q >= 0.7) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    return 'bg-red-100 text-red-800 border-red-200';
  };

  return (
    <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-3">
        <span className={`px-2 py-0.5 rounded text-xs font-bold border ${getLevelColor(prompt.Q_score)}`}>
          Q: {prompt.Q_score.toFixed(2)}
        </span>
        <span className="text-[10px] text-gray-400">#{prompt.id}</span>
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
  const [view, setView] = useState<'library' | 'editor'>('editor');
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (view === 'library') {
      fetchPrompts();
    }
  }, [view]);

  const fetchPrompts = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/prompts');
      const data = await response.json();
      setPrompts(data.prompts);
    } catch (error) {
      console.error('Failed to fetch prompts:', error);
    } finally {
      setLoading(false);
    }
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
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto p-6">
        {view === 'editor' ? (
          <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-200">
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-gray-900">Advanced Prompt Editor</h2>
              <p className="text-gray-500 mt-1">Refine your prompts using the PES Quality Framework.</p>
            </div>
            <PromptEditor onSave={() => setView('library')} />
          </div>
        ) : (
          <div>
            <div className="flex justify-between items-center mb-8">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Prompt Library</h2>
                <p className="text-gray-500 mt-1">Manage and monitor your prompt performance.</p>
              </div>
              <button
                onClick={() => setView('editor')}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium transition-colors"
              >
                + New Prompt
              </button>
            </div>

            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
                {[1, 2, 3, 4, 5, 6].map(i => (
                  <div key={i} className="h-40 bg-gray-200 rounded-lg"></div>
                ))}
              </div>
            ) : prompts.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {prompts.map(prompt => (
                  <PromptCard key={prompt.id} prompt={prompt} />
                ))}
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
