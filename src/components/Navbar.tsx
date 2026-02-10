import { Network, Upload, BarChart3, Sun, Moon } from 'lucide-react';
import { useState, useEffect } from 'react';

interface NavbarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  onFileUpload: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

export default function Navbar({ activeTab, onTabChange, onFileUpload }: NavbarProps) {
  const [isLight, setIsLight] = useState(false);

  useEffect(() => {
    document.documentElement.classList.toggle('light', isLight);
  }, [isLight]);
  return (
    <nav className="h-14 border-b border-border flex items-center px-4 gap-4 glass">
      <div className="flex items-center gap-2">
        <Network size={20} className="text-primary" />
        <span className="font-bold text-sm tracking-wider">CRYPTO GRAPH</span>
      </div>

      <div className="flex-1" />

      <div className="flex items-center gap-1 bg-secondary/50 rounded-lg p-1">
        {[
          { id: 'graph', label: 'Graphe', icon: Network },
          { id: 'analysis', label: 'Analyse', icon: BarChart3 },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeTab === tab.id
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <tab.icon size={14} />
            {tab.label}
          </button>
        ))}
      </div>

      <button
        onClick={() => setIsLight(!isLight)}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium border border-border hover:border-primary/50 transition-colors"
        title={isLight ? 'Mode sombre' : 'Mode clair'}
      >
        {isLight ? <Moon size={14} /> : <Sun size={14} />}
      </button>

      <label className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium cursor-pointer border border-border hover:border-primary/50 transition-colors">
        <Upload size={14} />
        CSV
        <input type="file" accept=".csv" onChange={onFileUpload} className="hidden" />
      </label>
    </nav>
  );
}
