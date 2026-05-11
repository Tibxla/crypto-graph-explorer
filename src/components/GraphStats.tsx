import { useState } from 'react';
import { NodeData, EdgeData } from '@/lib/graphTypes';
import { Network, Link2, Activity, Badge, ChevronDown, ChevronUp } from 'lucide-react';

interface GraphStatsProps {
  nodes: NodeData[];
  edges: EdgeData[];
  loading?: boolean;
  selectedNode?: NodeData | null;
}

export default function GraphStats({ nodes, edges, loading = false, selectedNode }: GraphStatsProps) {
  const [isMinimized, setIsMinimized] = useState(false);

  // Calculate community count
  const communitySet = new Set(nodes.map(n => n.community));
  
  // Calculate community distribution
  const communities = Array.from(communitySet).map(c => {
    const count = nodes.filter(n => n.community === c).length;
    const avgPageRank = nodes
      .filter(n => n.community === c)
      .reduce((sum, n) => sum + n.pagerank, 0) / count;
    return { id: c, count, avgPageRank };
  }).sort((a, b) => b.count - a.count);

  if (loading) {
    return (
      <div className="absolute bottom-6 left-6 backdrop-blur-md bg-black/40 border border-white/10 rounded-lg p-4 text-white text-sm font-mono">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 animate-spin text-blue-400" />
          <span>Construction du graphe...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="absolute bottom-6 left-6 space-y-3 z-10 transition-all duration-300">
      {/* Main stats */}
      <div className="backdrop-blur-md bg-black/50 border border-white/20 rounded-lg p-4 text-white font-mono text-xs space-y-3 max-w-xs relative">
        
        {/* Toggle Button */}
        <button 
          onClick={() => setIsMinimized(!isMinimized)}
          className="absolute top-2 right-2 p-1 hover:bg-white/10 rounded-md transition-colors"
          title={isMinimized ? "Agrandir" : "Réduire"}
        >
          {isMinimized ? <ChevronUp size={14} className="text-gray-400" /> : <ChevronDown size={14} className="text-gray-400" />}
        </button>

        {/* Title */}
        <div className="text-center border-b border-white/20 pb-2 pr-6">
          <h3 className="font-bold text-blue-300 text-sm">CRYPTO-GRAPH-EXPLORER</h3>
          {!isMinimized && <p className="text-gray-400 text-[10px] mt-1">WETH/Polygon Network Analysis</p>}
        </div>

        {!isMinimized && (
          <>
            {/* Main metrics */}
            <div className="grid grid-cols-2 gap-2">
              <div>
                <div className="flex items-center gap-1 text-gray-400 mb-1">
                  <Badge className="w-3 h-3 text-blue-400" />
                  <span>Nœuds</span>
                </div>
                <div className="text-lg font-bold text-blue-300">{nodes.length.toLocaleString()}</div>
              </div>
              <div>
                <div className="flex items-center gap-1 text-gray-400 mb-1">
                  <Link2 className="w-3 h-3 text-cyan-400" />
                  <span>Liens</span>
                </div>
                <div className="text-lg font-bold text-cyan-300">{edges.length.toLocaleString()}</div>
              </div>
            </div>

            {/* Community distribution */}
            <div className="border-t border-white/20 pt-2">
              <div className="flex items-center gap-1 text-gray-400 mb-2">
                <Network className="w-3 h-3 text-purple-400" />
                <span>COMMUNAUTÉS DÉTECTÉES</span>
              </div>
              <div className="space-y-1">
                {communities.slice(0, 8).map((community, i) => (
                  <div key={i} className="flex justify-between items-center text-[11px]">
                    <div className="flex items-center gap-1.5">
                      <div 
                        className="w-2 h-2 rounded-full" 
                        style={{
                          backgroundColor: `hsl(${(community.id * 45) % 360}, 70%, 50%)`
                        }}
                      />
                      <span className="text-gray-300">C{community.id}</span>
                    </div>
                    <span className="text-gray-400">{community.count}</span>
                  </div>
                ))}
                {communities.length > 8 && (
                  <div className="text-[10px] text-gray-500 italic">
                    +{communities.length - 8} other communities
                  </div>
                )}
              </div>
            </div>

            {/* Selected node info */}
            {selectedNode && (
              <div className="border-t border-white/20 pt-2">
                <div className="text-[11px] text-gray-400 mb-1">SELECTED NODE</div>
                <div className="space-y-1">
                  <div className="flex justify-between text-[11px]">
                    <span className="text-gray-400">Address:</span>
                    <span className="text-green-300 font-bold">{selectedNode.id.slice(0, 10)}...</span>
                  </div>
                  <div className="flex justify-between text-[11px]">
                    <span className="text-gray-400">Degree:</span>
                    <span className="text-yellow-300 font-bold">{selectedNode.degree}</span>
                  </div>
                  <div className="flex justify-between text-[11px]">
                    <span className="text-gray-400">PageRank:</span>
                    <span className="text-amber-300 font-bold">{selectedNode.pagerank.toFixed(4)}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Status bar */}
            <div className="border-t border-white/20 pt-2 text-[10px] text-gray-400">
              <div className="flex justify-between items-center">
                <span>Prêt</span>
                <div className="flex gap-1">
                  <div className="w-1.5 h-1.5 rounded-full bg-green-400"></div>
                  <div className="w-1.5 h-1.5 rounded-full bg-green-400"></div>
                  <div className="w-1.5 h-1.5 rounded-full bg-green-400"></div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Instructions */}
      {!isMinimized && (
        <div className="backdrop-blur-md bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-white font-mono text-[10px]">
          <div className="text-gray-300"><span className="text-yellow-200">Sélectionnez un nœud pour voir les détails</span></div>
        </div>
      )}
    </div>
  );
}
