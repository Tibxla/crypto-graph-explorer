import { useState, useEffect, useMemo, useCallback } from 'react';
import { Network } from 'lucide-react';
import Navbar from '@/components/Navbar';
import GraphCanvas from '@/components/GraphCanvas';
import StatsPanel from '@/components/StatsPanel';
import AnalysisPanel from '@/components/AnalysisPanel';
import { NodeData, EdgeData } from '@/lib/graphTypes';
import { parseCSV, generateEdges, computeStats } from '@/lib/graphUtils';

const MAX_DISPLAY_NODES = 300;

export default function Index() {
  const [allNodes, setAllNodes] = useState<NodeData[]>([]);
  const [displayNodes, setDisplayNodes] = useState<NodeData[]>([]);
  const [edges, setEdges] = useState<EdgeData[]>([]);
  const [selectedNode, setSelectedNode] = useState<NodeData | null>(null);
  const [removedNodes, setRemovedNodes] = useState<Set<string>>(new Set());
  const [activeTab, setActiveTab] = useState('graph');
  const [nodeLimit, setNodeLimit] = useState(MAX_DISPLAY_NODES);
  const [loading, setLoading] = useState(true);

  const loadCSV = useCallback(async (csvText: string) => {
    setLoading(true);
    const nodes = parseCSV(csvText);
    setAllNodes(nodes);
    
    const sorted = [...nodes].sort((a, b) => b.degree - a.degree);
    const limited = sorted.slice(0, nodeLimit);
    setDisplayNodes(limited);
    
    const edgeData = generateEdges(limited);
    setEdges(edgeData);
    setRemovedNodes(new Set());
    setSelectedNode(null);
    setLoading(false);
  }, [nodeLimit]);

  useEffect(() => {
    fetch('/data/nodes_metrics.csv')
      .then(r => r.text())
      .then(loadCSV)
      .catch(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (allNodes.length === 0) return;
    const sorted = [...allNodes].sort((a, b) => b.degree - a.degree);
    const limited = sorted.slice(0, nodeLimit);
    setDisplayNodes(limited);
    setEdges(generateEdges(limited));
  }, [nodeLimit, allNodes]);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => loadCSV(ev.target?.result as string);
    reader.readAsText(file);
  };

  const stats = useMemo(() => {
    const activeNodes = displayNodes.filter(n => !removedNodes.has(n.id));
    const activeEdges = edges.filter(e => !removedNodes.has(e.source) && !removedNodes.has(e.target));
    return computeStats(activeNodes, activeEdges);
  }, [displayNodes, edges, removedNodes]);

  const topNodes = useMemo(
    () => [...displayNodes].filter(n => !removedNodes.has(n.id)).sort((a, b) => b.degree - a.degree),
    [displayNodes, removedNodes]
  );

  return (
    <div className="h-screen flex flex-col bg-background">
      <Navbar activeTab={activeTab} onTabChange={setActiveTab} onFileUpload={handleFileUpload} />
      
      <div className="flex-1 flex overflow-hidden">
        {/* Left panel */}
        <div className="w-72 border-r border-border flex-shrink-0">
          <StatsPanel
            stats={stats}
            selectedNode={selectedNode}
            topNodes={topNodes}
            onNodeSelect={setSelectedNode}
          />
        </div>

        {/* Center: Graph */}
        <div className="flex-1 relative">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center space-y-3">
                <Network className="w-12 h-12 text-primary mx-auto node-pulse" />
                <p className="text-sm text-muted-foreground">Chargement du graphe...</p>
              </div>
            </div>
          ) : (
            <GraphCanvas
              nodes={displayNodes}
              edges={edges}
              onNodeSelect={setSelectedNode}
              selectedNode={selectedNode}
              removedNodes={removedNodes}
            />
          )}
          
          {/* Node limit slider */}
          <div className="absolute bottom-4 left-4 glass rounded-lg px-4 py-2 flex items-center gap-3">
            <span className="text-[10px] uppercase tracking-wider text-muted-foreground">Nœuds</span>
            <input
              type="range"
              min={50}
              max={Math.min(allNodes.length, 1000)}
              value={nodeLimit}
              onChange={(e) => setNodeLimit(Number(e.target.value))}
              className="w-32 accent-primary"
            />
            <span className="text-xs font-mono text-primary w-10">{nodeLimit}</span>
          </div>
        </div>

        {/* Right panel: Analysis */}
        {activeTab === 'analysis' && (
          <div className="w-80 border-l border-border flex-shrink-0">
            <AnalysisPanel
              nodes={displayNodes}
              edges={edges}
              removedNodes={removedNodes}
              onRemoveNode={(id) => setRemovedNodes(prev => new Set(prev).add(id))}
              onResetRemovals={() => setRemovedNodes(new Set())}
            />
          </div>
        )}
      </div>
    </div>
  );
}
