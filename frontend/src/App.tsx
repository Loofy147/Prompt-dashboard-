import React, { useState } from 'react';
import PromptEditor from './components/PromptEditor';

const App: React.FC = () => {
  const [view, setView] = useState<'library' | 'editor'>('editor');

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-indigo-700 text-white p-4 shadow-md">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <h1 className="text-xl font-bold">Prompt Dashboard Manager</h1>
          <div className="flex gap-4">
            <button
              onClick={() => setView('library')}
              className={`px-3 py-1 rounded ${view === 'library' ? 'bg-indigo-900' : 'hover:bg-indigo-600'}`}
            >
              Library
            </button>
            <button
              onClick={() => setView('editor')}
              className={`px-3 py-1 rounded ${view === 'editor' ? 'bg-indigo-900' : 'hover:bg-indigo-600'}`}
            >
              Editor
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto p-6">
        {view === 'editor' ? (
          <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Advanced Prompt Editor</h2>
            <PromptEditor />
          </div>
        ) : (
          <div className="text-center py-20">
            <h2 className="text-2xl font-semibold text-gray-600">Library View Coming Soon</h2>
            <p className="text-gray-400 mt-2">The 5 seeded prompts are available in the backend API.</p>
            <button
              onClick={() => setView('editor')}
              className="mt-6 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              Go to Editor
            </button>
          </div>
        )}
      </main>
    </div>
  );
};

export default App;
