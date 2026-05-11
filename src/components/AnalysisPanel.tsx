import { useState } from 'react';
import { NodeData, EdgeData, SimulationResult } from '@/lib/graphTypes';
import { 
  simulateRemoval, 
  shortenAddress, 
  getNodeColor,
  calculateClustering,
  detectBridges,
  calculateBetweenness,
  calculateDegreeDistribution,
  calculateAveragePathLength,
  calculateSimilarity,
  calculateKCore,
  simulateFlow,
  findShortestPath,
  analyzeNetworkTopology,
  analyzeCentrality,
  analyzeSmallWorldProperties,
  analyzeWeightedFlows,
  analyzeTemporalDynamics
} from '@/lib/graphUtils';
import { 
  Trash2, 
  Zap, 
  BarChart3, 
  AlertTriangle, 
  Network,
  GitBranch,
  Target,
  TrendingUp,
  Route,
  Users,
  Layers,
  Share2
} from 'lucide-react';

interface AnalysisPanelProps {
  nodes: NodeData[];
  edges: EdgeData[];
  removedNodes: Set<string>;
  onRemoveNode: (nodeId: string) => void;
  onRemoveNodes: (nodeIds: string[]) => void;
  onResetRemovals: () => void;
  onVisualize: (nodes: string[], edges: Array<{source: string, target: string}>, mode: string) => void;
  onClearVisualization: () => void;
}

export default function AnalysisPanel({ 
  nodes, 
  edges, 
  removedNodes, 
  onRemoveNode,
  onRemoveNodes,
  onResetRemovals,
  onVisualize,
  onClearVisualization
}: AnalysisPanelProps) {
  const [results, setResults] = useState<SimulationResult[]>([]);
  const [analysisResults, setAnalysisResults] = useState<any>(null);
  const [activeAnalysis, setActiveAnalysis] = useState<string | null>(null);

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
    const nodesToRemove: string[] = [];
    let currentNodes = [...activeNodes];
    let currentEdges = [...activeEdges];

    for (let i = 0; i < count; i++) {
      const top = currentNodes.sort((a, b) => b.degree - a.degree)[0];
      if (!top) break;
      const result = simulateRemoval(currentNodes, currentEdges, top);
      newResults.push(result);
      nodesToRemove.push(top.id);
      currentNodes = currentNodes.filter(n => n.id !== top.id);
      currentEdges = currentEdges.filter(e => e.source !== top.id && e.target !== top.id);
    }
    
    setResults(prev => [...newResults, ...prev]);
    // Remove all nodes at once to avoid multiple re-renders
    onRemoveNodes(nodesToRemove);
  };

  const handleReset = () => {
    setResults([]);
    onResetRemovals();
  };

  // New analysis handlers
  const runClusteringAnalysis = () => {
    const result = calculateClustering(activeNodes, activeEdges);
    setAnalysisResults(result);
    setActiveAnalysis('clustering');
  };

  const runBridgeDetection = () => {
    const result = detectBridges(activeNodes, activeEdges);
    setAnalysisResults(result);
    setActiveAnalysis('bridges');
    // Visualize bridges on graph
    onVisualize(
      result.flatMap((b: any) => [b.source, b.target]),
      result,
      'bridges'
    );
  };

  const runBetweennessAnalysis = () => {
    const result = calculateBetweenness(activeNodes, activeEdges);
    setAnalysisResults(result);
    setActiveAnalysis('betweenness');
  };

  const runDegreeDistribution = () => {
    const result = calculateDegreeDistribution(activeNodes);
    setAnalysisResults(result);
    setActiveAnalysis('distribution');
  };

  const runPathAnalysis = () => {
    // Find shortest path between two high-degree nodes
    const sorted = [...activeNodes].sort((a, b) => b.degree - a.degree);
    if (sorted.length < 2) return;
    
    const result = findShortestPath(activeNodes, activeEdges, sorted[0].id, sorted[1].id);
    setAnalysisResults(result);
    setActiveAnalysis('path');
    
    if (result) {
      onVisualize(result.path, result.edges, 'path');
    }
  };

  const runSimilarityAnalysis = () => {
    const result = calculateSimilarity(activeNodes, activeEdges, 15);
    setAnalysisResults(result);
    setActiveAnalysis('similarity');
  };

  const runKCoreAnalysis = () => {
    const result = calculateKCore(activeNodes, activeEdges);
    setAnalysisResults(result);
    setActiveAnalysis('kcore');
    // Highlight top k-core nodes
    const topKCore = result.distribution
      .filter((n: any) => n.coreness >= result.maxK - 1)
      .map((n: any) => n.nodeId);
    onVisualize(topKCore, [], 'kcore');
  };

  const runFlowSimulation = () => {
    const topNode = [...activeNodes].sort((a, b) => b.degree - a.degree)[0];
    if (!topNode) return;
    const result = simulateFlow(activeNodes, activeEdges, topNode.id, 0.3, 10);
    setAnalysisResults(result);
    setActiveAnalysis('flow');
  };

  // ===== RESEARCH QUESTIONS HANDLERS =====

  const runRQ1Topology = () => {
    const result = analyzeNetworkTopology(activeNodes, activeEdges);
    setAnalysisResults(result);
    setActiveAnalysis('rq1');
  };

  const runRQ2Centrality = () => {
    const result = analyzeCentrality(activeNodes, activeEdges);
    setAnalysisResults(result);
    setActiveAnalysis('rq2');
  };

  const runRQ5SmallWorld = () => {
    const result = analyzeSmallWorldProperties(activeNodes, activeEdges);
    setAnalysisResults(result);
    setActiveAnalysis('rq5');
  };

  const runRQ6WeightedFlows = () => {
    const result = analyzeWeightedFlows(activeNodes, activeEdges);
    setAnalysisResults(result);
    setActiveAnalysis('rq6');
  };

  const runRQ4Temporal = () => {
    const result = analyzeTemporalDynamics(activeNodes, activeEdges);
    setAnalysisResults(result);
    setActiveAnalysis('rq4');
  };

  return (
    <div className="h-full overflow-y-auto p-4 space-y-4">
      <h2 className="text-xs uppercase tracking-widest text-muted-foreground">Analyse de réseau</h2>

      {/* Removal Actions */}
      <div className="space-y-2">
        <h3 className="text-[10px] uppercase tracking-wider text-muted-foreground/70">Suppression</h3>
        <button
          onClick={handleRemoveTop}
          className="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg bg-destructive/10 border border-destructive/30 text-destructive hover:bg-destructive/20 transition-colors text-sm"
        >
          <Trash2 size={14} />
          Supprimer plus grand nœud
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
          Cascade (top 5)
        </button>
      </div>

      {/* Advanced Analyses */}
      <div className="space-y-2">
        <h3 className="text-[10px] uppercase tracking-wider text-muted-foreground/70">Analyses Avancées</h3>
        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={runClusteringAnalysis}
            className="flex items-center gap-1.5 px-2.5 py-2 rounded-lg bg-primary/10 border border-primary/30 hover:bg-primary/20 transition-colors text-xs"
          >
            <Network size={12} />
            Clustering
          </button>
          <button
            onClick={runBridgeDetection}
            className="flex items-center gap-1.5 px-2.5 py-2 rounded-lg bg-primary/10 border border-primary/30 hover:bg-primary/20 transition-colors text-xs"
          >
            <GitBranch size={12} />
            Ponts
          </button>
          <button
            onClick={runBetweennessAnalysis}
            className="flex items-center gap-1.5 px-2.5 py-2 rounded-lg bg-primary/10 border border-primary/30 hover:bg-primary/20 transition-colors text-xs"
          >
            <Target size={12} />
            Betweenness
          </button>
          <button
            onClick={runDegreeDistribution}
            className="flex items-center gap-1.5 px-2.5 py-2 rounded-lg bg-primary/10 border border-primary/30 hover:bg-primary/20 transition-colors text-xs"
          >
            <TrendingUp size={12} />
            Distribution
          </button>
          <button
            onClick={runPathAnalysis}
            className="flex items-center gap-1.5 px-2.5 py-2 rounded-lg bg-primary/10 border border-primary/30 hover:bg-primary/20 transition-colors text-xs"
          >
            <Route size={12} />
            Chemins
          </button>
          <button
            onClick={runSimilarityAnalysis}
            className="flex items-center gap-1.5 px-2.5 py-2 rounded-lg bg-primary/10 border border-primary/30 hover:bg-primary/20 transition-colors text-xs"
          >
            <Users size={12} />
            Similarité
          </button>
          <button
            onClick={runKCoreAnalysis}
            className="flex items-center gap-1.5 px-2.5 py-2 rounded-lg bg-primary/10 border border-primary/30 hover:bg-primary/20 transition-colors text-xs"
          >
            <Layers size={12} />
            K-Core
          </button>
          <button
            onClick={runFlowSimulation}
            className="flex items-center gap-1.5 px-2.5 py-2 rounded-lg bg-primary/10 border border-primary/30 hover:bg-primary/20 transition-colors text-xs"
          >
            <Share2 size={12} />
            Flux
          </button>
        </div>
      </div>

      {/* Research Questions Analyses */}
      <div className="space-y-2">
        <h3 className="text-[10px] uppercase tracking-wider text-muted-foreground/70">Questions de Recherche (RQ)</h3>
        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={runRQ1Topology}
            className="flex items-center gap-1.5 px-2.5 py-2 rounded-lg bg-blue-500/10 border border-blue-500/30 hover:bg-blue-500/20 transition-colors text-xs"
          >
            <Network size={12} />
            RQ1: Topologie
          </button>
          <button
            onClick={runRQ2Centrality}
            className="flex items-center gap-1.5 px-2.5 py-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 hover:bg-cyan-500/20 transition-colors text-xs"
          >
            <Target size={12} />
            RQ2: Centralité
          </button>
          <button
            onClick={runClusteringAnalysis}
            className="flex items-center gap-1.5 px-2.5 py-2 rounded-lg bg-green-500/10 border border-green-500/30 hover:bg-green-500/20 transition-colors text-xs"
          >
            <Network size={12} />
            RQ3: Clustering
          </button>
          <button
            onClick={runRQ5SmallWorld}
            className="flex items-center gap-1.5 px-2.5 py-2 rounded-lg bg-purple-500/10 border border-purple-500/30 hover:bg-purple-500/20 transition-colors text-xs"
          >
            <Layers size={12} />
            RQ5: Small-World
          </button>
          <button
            onClick={runRQ6WeightedFlows}
            className="flex items-center gap-1.5 px-2.5 py-2 rounded-lg bg-amber-500/10 border border-amber-500/30 hover:bg-amber-500/20 transition-colors text-xs"
          >
            <TrendingUp size={12} />
            RQ6: Flux Pondérés
          </button>
          <button
            onClick={runRQ4Temporal}
            className="flex items-center gap-1.5 px-2.5 py-2 rounded-lg bg-rose-500/10 border border-rose-500/30 hover:bg-rose-500/20 transition-colors text-xs col-span-2"
          >
            <Share2 size={12} />
            RQ4: Analyse Temporelle
          </button>
        </div>
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

      {/* Analysis Results */}
      {activeAnalysis && analysisResults && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-xs uppercase tracking-widest text-muted-foreground">Résultats</h3>
            <button
              onClick={() => {
                setActiveAnalysis(null);
                onClearVisualization();
              }}
              className="text-xs text-muted-foreground hover:text-primary"
            >
              Fermer
            </button>
          </div>
          
          {activeAnalysis === 'clustering' && (
            <div className="glass rounded-lg p-3 space-y-2">
              <div className="flex items-center gap-2">
                <Network size={14} className="text-primary" />
                <span className="font-semibold text-sm">Coefficient de Clustering</span>
              </div>
              <div className="text-xs space-y-1">
                <p><span className="text-muted-foreground">Moyenne:</span> <span className="font-bold text-primary">{analysisResults.average.toFixed(4)}</span></p>
                <p className="text-[11px] text-muted-foreground mt-2">Top 5 nœuds avec clustering élevé:</p>
                {analysisResults.distribution
                  .filter((d: any) => d.coefficient > 0)
                  .sort((a: any, b: any) => b.coefficient - a.coefficient)
                  .slice(0, 5)
                  .map((d: any, i: number) => (
                    <div key={i} className="flex justify-between text-[10px] font-mono">
                      <span>{shortenAddress(d.nodeId)}</span>
                      <span className="text-primary">{d.coefficient.toFixed(3)}</span>
                    </div>
                  ))}
              </div>
            </div>
          )}

          {activeAnalysis === 'bridges' && (
            <div className="glass rounded-lg p-3 space-y-2">
              <div className="flex items-center gap-2">
                <GitBranch size={14} className="text-destructive" />
                <span className="font-semibold text-sm">Ponts Critiques</span>
              </div>
              <div className="text-xs space-y-1">
                <p><span className="text-muted-foreground">Nombre de ponts:</span> <span className="font-bold text-destructive">{analysisResults.length}</span></p>
                {analysisResults.length > 0 ? (
                  <>
                    <p className="text-[11px] text-muted-foreground mt-2">Exemples de ponts:</p>
                    {analysisResults.slice(0, 5).map((b: any, i: number) => (
                      <div key={i} className="text-[10px] font-mono flex gap-1">
                        <span>{shortenAddress(b.source)}</span>
                        <span className="text-muted-foreground">→</span>
                        <span>{shortenAddress(b.target)}</span>
                      </div>
                    ))}
                  </>
                ) : (
                  <p className="text-[11px] text-green-500">Réseau robuste, aucun pont critique</p>
                )}
              </div>
            </div>
          )}

          {activeAnalysis === 'betweenness' && (
            <div className="glass rounded-lg p-3 space-y-2">
              <div className="flex items-center gap-2">
                <Target size={14} className="text-neon-amber" />
                <span className="font-semibold text-sm">Centralité Intermédiaire</span>
              </div>
              <div className="text-xs space-y-1">
                <p className="text-[11px] text-muted-foreground">Top 5 nœuds de passage:</p>
                {analysisResults.slice(0, 5).map((b: any, i: number) => (
                  <div key={i} className="flex justify-between text-[10px] font-mono">
                    <span>{shortenAddress(b.nodeId)}</span>
                    <span className="text-neon-amber">{b.betweenness.toFixed(2)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeAnalysis === 'distribution' && (
            <div className="glass rounded-lg p-3 space-y-2">
              <div className="flex items-center gap-2">
                <TrendingUp size={14} className="text-accent" />
                <span className="font-semibold text-sm">Distribution des Degrés</span>
              </div>
              <div className="text-xs space-y-1">
                {analysisResults.slice(0, 8).map((d: any, i: number) => (
                  <div key={i} className="flex justify-between items-center text-[10px]">
                    <span className="text-muted-foreground">Degré {d.degree}:</span>
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-muted rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-accent" 
                          style={{ width: `${Math.min(100, d.percentage * 2)}%` }}
                        />
                      </div>
                      <span className="w-12 text-right">{d.count} ({d.percentage.toFixed(1)}%)</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeAnalysis === 'path' && (
            <div className="glass rounded-lg p-3 space-y-2">
              <div className="flex items-center gap-2">
                <Route size={14} className="text-primary" />
                <span className="font-semibold text-sm">Plus Court Chemin</span>
              </div>
              {analysisResults ? (
                <div className="text-xs space-y-1">
                  <p><span className="text-muted-foreground">Distance:</span> <span className="font-bold text-primary">{analysisResults.distance} sauts</span></p>
                  <p className="text-[11px] text-muted-foreground mt-2">Chemin:</p>
                  <div className="space-y-0.5">
                    {analysisResults.path.map((nodeId: string, i: number) => (
                      <div key={i} className="flex items-center gap-1 text-[10px] font-mono">
                        <span className="text-primary">{shortenAddress(nodeId)}</span>
                        {i < analysisResults.path.length - 1 && <span className="text-muted-foreground">→</span>}
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <p className="text-xs text-muted-foreground">Aucun chemin trouvé</p>
              )}
            </div>
          )}

          {activeAnalysis === 'similarity' && (
            <div className="glass rounded-lg p-3 space-y-2">
              <div className="flex items-center gap-2">
                <Users size={14} className="text-primary" />
                <span className="font-semibold text-sm">Similarité entre Nœuds</span>
              </div>
              <div className="text-xs space-y-1">
                <p className="text-[11px] text-muted-foreground">Paires les plus similaires:</p>
                {analysisResults.slice(0, 5).map((s: any, i: number) => (
                  <div key={i} className="space-y-0.5">
                    <div className="flex justify-between text-[10px] font-mono">
                      <span>{shortenAddress(s.nodeA)} ↔ {shortenAddress(s.nodeB)}</span>
                      <span className="text-primary">{(s.similarity * 100).toFixed(0)}%</span>
                    </div>
                    <p className="text-[9px] text-muted-foreground">{s.commonNeighbors} voisins communs</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeAnalysis === 'kcore' && (
            <div className="glass rounded-lg p-3 space-y-2">
              <div className="flex items-center gap-2">
                <Layers size={14} className="text-accent" />
                <span className="font-semibold text-sm">K-Core Decomposition</span>
              </div>
              <div className="text-xs space-y-1">
                <p><span className="text-muted-foreground">K-core max:</span> <span className="font-bold text-accent">{analysisResults.maxK}</span></p>
                <p className="text-[11px] text-muted-foreground mt-2">Top 5 nœuds du cœur:</p>
                {analysisResults.distribution.slice(0, 5).map((k: any, i: number) => (
                  <div key={i} className="flex justify-between text-[10px] font-mono">
                    <span>{shortenAddress(k.nodeId)}</span>
                    <span className="text-accent">k={k.coreness}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeAnalysis === 'flow' && (
            <div className="glass rounded-lg p-3 space-y-2">
              <div className="flex items-center gap-2">
                <Share2 size={14} className="text-primary" />
                <span className="font-semibold text-sm">Simulation de Flux</span>
              </div>
              <div className="text-xs space-y-1">
                <p className="text-[11px] text-muted-foreground">Propagation (prob=30%):</p>
                {analysisResults.map((f: any, i: number) => (
                  <div key={i} className="flex justify-between items-center text-[10px]">
                    <span className="text-muted-foreground">Étape {f.step}:</span>
                    <div className="flex items-center gap-2">
                      <div className="w-20 h-1.5 bg-muted rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-primary" 
                          style={{ width: `${(f.infected / activeNodes.length) * 100}%` }}
                        />
                      </div>
                      <span className="w-16 text-right">{f.infected} ({((f.infected / activeNodes.length) * 100).toFixed(0)}%)</span>
                    </div>
                  </div>
                ))}
                <p className="text-[11px] text-muted-foreground mt-2">
                  Taux final: {((analysisResults[analysisResults.length - 1].infected / activeNodes.length) * 100).toFixed(1)}%
                </p>
              </div>
            </div>
          )}

          {/* RQ1: Topology */}
          {activeAnalysis === 'rq1' && (
            <div className="glass rounded-lg p-3 space-y-2 border-l-4 border-blue-500">
              <div className="flex items-center gap-2">
                <Network size={14} className="text-blue-500" />
                <span className="font-semibold text-sm">RQ1: Topologie du Réseau</span>
              </div>
              <div className="text-xs space-y-1">
                <p className="text-[11px] text-muted-foreground">Métriques globales:</p>
                <div className="grid grid-cols-2 gap-2 text-[10px]">
                  <div><span className="text-muted-foreground">Deg. moyen:</span> <span className="font-bold text-blue-500">{analysisResults.avgDegree.toFixed(2)}</span></div>
                  <div><span className="text-muted-foreground">Deg. max:</span> <span className="font-bold text-blue-500">{analysisResults.maxDegree}</span></div>
                  <div><span className="text-muted-foreground">Densité:</span> <span className="font-bold text-blue-500">{analysisResults.density.toFixed(4)}</span></div>
                  <div><span className="text-muted-foreground">Diamètre:</span> <span className="font-bold text-blue-500">{analysisResults.diameter}</span></div>
                  <div className="col-span-2"><span className="text-muted-foreground">Composantes:</span> <span className="font-bold text-blue-500">{analysisResults.connectedComponents}</span></div>
                </div>
              </div>
            </div>
          )}

          {/* RQ2: Centrality */}
          {activeAnalysis === 'rq2' && (
            <div className="glass rounded-lg p-3 space-y-2 border-l-4 border-cyan-500">
              <div className="flex items-center gap-2">
                <Target size={14} className="text-cyan-500" />
                <span className="font-semibold text-sm">RQ2: Mesures de Centralité</span>
              </div>
              <div className="text-xs space-y-2">
                <div>
                  <p className="text-[10px] text-muted-foreground font-bold mb-1">Top par degré:</p>
                  {analysisResults.topByDegree.slice(0, 3).map((d: any, i: number) => (
                    <div key={i} className="text-[9px] text-cyan-500">{shortenAddress(d.id)}: {d.value}</div>
                  ))}
                </div>
                <div>
                  <p className="text-[10px] text-muted-foreground font-bold mb-1">Top par PageRank:</p>
                  {analysisResults.topByPageRank.slice(0, 3).map((d: any, i: number) => (
                    <div key={i} className="text-[9px] text-cyan-500">{shortenAddress(d.id)}: {d.value.toFixed(4)}</div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* RQ5: Small-World */}
          {activeAnalysis === 'rq5' && (
            <div className="glass rounded-lg p-3 space-y-2 border-l-4 border-purple-500">
              <div className="flex items-center gap-2">
                <Layers size={14} className="text-purple-500" />
                <span className="font-semibold text-sm">RQ5: Propriétés Small-World</span>
              </div>
              <div className="text-xs space-y-1">
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <p className="text-[10px] text-muted-foreground">Coeff. clustering:</p>
                    <p className="font-bold text-purple-500">{analysisResults.avgClusteringCoeff.toFixed(4)}</p>
                  </div>
                  <div>
                    <p className="text-[10px] text-muted-foreground">Chemin moyen:</p>
                    <p className="font-bold text-purple-500">{analysisResults.avgPathLength.toFixed(2)}</p>
                  </div>
                  <div className="col-span-2">
                    <p className="text-[10px] text-muted-foreground">Est Small-World:</p>
                    <p className="font-bold" style={{color: analysisResults.isSmallWorld ? '#10b981' : '#ef4444'}}>
                      {analysisResults.isSmallWorld ? 'OUI' : 'NON'}
                    </p>
                  </div>
                </div>
                <p className="text-[9px] text-muted-foreground mt-1">
                  Comparaison aléatoire: c={analysisResults.randomClustering.toFixed(4)}, L={analysisResults.randomAvgPath.toFixed(2)}
                </p>
              </div>
            </div>
          )}

          {/* RQ6: Weighted Flows */}
          {activeAnalysis === 'rq6' && (
            <div className="glass rounded-lg p-3 space-y-2 border-l-4 border-amber-500">
              <div className="flex items-center gap-2">
                <TrendingUp size={14} className="text-amber-500" />
                <span className="font-semibold text-sm">RQ6: Flux Pondérés (Gini)</span>
              </div>
              <div className="text-xs space-y-1">
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <p className="text-[10px] text-muted-foreground">Coeff. Gini:</p>
                    <p className="font-bold text-amber-500">{analysisResults.giniCoefficient.toFixed(4)}</p>
                  </div>
                  <div>
                    <p className="text-[10px] text-muted-foreground">Concentration:</p>
                    <p className="font-bold text-amber-500">{analysisResults.concentration.toFixed(1)}%</p>
                  </div>
                  <div className="col-span-2">
                    <p className="text-[10px] text-muted-foreground">Distribution:</p>
                    <p className="font-bold text-amber-500">{analysisResults.flowDistribution}</p>
                  </div>
                </div>
                <p className="text-[9px] text-muted-foreground mt-1">
                  Flux moyen par nœud: {analysisResults.avgFlowPerNode.toFixed(2)} | Max: {analysisResults.maxFlow}
                </p>
              </div>
            </div>
          )}

          {/* RQ4: Temporal */}
          {activeAnalysis === 'rq4' && (
            <div className="glass rounded-lg p-3 space-y-2 border-l-4 border-rose-500">
              <div className="flex items-center gap-2">
                <Share2 size={14} className="text-rose-500" />
                <span className="font-semibold text-sm">RQ4: Analyse Temporelle</span>
              </div>
              <div className="text-xs space-y-1">
                <p className="text-[10px] text-muted-foreground">Heures de pointe: {analysisResults.peakHours.join(', ')}</p>
                <p className="text-[10px] text-yellow-600 bg-yellow-500/10 rounded px-2 py-1 mt-2">
                  {analysisResults.recommendation}
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Removal Results */}
      {results.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-xs uppercase tracking-widest text-muted-foreground">Résultats Suppressions</h3>
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
