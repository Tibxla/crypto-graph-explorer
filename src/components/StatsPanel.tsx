import { useState } from 'react';
import { ChevronUp, ChevronDown, X } from 'lucide-react';
import { NodeData, GraphStats } from '@/lib/graphTypes';
import { getNodeColor, shortenAddress } from '@/lib/graphUtils';

interface StatsPanelProps {
  stats: GraphStats;
  selectedNode: NodeData | null;
  topNodes: NodeData[];
  onNodeSelect: (node: NodeData) => void;
}

export default function StatsPanel({ stats, selectedNode, topNodes, onNodeSelect }: StatsPanelProps) {
  const [showSelectedNode, setShowSelectedNode] = useState(true);
  const [showTopNodes, setShowTopNodes] = useState(true);

  return (
    <div className="h-full overflow-y-auto p-4 space-y-4 bg-gradient-to-b from-card/50 to-background/50">
      {/* Network overview */}
      <div className="rounded-lg border border-border/50 bg-card/40 p-4 backdrop-blur-sm">
        <h2 className="text-xs uppercase tracking-widest text-primary font-bold mb-4">Vue d'ensemble</h2>
        <div className="grid grid-cols-2 gap-2.5">
          <StatCard label="Nœuds" value={stats.totalNodes.toLocaleString()} />
          <StatCard label="Arêtes" value={stats.totalEdges.toLocaleString()} />
          <StatCard label="Degré moy." value={stats.avgDegree.toFixed(1)} />
          <StatCard label="Communautés" value={stats.communities.toString()} />
        </div>
      </div>

      {/* Selected node - Collapsible */}
      {selectedNode && (
        <div className="rounded-lg border border-primary/20 bg-gradient-to-br from-primary/5 to-primary/2 backdrop-blur-sm overflow-hidden">
          {/* Header */}
          <button
            onClick={() => setShowSelectedNode(!showSelectedNode)}
            className="w-full flex items-center justify-between px-4 py-3 hover:bg-primary/5 transition-colors border-b border-primary/10"
          >
            <div className="flex items-center gap-3 flex-1 min-w-0">
              <div
                className="w-3 h-3 rounded-full flex-shrink-0 shadow-md ring-2 ring-primary/30"
                style={{ backgroundColor: getNodeColor(selectedNode.community) }}
              />
              <div className="flex-1 min-w-0 text-left">
                <p className="font-mono text-xs uppercase tracking-wider text-primary/70 mb-0.5">Nœud sélectionné</p>
                <p className="font-mono text-sm font-bold text-foreground truncate">{shortenAddress(selectedNode.id)}</p>
              </div>
            </div>
            <div className="flex items-center gap-2 flex-shrink-0">
              {showSelectedNode ? (
                <ChevronUp size={16} className="text-primary/60" />
              ) : (
                <ChevronDown size={16} className="text-primary/60" />
              )}
            </div>
          </button>

          {/* Content */}
          {showSelectedNode && (
            <div className="px-4 py-3 space-y-4 border-t border-primary/10">
              {/* Full address */}
              <div className="bg-background/50 rounded-md p-2.5 border border-border/30">
                <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1">Adresse complète</p>
                <p className="font-mono text-[11px] text-primary break-all leading-relaxed">{selectedNode.id}</p>
              </div>

              {/* Community */}
              <div className="flex items-center gap-2 bg-background/50 rounded-md p-2.5 border border-border/30">
                <span className="text-[10px] uppercase tracking-wider text-muted-foreground">Communauté:</span>
                <span className="font-bold text-primary">{selectedNode.community}</span>
              </div>

              {/* Stats grid */}
              <div className="grid grid-cols-2 gap-2">
                <StatBox label="Degré" value={selectedNode.degree} />
                <StatBox label="In-degree" value={selectedNode.in_degree} />
                <StatBox label="Out-degree" value={selectedNode.out_degree} />
                <StatBox label="PageRank" value={selectedNode.pagerank.toFixed(6)} />
              </div>

              {/* Clear selection */}
              <button
                onClick={() => onNodeSelect(null)}
                className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-md border border-destructive/30 hover:border-destructive/60 hover:bg-destructive/5 transition-all text-xs text-destructive font-medium"
              >
                <X size={14} />
                Désélectionner
              </button>
            </div>
          )}
        </div>
      )}

      {/* Top nodes - Collapsible */}
      <div className="rounded-lg border border-border/50 bg-card/40 backdrop-blur-sm overflow-hidden">
        <button
          onClick={() => setShowTopNodes(!showTopNodes)}
          className="w-full flex items-center justify-between px-4 py-3 hover:bg-secondary/30 transition-colors border-b border-border/30"
        >
          <h2 className="text-xs uppercase tracking-widest text-primary font-bold">Top 10 nœuds</h2>
          {showTopNodes ? (
            <ChevronUp size={16} className="text-muted-foreground" />
          ) : (
            <ChevronDown size={16} className="text-muted-foreground" />
          )}
        </button>
        {showTopNodes && (
          <div className="p-4 space-y-2">
            {topNodes.slice(0, 10).map((node, i) => (
              <button
                key={node.id}
                onClick={() => onNodeSelect(node)}
                className="w-full flex items-center gap-2.5 px-2.5 py-2.5 rounded-md text-left hover:bg-primary/10 transition-all duration-200 border border-transparent hover:border-primary/40 group"
              >
                <span className="text-xs font-bold text-muted-foreground w-5 text-center group-hover:text-primary transition-colors">{i + 1}</span>
                <div
                  className="w-3 h-3 rounded-full flex-shrink-0 shadow-md ring-1 ring-offset-1 ring-offset-background ring-primary/20"
                  style={{ backgroundColor: getNodeColor(node.community) }}
                />
                <span className="font-mono text-[11px] truncate flex-1 text-foreground">{shortenAddress(node.id)}</span>
                <span className="text-xs text-primary font-semibold tabular-nums group-hover:text-primary transition-colors">{node.degree}</span>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-border/40 bg-background/60 p-2.5 hover:border-primary/40 transition-colors">
      <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1.5">{label}</p>
      <p className="text-base font-bold text-primary">{value}</p>
    </div>
  );
}

function StatBox({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="bg-background/50 rounded-md p-2.5 border border-border/30 hover:border-primary/30 transition-colors">
      <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1.5">{label}</p>
      <p className="text-sm font-bold text-primary">{value}</p>
    </div>
  );
}
