
import React, { useState, useRef, useEffect } from 'react';
import { CommandEntry } from '../types';
import { ICONS } from '../constants';

interface TerminalProps {
  history: CommandEntry[];
  onSend: (cmd: string) => void;
  onClear: () => void;
}

const Terminal: React.FC<TerminalProps> = ({ history, onSend, onClear }) => {
  const [input, setInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [history]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    onSend(input);
    setInput('');
  };

  return (
    <div className="h-full flex flex-col glass rounded-3xl border border-slate-800 overflow-hidden shadow-2xl">
      {/* Terminal Toolbar */}
      <div className="h-10 bg-slate-900/80 border-b border-slate-800 flex items-center justify-between px-4">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-red-500/20 border border-red-500/30" />
            <div className="w-3 h-3 rounded-full bg-amber-500/20 border border-amber-500/30" />
            <div className="w-3 h-3 rounded-full bg-emerald-500/20 border border-emerald-500/30" />
          </div>
          <span className="ml-3 text-[10px] font-bold text-slate-500 tracking-widest uppercase">jarvis@core ~ terminal</span>
        </div>
        <button 
          onClick={onClear}
          className="text-slate-500 hover:text-red-400 transition-colors"
          title="Clear History"
        >
          <ICONS.Trash />
        </button>
      </div>

      {/* History Area */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-6 space-y-4 mono text-sm leading-relaxed"
      >
        <div className="text-slate-500 mb-6">
          <p className="text-indigo-400 font-bold">Jarvis Core Terminal v2.4.0-stable</p>
          <p>Initializing secure WebSocket channel...</p>
          <p>Authentication token verified. System ready.</p>
          <p className="mt-2">Type 'help' to see available modular commands.</p>
        </div>

        {history.slice().reverse().map((entry) => (
          <div key={entry.id} className="space-y-1 animate-in fade-in slide-in-from-bottom-2 duration-300">
            <div className="flex items-start gap-2 text-indigo-400 font-medium">
              <span className="opacity-50 select-none">$</span>
              <span>{entry.command}</span>
            </div>
            <div className={`pl-4 border-l border-slate-800 ml-1.5 ${
              entry.status === 'error' ? 'text-red-400' : 'text-slate-300'
            }`}>
              {entry.response}
            </div>
          </div>
        ))}
      </div>

      {/* Command Input Area */}
      <form onSubmit={handleSubmit} className="p-4 bg-slate-950/80 border-t border-slate-800 flex items-center gap-3">
        <span className="text-indigo-500 mono font-bold select-none ml-2">$</span>
        <input
          autoFocus
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter command directive..."
          className="flex-1 bg-transparent border-none focus:ring-0 text-slate-200 mono text-sm placeholder:text-slate-700"
        />
        <button type="submit" className="hidden" aria-label="Submit" />
      </form>
    </div>
  );
};

export default Terminal;
