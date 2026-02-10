import { NodeData, GraphStats } from '@/lib/graphTypes';
import { getNodeColor, shortenAddress } from '@/lib/graphUtils';

interface StatsPanelProps {
  stats: GraphStats;
  selectedNode: NodeData | null;
  topNodes: NodeData[];
  onNodeSelect: (node: NodeData) => void;
}

export default function StatsPanel({ stats, selectedNode, topNodes, onNodeSelect }: StatsPanelProps) {
  return (
    <div className="h-full overflow-y-auto p-4 space-y-6">
      {/* Network overview */}
      <div>
        <h2 className="text-xs uppercase tracking-widest text-muted-foreground mb-3">Réseau</h2>
        <div className="grid grid-cols-2 gap-3">
          <StatCard label="Nœuds" value={stats.totalNodes.toLocaleString()} />
          <StatCard label="Arêtes" value={stats.totalEdges.toLocaleString()} />
          <StatCard label="Degré moy." value={stats.avgDegree.toFixed(1)} />
          <StatCard label="Communautés" value={stats.communities.toString()} />
        </div>
      </div>

      {/* Selected node */}
      {selectedNode && (
        <div>
          <h2 className="text-xs uppercase tracking-widest text-muted-foreground mb-3">Nœud sélectionné</h2>
          <div className="glass rounded-lg p-3 space-y-2">
            <div className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: getNodeColor(selectedNode.community) }}
              />
              <span className="font-mono text-xs text-primary">{shortenAddress(selectedNode.id)}</span>
            </div>
            <p className="font-mono text-[10px] text-muted-foreground break-all">{selectedNode.id}</p>
            <div className="grid grid-cols-2 gap-2 mt-2">
              <MiniStat label="Degré" value={selectedNode.degree} />
              <MiniStat label="In" value={selectedNode.in_degree} />
              <MiniStat label="Out" value={selectedNode.out_degree} />
              <MiniStat label="PageRank" value={selectedNode.pagerank.toFixed(6)} />
              <MiniStat label="Communauté" value={selectedNode.community} />
            </div>
          </div>
        </div>
      )}

      {/* Top nodes */}
      <div>
        <h2 className="text-xs uppercase tracking-widest text-muted-foreground mb-3">Top 10 (Degré)</h2>
        <div className="space-y-1">
          {topNodes.slice(0, 10).map((node, i) => (
            <button
              key={node.id}
              onClick={() => onNodeSelect(node)}
              className="w-full flex items-center gap-2 px-2 py-1.5 rounded text-left hover:bg-secondary/50 transition-colors"
            >
              <span className="text-xs text-muted-foreground w-4">{i + 1}</span>
              <div
                className="w-2 h-2 rounded-full flex-shrink-0"
                style={{ backgroundColor: getNodeColor(node.community) }}
              />
              <span className="font-mono text-[11px] truncate flex-1">{shortenAddress(node.id)}</span>
              <span className="text-xs text-primary font-medium">{node.degree}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="glass rounded-lg p-3">
      <p className="text-[10px] uppercase tracking-wider text-muted-foreground">{label}</p>
      <p className="text-lg font-bold text-primary glow-text">{value}</p>
    </div>
  );
}

function MiniStat({ label, value }: { label: string; value: string | number }) {
  return (
    <div>
      <p className="text-[10px] text-muted-foreground">{label}</p>
      <p className="text-sm font-medium">{value}</p>
    </div>
  );
}
