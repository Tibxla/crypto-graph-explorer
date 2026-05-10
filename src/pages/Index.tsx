import { useState, useEffect, useMemo, useCallback } from 'react';
import { Network, ChevronLeft, ChevronRight } from 'lucide-react';
import Navbar from '@/components/Navbar';
import GraphCanvas from '@/components/GraphCanvas';
import GraphStats from '@/components/GraphStats';
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
  const [highlightedNodes, setHighlightedNodes] = useState<Set<string>>(new Set());
  const [highlightedEdges, setHighlightedEdges] = useState<Array<{source: string, target: string}>>([]); 
  const [visualizationMode, setVisualizationMode] = useState<string | null>(null);
  const [showStatsPanel, setShowStatsPanel] = useState(true);
  const [showAnalysisPanel, setShowAnalysisPanel] = useState(true);

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
        {/* Left panel - Collapsible */}
        <div className={`border-r border-border flex-shrink-0 transition-all duration-300 overflow-hidden ${
          showStatsPanel ? 'w-80' : 'w-0'
        }`}>
          <StatsPanel
            stats={stats}
            selectedNode={selectedNode}
            topNodes={topNodes}
            onNodeSelect={setSelectedNode}
          />
        </div>

        {/* Center: Graph + Toggle Button */}
        <div className="flex-1 relative flex flex-col">
          {/* Toggle Stats Panel Button */}
          <button
            onClick={() => setShowStatsPanel(!showStatsPanel)}
            className="absolute top-4 left-4 z-10 p-1.5 rounded-lg border border-border hover:border-primary/50 hover:bg-secondary/50 transition-all duration-200 glass"
            title={showStatsPanel ? 'Masquer le panneau' : 'Afficher le panneau'}
          >
            {showStatsPanel ? (
              <ChevronLeft size={16} className="text-muted-foreground hover:text-primary transition-colors" />
            ) : (
              <ChevronRight size={16} className="text-muted-foreground hover:text-primary transition-colors" />
            )}
          </button>

          {/* Toggle Analysis Panel Button */}
          {activeTab === 'analysis' && (
            <button
              onClick={() => setShowAnalysisPanel(!showAnalysisPanel)}
              className="absolute top-4 right-4 z-10 p-1.5 rounded-lg border border-border hover:border-primary/50 hover:bg-secondary/50 transition-all duration-200 glass"
              title={showAnalysisPanel ? 'Masquer l\'analyse' : 'Afficher l\'analyse'}
            >
              {showAnalysisPanel ? (
                <ChevronRight size={16} className="text-muted-foreground hover:text-primary transition-colors" />
              ) : (
                <ChevronLeft size={16} className="text-muted-foreground hover:text-primary transition-colors" />
              )}
            </button>
          )}

          {/* Graph content */}
          <div className="flex-1 relative">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center space-y-3">
                <Network className="w-12 h-12 text-primary mx-auto node-pulse" />
                <p className="text-sm text-muted-foreground">Chargement du graphe...</p>
              </div>
            </div>
          ) : (
            <>
              <GraphCanvas
                nodes={displayNodes}
                edges={edges}
                onNodeSelect={setSelectedNode}
                selectedNode={selectedNode}
                removedNodes={removedNodes}
                highlightedNodes={highlightedNodes}
                highlightedEdges={highlightedEdges}
                visualizationMode={visualizationMode}
              />
              
              {/* Graph Statistics Overlay */}
              <GraphStats
                nodes={displayNodes.filter(n => !removedNodes.has(n.id))}
                edges={edges.filter(e => !removedNodes.has(e.source) && !removedNodes.has(e.target))}
                loading={loading}
                selectedNode={selectedNode}
              />
            </>
          )}

            {/* Node limit slider */}
            <div className="absolute bottom-6 right-6 glass rounded-lg px-4 py-2 flex items-center gap-3 z-10">
            <span className="text-[10px] uppercase tracking-wider text-muted-foreground">Nœuds max</span>
            <input
              type="range"
              min={50}
              max={Math.min(allNodes.length, 1000)}
              value={nodeLimit}
              onChange={(e) => setNodeLimit(Number(e.target.value))}
              className="w-32 accent-primary"
            />
            <span className="text-xs font-mono text-primary w-10 text-right">{nodeLimit}</span>
            </div>
          </div>
        </div>

        {/* Right panel: Analysis */}
        {activeTab === 'analysis' && showAnalysisPanel && (
          <div className="w-80 border-l border-border flex-shrink-0">
            <AnalysisPanel
              nodes={displayNodes}
              edges={edges}
              removedNodes={removedNodes}
              onRemoveNode={(id) => setRemovedNodes(prev => new Set(prev).add(id))}
              onRemoveNodes={(ids) => setRemovedNodes(prev => {
                const newSet = new Set(prev);
                ids.forEach(id => newSet.add(id));
                return newSet;
              })}
              onResetRemovals={() => setRemovedNodes(new Set())}
              onVisualize={(nodes, edges, mode) => {
                setHighlightedNodes(new Set(nodes));
                setHighlightedEdges(edges);
                setVisualizationMode(mode);
              }}
              onClearVisualization={() => {
                setHighlightedNodes(new Set());
                setHighlightedEdges([]);
                setVisualizationMode(null);
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
}
