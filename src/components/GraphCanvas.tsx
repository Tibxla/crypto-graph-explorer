import { useEffect, useRef, useCallback, useState } from 'react';
import * as d3 from 'd3';
import { NodeData, EdgeData } from '@/lib/graphTypes';
import { getNodeColor, shortenAddress } from '@/lib/graphUtils';

interface GraphCanvasProps {
  nodes: NodeData[];
  edges: EdgeData[];
  onNodeSelect: (node: NodeData | null) => void;
  selectedNode: NodeData | null;
  removedNodes: Set<string>;
}

export default function GraphCanvas({ nodes, edges, onNodeSelect, selectedNode, removedNodes }: GraphCanvasProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  useEffect(() => {
    const obs = new ResizeObserver(entries => {
      const { width, height } = entries[0].contentRect;
      setDimensions({ width, height });
    });
    if (containerRef.current) obs.observe(containerRef.current);
    return () => obs.disconnect();
  }, []);

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const { width, height } = dimensions;
    const activeNodes = nodes.filter(n => !removedNodes.has(n.id));
    const activeNodeIds = new Set(activeNodes.map(n => n.id));
    const activeEdges = edges
      .filter(e => {
        const src = typeof e.source === 'object' ? (e.source as any).id : e.source;
        const tgt = typeof e.target === 'object' ? (e.target as any).id : e.target;
        return activeNodeIds.has(src) && activeNodeIds.has(tgt);
      })
      .map(e => ({
        source: typeof e.source === 'object' ? (e.source as any).id : e.source,
        target: typeof e.target === 'object' ? (e.target as any).id : e.target,
      }));

    const g = svg.append('g');

    // Zoom
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 8])
      .on('zoom', (event) => g.attr('transform', event.transform));
    svg.call(zoom);

    // Scale node sizes
    const maxDeg = Math.max(...activeNodes.map(n => n.degree), 1);
    const sizeScale = d3.scaleSqrt().domain([0, maxDeg]).range([3, 25]);

    const simulation = d3.forceSimulation(activeNodes as any)
      .force('link', d3.forceLink(activeEdges as any).id((d: any) => d.id).distance(80).strength(0.3))
      .force('charge', d3.forceManyBody().strength(-100).distanceMax(300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius((d: any) => sizeScale(d.degree) + 2));

    // Draw edges - thin gray lines
    const link = g.append('g')
      .selectAll('line')
      .data(activeEdges)
      .join('line')
      .attr('stroke', '#9ca3af')
      .attr('stroke-width', 1)
      .attr('stroke-opacity', 0.4);

    // Draw nodes
    const node = g.append('g')
      .selectAll('circle')
      .data(activeNodes)
      .join('circle')
      .attr('r', (d) => sizeScale(d.degree))
      .attr('fill', (d) => getNodeColor(d.community))
      .attr('fill-opacity', 0.8)
      .attr('stroke', (d) => selectedNode?.id === d.id ? '#fff' : 'transparent')
      .attr('stroke-width', 2)
      .attr('cursor', 'pointer')
      .on('click', (_, d) => onNodeSelect(d))
      .on('mouseenter', function(_, d) {
        d3.select(this).attr('fill-opacity', 1).attr('stroke', '#fff');
        tooltip.style('display', 'block')
          .html(`<strong>${shortenAddress(d.id)}</strong><br/>Degree: ${d.degree}<br/>PageRank: ${d.pagerank.toFixed(6)}`);
      })
      .on('mousemove', (event) => {
        tooltip.style('left', (event.offsetX + 15) + 'px').style('top', (event.offsetY - 10) + 'px');
      })
      .on('mouseleave', function(_, d) {
        d3.select(this)
          .attr('fill-opacity', 0.8)
          .attr('stroke', selectedNode?.id === d.id ? '#fff' : 'transparent');
        tooltip.style('display', 'none');
      })
      .call(d3.drag<any, any>()
        .on('start', (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x; d.fy = d.y;
        })
        .on('drag', (event, d) => { d.fx = event.x; d.fy = event.y; })
        .on('end', (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null; d.fy = null;
        })
      );

    // Tooltip
    const tooltip = d3.select(containerRef.current)
      .append('div')
      .attr('class', 'absolute pointer-events-none glass rounded px-3 py-2 text-xs font-mono z-50')
      .style('display', 'none');

    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);
      node.attr('cx', (d: any) => d.x).attr('cy', (d: any) => d.y);
    });

    return () => {
      simulation.stop();
      tooltip.remove();
    };
  }, [nodes, edges, dimensions, removedNodes, selectedNode, onNodeSelect]);

  return (
    <div ref={containerRef} className="relative w-full h-full grid-bg">
      <svg ref={svgRef} width={dimensions.width} height={dimensions.height} className="w-full h-full" />
    </div>
  );
}
