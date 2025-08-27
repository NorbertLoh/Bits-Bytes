import React from 'react';
import { AppView } from '../types/types';

interface HeaderProps {
  currentView: AppView;
  onViewChange: (view: AppView) => void;
}

const Header: React.FC<HeaderProps> = ({ currentView, onViewChange }) => {
  const getTabClass = (view: AppView) => {
    const baseClasses = 'px-4 py-2 text-sm sm:text-base font-medium rounded-md transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 focus:ring-cyan-400';
    if (currentView === view) {
      return `${baseClasses} bg-white text-black shadow-lg`;
    }
    return `${baseClasses} text-slate-300 hover:bg-slate-800`;
  };

  return (
    <header className="text-center">
      <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-white to-red-500">
        Geo-Compliance Detection System
      </h1>
      <p className="mt-2 text-md sm:text-lg text-slate-400 max-w-2xl mx-auto">
        Automating Geo-Regulation with LLM to turn regulatory detection from a blind spot into a traceable, auditable output.
      </p>
      <div className="mt-6 flex justify-center bg-slate-900 p-1 rounded-lg max-w-xs mx-auto">
        <button
          onClick={() => onViewChange(AppView.MANUAL)}
          className={getTabClass(AppView.MANUAL)}
        >
          Manual Validation
        </button>
        <button
          onClick={() => onViewChange(AppView.BULK)}
          className={getTabClass(AppView.BULK)}
        >
          Bulk Processing
        </button>
      </div>
    </header>
  );
};

export default Header;