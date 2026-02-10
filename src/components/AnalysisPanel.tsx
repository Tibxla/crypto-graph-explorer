import { useState } from 'react';
import { NodeData, EdgeData, SimulationResult } from '@/lib/graphTypes';
import { simulateRemoval, shortenAddress, getNodeColor } from '@/lib/graphUtils';
import { Trash2, Zap, BarChart3, AlertTriangle } from 'lucide-react';

interface AnalysisPanelProps {
  nodes: NodeData[];
  edges: EdgeData[];
  removedNodes: Set<string>;
  onRemoveNode: (nodeId: string) => void;
  onResetRemovals: () => void;
}

export default function AnalysisPanel({ nodes, edges, removedNodes, onRemoveNode, onResetRemovals }: AnalysisPanelProps) {
  const [results, setResults] = useState<SimulationResult[]>([]);
  const [mode, setMode] = useState<'single' | 'cascade'>('single');

  const activeNodes = nodes.filter(n => !removedNodes.has(n.id));
  const activeEdges = edges.filter(e => !removedNodes.has(e.source) && !removedNodes.has(e.target));

  const handleRemoveTop = () => {
    const topNode = [...activeNodes].sort((a, b) => b.degree - a.degree)[0];
    if (!topNode) return;
    const result = simulateRemoval(activeNodes, activeEdges, topNode);
    setResults(prev => [result, ...prev]);
    onRemoveNode(topNode.id);
  };

  const handleRemoveTopPageRank = () => {
    const topNode = [...activeNodes].sort((a, b) => b.pagerank - a.pagerank)[0];
    if (!topNode) return;
    const result = simulateRemoval(activeNodes, activeEdges, topNode);
    setResults(prev => [result, ...prev]);
    onRemoveNode(topNode.id);
  };

  const handleCascade = () => {
    const sorted = [...activeNodes].sort((a, b) => b.degree - a.degree);
    const count = Math.min(5, sorted.length);
    const newResults: SimulationResult[] = [];
    let currentNodes = [...activeNodes];
    let currentEdges = [...activeEdges];

    for (let i = 0; i < count; i++) {
      const top = currentNodes.sort((a, b) => b.degree - a.degree)[0];
      if (!top) break;
      const result = simulateRemoval(currentNodes, currentEdges, top);
      newResults.push(result);
      onRemoveNode(top.id);
      currentNodes = currentNodes.filter(n => n.id !== top.id);
      currentEdges = currentEdges.filter(e => e.source !== top.id && e.target !== top.id);
    }
    setResults(prev => [...newResults, ...prev]);
  };

  const handleReset = () => {
    setResults([]);
    onResetRemovals();
  };

  return (
    <div className="h-full overflow-y-auto p-4 space-y-4">
      <h2 className="text-xs uppercase tracking-widest text-muted-foreground">Analyse de réseau</h2>

      {/* Actions */}
      <div className="space-y-2">
        <button
          onClick={handleRemoveTop}
          className="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg bg-destructive/10 border border-destructive/30 text-destructive hover:bg-destructive/20 transition-colors text-sm"
        >
          <Trash2 size={14} />
          Supprimer le plus grand nœud (degré)
        </button>
        <button
          onClick={handleRemoveTopPageRank}
          className="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg bg-accent/10 border border-accent/30 text-accent hover:bg-accent/20 transition-colors text-sm"
        >
          <Zap size={14} />
          Supprimer top PageRank
        </button>
        <button
          onClick={handleCascade}
          className="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg bg-neon-amber/10 border border-neon-amber/30 text-neon-amber hover:bg-neon-amber/20 transition-colors text-sm"
        >
          <BarChart3 size={14} />
          Suppression en cascade (top 5)
        </button>
      </div>

      {removedNodes.size > 0 && (
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">
            {removedNodes.size} nœud{removedNodes.size > 1 ? 's' : ''} supprimé{removedNodes.size > 1 ? 's' : ''}
          </span>
          <button
            onClick={handleReset}
            className="text-xs text-primary hover:underline"
          >
            Réinitialiser
          </button>
        </div>
      )}

      {/* Results */}
      {results.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-xs uppercase tracking-widest text-muted-foreground">Résultats</h3>
          {results.map((r, i) => (
            <div key={i} className="glass rounded-lg p-3 space-y-2">
              <div className="flex items-center gap-2">
                <AlertTriangle size={12} className="text-neon-amber" />
                <span className="font-mono text-xs">{shortenAddress(r.removedNode.id)}</span>
                <span className="ml-auto text-xs font-bold" style={{ color: getNodeColor(r.removedNode.community) }}>
                  C{r.removedNode.community}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-[11px]">
                <div>
                  <span className="text-muted-foreground">Arêtes perdues</span>
                  <p className="font-medium text-destructive">
                    -{r.beforeStats.totalEdges - r.afterStats.totalEdges}
                  </p>
                </div>
                <div>
                  <span className="text-muted-foreground">Impact</span>
                  <p className="font-medium text-neon-amber">{r.impactScore.toFixed(1)}%</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Composantes</span>
                  <p className="font-medium">{r.componentsAfter}</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Degré</span>
                  <p className="font-medium">{r.removedNode.degree}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
