import Papa from 'papaparse';
import { NodeData, EdgeData, GraphStats, SimulationResult, COMMUNITY_COLORS } from './graphTypes';

export function parseCSV(csvText: string): NodeData[] {
  const result = Papa.parse(csvText, { header: true, skipEmptyLines: true });
  return result.data.map((row: any) => ({
    id: row.id,
    degree: Number(row.degree) || 0,
    in_degree: Number(row.in_degree) || 0,
    out_degree: Number(row.out_degree) || 0,
    pagerank: Number(row.pagerank) || 0,
    community: Number(row.community) || 0,
  }));
}

export function generateEdges(nodes: NodeData[]): EdgeData[] {
  const edges: EdgeData[] = [];
  const communityMap = new Map<number, NodeData[]>();
  
  nodes.forEach(n => {
    const list = communityMap.get(n.community) || [];
    list.push(n);
    communityMap.set(n.community, list);
  });

  // Connect nodes within same community based on degree
  communityMap.forEach((members) => {
    const sorted = [...members].sort((a, b) => b.degree - a.degree);
    for (let i = 0; i < sorted.length; i++) {
      const connectCount = Math.min(Math.ceil(sorted[i].out_degree * 0.3), 5);
      for (let j = 0; j < connectCount && j < sorted.length; j++) {
        if (i !== j) {
          edges.push({ source: sorted[i].id, target: sorted[j].id });
        }
      }
    }
  });

  // Add some cross-community edges for high-degree nodes
  const topNodes = [...nodes].sort((a, b) => b.degree - a.degree).slice(0, 20);
  for (let i = 0; i < topNodes.length; i++) {
    for (let j = i + 1; j < Math.min(i + 3, topNodes.length); j++) {
      if (topNodes[i].community !== topNodes[j].community) {
        edges.push({ source: topNodes[i].id, target: topNodes[j].id });
      }
    }
  }

  return edges;
}

export function computeStats(nodes: NodeData[], edges: EdgeData[]): GraphStats {
  const degrees = nodes.map(n => n.degree);
  const communities = new Set(nodes.map(n => n.community));
  const maxPossibleEdges = nodes.length * (nodes.length - 1) / 2;
  
  return {
    totalNodes: nodes.length,
    totalEdges: edges.length,
    avgDegree: degrees.reduce((a, b) => a + b, 0) / nodes.length,
    maxDegree: Math.max(...degrees),
    communities: communities.size,
    density: maxPossibleEdges > 0 ? edges.length / maxPossibleEdges : 0,
  };
}

export function simulateRemoval(
  nodes: NodeData[],
  edges: EdgeData[],
  nodeToRemove: NodeData
): SimulationResult {
  const beforeStats = computeStats(nodes, edges);
  
  const remainingNodes = nodes.filter(n => n.id !== nodeToRemove.id);
  const remainingEdges = edges.filter(
    e => e.source !== nodeToRemove.id && e.target !== nodeToRemove.id
  );
  
  const afterStats = computeStats(remainingNodes, remainingEdges);
  
  // Estimate connected components (simplified)
  const nodeSet = new Set(remainingNodes.map(n => n.id));
  const adj = new Map<string, Set<string>>();
  remainingNodes.forEach(n => adj.set(n.id, new Set()));
  remainingEdges.forEach(e => {
    adj.get(e.source)?.add(e.target);
    adj.get(e.target)?.add(e.source);
  });
  
  const visited = new Set<string>();
  let components = 0;
  
  for (const nodeId of nodeSet) {
    if (!visited.has(nodeId)) {
      components++;
      const stack = [nodeId];
      while (stack.length) {
        const curr = stack.pop()!;
        if (visited.has(curr)) continue;
        visited.add(curr);
        adj.get(curr)?.forEach(neighbor => {
          if (!visited.has(neighbor)) stack.push(neighbor);
        });
      }
    }
  }
  
  const edgeLoss = (beforeStats.totalEdges - afterStats.totalEdges) / beforeStats.totalEdges;
  const impactScore = edgeLoss * 100;
  
  return {
    removedNode: nodeToRemove,
    beforeStats,
    afterStats,
    componentsBefore: 1,
    componentsAfter: components,
    impactScore,
  };
}

export function getNodeColor(community: number): string {
  return COMMUNITY_COLORS[community % COMMUNITY_COLORS.length];
}

export function shortenAddress(addr: string): string {
  if (addr.length <= 12) return addr;
  return `${addr.slice(0, 6)}...${addr.slice(-4)}`;
}
