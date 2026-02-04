import React from 'react';
import { History } from 'lucide-react';

export interface Prompt {
  id: number;
  text: string;
  tags: string[];
  Q_score: number;
  version: number;
  parent_id: number | null;
  created_at: string;
}

interface PromptCardProps {
  prompt: Prompt;
  onEdit: (p: Prompt) => void;
}

const PromptCard: React.FC<PromptCardProps> = React.memo(({ prompt, onEdit }) => {
  const getLevelColor = (q: number) => {
    if (q >= 0.9) return 'bg-green-100 text-green-800 border-green-200';
    if (q >= 0.8) return 'bg-blue-100 text-blue-800 border-blue-200';
    if (q >= 0.7) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    return 'bg-red-100 text-red-800 border-red-200';
  };

  return (
    <div
      className="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm hover:shadow-2xl hover:shadow-palette-primary/10 transition-all cursor-pointer group flex flex-col h-full transform hover:-translate-y-1"
      onClick={() => onEdit(prompt)}
    >
      <div className="flex justify-between items-start mb-4">
        <div className="flex gap-2">
          <div className="flex flex-col">
             <span className="text-[8px] font-black text-gray-400 uppercase tracking-widest mb-0.5">Q-SCORE</span>
             <span className={`px-2 py-0.5 rounded-lg text-[10px] font-black border ${getLevelColor(prompt.Q_score)}`}>
                {prompt.Q_score.toFixed(4)}
             </span>
          </div>
          <div className="flex flex-col">
             <span className="text-[8px] font-black text-gray-400 uppercase tracking-widest mb-0.5">VERSION</span>
             <span className="px-2 py-0.5 bg-gray-50 text-gray-400 rounded-lg text-[10px] font-bold border border-gray-100 flex items-center gap-1">
                <History size={8} /> v{prompt.version}
             </span>
          </div>
        </div>
        <span className="text-[10px] text-gray-300 font-mono font-bold tracking-tighter">ID: {prompt.id}</span>
      </div>

      <div className="relative flex-1">
        <p className="text-sm text-gray-700 line-clamp-4 font-medium leading-relaxed mb-6">
          {prompt.text}
        </p>
        <div className="absolute bottom-0 left-0 right-0 h-4 bg-gradient-to-t from-white to-transparent pointer-events-none"></div>
      </div>

      <div className="flex flex-wrap gap-1.5 pt-4 border-t border-gray-50 mt-auto">
        {prompt.tags.map(tag => (
          <span key={tag} className="px-2.5 py-0.5 bg-palette-light/50 text-palette-dark rounded-md text-[9px] font-black uppercase tracking-tight">
            {tag}
          </span>
        ))}
      </div>
    </div>
  );
});

export default PromptCard;
