export interface NodeData {
  id: string;
  degree: number;
  in_degree: number;
  out_degree: number;
  pagerank: number;
  community: number;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  fx?: number | null;
  fy?: number | null;
}

export interface EdgeData {
  source: string;
  target: string;
}

export interface GraphStats {
  totalNodes: number;
  totalEdges: number;
  avgDegree: number;
  maxDegree: number;
  communities: number;
  density: number;
}

export interface SimulationResult {
  removedNode: NodeData;
  beforeStats: GraphStats;
  afterStats: GraphStats;
  componentsBefore: number;
  componentsAfter: number;
  impactScore: number;
}

export const COMMUNITY_COLORS = [
  'hsl(170, 80%, 50%)',   // cyan
  'hsl(280, 60%, 55%)',   // purple
  'hsl(45, 90%, 55%)',    // amber
  'hsl(340, 70%, 55%)',   // pink
  'hsl(200, 70%, 55%)',   // blue
  'hsl(120, 60%, 45%)',   // green
  'hsl(30, 80%, 55%)',    // orange
  'hsl(0, 70%, 55%)',     // red
  'hsl(60, 70%, 50%)',    // yellow
  'hsl(240, 50%, 60%)',   // indigo
];
