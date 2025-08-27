import React, { useState, useCallback } from 'react';
import { AppView } from './types/types';
import ManualValidator from './components/ManualValidator';
import BulkProcessor from './components/BulkProcessor';
import Header from './components/Header';

const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<AppView>(AppView.MANUAL);

  const handleViewChange = useCallback((view: AppView) => {
    setCurrentView(view);
  }, []);

  return (
    <div className="min-h-screen bg-black text-slate-200 font-sans">
      <div className="container mx-auto p-4 sm:p-6 lg:p-8">
        <Header currentView={currentView} onViewChange={handleViewChange} />
        <main className="mt-6">
          {currentView === AppView.MANUAL && <ManualValidator />}
          {currentView === AppView.BULK && <BulkProcessor />}
        </main>
      </div>
    </div>
  );
};

export default App;