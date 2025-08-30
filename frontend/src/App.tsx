import React, { useState, useCallback } from 'react';
import { AppView } from './types/types';
import ManualValidator from './components/ManualValidator';
import BulkProcessor from './components/BulkProcessor';
import Header from './components/Header';
import MemoryPanel from './components/MemoryPanel';
import { BrainIcon } from './icons/icons';

const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<AppView>(AppView.MANUAL);
  const [isMemoryPanelOpen, setIsMemoryPanelOpen] = useState<boolean>(false);
  const [memory, setMemory] = useState<string[]>(['']);

  const handleViewChange = useCallback((view: AppView) => {
    setCurrentView(view);
  }, []);

  return (
    <div className="min-h-screen bg-black text-slate-200 font-sans">
      <div className="container mx-auto p-4 sm:p-6 lg:p-8">
        <Header currentView={currentView} onViewChange={handleViewChange} />
        <main className="mt-6">
          {currentView === AppView.MANUAL && <ManualValidator memory={memory} />}
          {currentView === AppView.BULK && <BulkProcessor memory={memory} />}
        </main>
      </div>
      <button
        onClick={() => setIsMemoryPanelOpen(true)}
        className="fixed bottom-6 left-6 bg-cyan-400 text-black p-4 rounded-full shadow-lg hover:bg-cyan-500 transition-transform transform hover:scale-110 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 focus:ring-cyan-400 z-40"
        aria-label="Open context memory panel"
        title="Open Context Memory"
      >
        <BrainIcon className="h-6 w-6" />
      </button>

      <MemoryPanel
        isOpen={isMemoryPanelOpen}
        onClose={() => setIsMemoryPanelOpen(false)}
        memory={memory}
        setMemory={setMemory}
      />
    </div>
  );
};

export default App;