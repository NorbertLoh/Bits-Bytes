import React, { useEffect, Dispatch, SetStateAction } from 'react';
import { XIcon, BrainIcon, PlusIcon, TrashIcon } from './../icons/icons';

interface MemoryPanelProps {
  isOpen: boolean;
  onClose: () => void;
  memory: string[];
  setMemory: Dispatch<SetStateAction<string[]>>;
}

const MemoryPanel: React.FC<MemoryPanelProps> = ({ isOpen, onClose, memory, setMemory }) => {

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  const handleAddMemoryField = () => {
    if (memory.length < 10) {
      setMemory([...memory, '']);
    }
  };

  const handleMemoryChange = (index: number, value: string) => {
    const newMemory = [...memory];
    newMemory[index] = value;
    setMemory(newMemory);
  };

  const handleRemoveMemoryField = (index: number) => {
    const newMemory = memory.filter((_, i) => i !== index);
    setMemory(newMemory);
  };

  return (
    <div
      className={`fixed inset-0 z-50 transition-all duration-300 ${isOpen ? 'visible' : 'invisible'}`}
      aria-labelledby="memory-panel-title"
      role="dialog"
      aria-modal="true"
    >
      {/* Overlay */}
      <div
        className={`absolute inset-0 bg-black/70 transition-opacity duration-300 ${isOpen ? 'opacity-100' : 'opacity-0'}`}
        onClick={onClose}
        aria-hidden="true"
      />
      
      {/* Drawer */}
      <div
        className={`absolute top-0 left-0 flex flex-col h-full w-full max-w-md bg-slate-900 border-r border-slate-700 shadow-xl transform transition-transform ease-in-out duration-300 ${isOpen ? 'translate-x-0' : '-translate-x-full'}`}
      >
        {/* Header */}
        <header className="flex items-center justify-between p-4 border-b border-slate-700 flex-shrink-0">
          <h2 id="memory-panel-title" className="text-lg font-semibold text-slate-100 flex items-center gap-2">
            <BrainIcon className="h-5 w-5 text-cyan-400" />
            Context Memory
          </h2>
          <button
            onClick={onClose}
            className="p-1 rounded-full text-slate-400 hover:bg-slate-800 hover:text-white focus:outline-none focus:ring-2 focus:ring-cyan-400"
            aria-label="Close memory panel"
          >
            <XIcon className="h-5 w-5" />
          </button>
        </header>

        {/* Content */}
        <div className="flex-grow p-4 overflow-y-auto">
          <p className="text-sm text-slate-400 mb-4">
            Add contextual information here. This will be included with every analysis request to improve accuracy. You can add up to 10 entries.
          </p>
          <div className="space-y-3">
            {memory.map((item, index) => (
              <div key={index} className="flex items-center gap-2 animate-fade-in">
                <input
                  type="text"
                  value={item}
                  onChange={(e) => handleMemoryChange(index, e.target.value)}
                  placeholder={`Memory context ${index + 1}...`}
                  className="flex-grow p-2 bg-slate-800 border border-slate-600 text-slate-100 rounded-md shadow-sm focus:ring-cyan-400 focus:border-cyan-400 transition"
                />
                <button
                  onClick={() => handleRemoveMemoryField(index)}
                  className="p-2 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded-md transition-colors"
                  aria-label={`Remove memory field ${index + 1}`}
                >
                  <TrashIcon className="h-5 w-5" />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <footer className="p-4 border-t border-slate-700 flex-shrink-0">
          <button
            onClick={handleAddMemoryField}
            disabled={memory.length >= 10}
            className="w-full flex justify-center items-center gap-2 px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-black bg-cyan-400 hover:bg-cyan-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 focus:ring-cyan-400 disabled:bg-slate-700 disabled:text-slate-400 disabled:cursor-not-allowed transition"
          >
            <PlusIcon className="h-5 w-5" />
            Add Memory Field
          </button>
           {memory.length >= 10 && (
             <p className="text-xs text-center text-yellow-400 mt-2">Maximum of 10 memory fields reached.</p>
            )}
        </footer>
      </div>
    </div>
  );
};

export default MemoryPanel;