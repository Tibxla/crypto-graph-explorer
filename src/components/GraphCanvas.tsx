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
  highlightedNodes?: Set<string>;
  highlightedEdges?: Array<{source: string, target: string}>;
  visualizationMode?: string | null;
}

export default function GraphCanvas({ 
  nodes, 
  edges, 
  onNodeSelect, 
  selectedNode, 
  removedNodes,
  highlightedNodes = new Set(),
  highlightedEdges = [],
  visualizationMode = null
}: GraphCanvasProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const linkRef = useRef<any>(null);
  const nodeRef = useRef<any>(null);
  const draggingNodeRef = useRef<string | null>(null);

  useEffect(() => {
    const obs = new ResizeObserver(entries => {
      const { width, height } = entries[0].contentRect;
      setDimensions({ width, height });
    });
    if (containerRef.current) obs.observe(containerRef.current);
    return () => obs.disconnect();
  }, []);

  // Update edge and node styles when selectedNode changes
  useEffect(() => {
    if (!linkRef.current || !nodeRef.current) return;

    const isEdgeHighlighted = (d: any) => {
      const srcId = typeof d.source === 'object' ? d.source.id : d.source;
      const tgtId = typeof d.target === 'object' ? d.target.id : d.target;
      return highlightedEdges.some(e => 
        (e.source === srcId && e.target === tgtId) || 
        (e.source === tgtId && e.target === srcId)
      );
    };

    linkRef.current
      .transition()
      .duration(300)
      .attr('stroke', (d: any) => {
        if (highlightedEdges.length > 0 && isEdgeHighlighted(d)) {
          return visualizationMode === 'bridges' ? '#ef4444' : '#3b82f6';
        }
        if (!selectedNode) return '#d1d5db';
        const srcId = typeof d.source === 'object' ? d.source.id : d.source;
        const tgtId = typeof d.target === 'object' ? d.target.id : d.target;
        return (srcId === selectedNode.id || tgtId === selectedNode.id) ? '#1f2937' : '#d1d5db';
      })
      .attr('stroke-width', (d: any) => {
        if (highlightedEdges.length > 0 && isEdgeHighlighted(d)) return 4;
        if (!selectedNode) return 1.5;
        const srcId = typeof d.source === 'object' ? d.source.id : d.source;
        const tgtId = typeof d.target === 'object' ? d.target.id : d.target;
        return (srcId === selectedNode.id || tgtId === selectedNode.id) ? 3 : 1.5;
      })
      .attr('stroke-opacity', (d: any) => {
        if (highlightedEdges.length > 0) {
          return isEdgeHighlighted(d) ? 1 : 0.08;
        }
        if (!selectedNode) return 0.35;
        const srcId = typeof d.source === 'object' ? d.source.id : d.source;
        const tgtId = typeof d.target === 'object' ? d.target.id : d.target;
        return (srcId === selectedNode.id || tgtId === selectedNode.id) ? 0.95 : 0.15;
      })
      .attr('filter', (d: any) => {
        const srcId = typeof d.source === 'object' ? d.source.id : d.source;
        const tgtId = typeof d.target === 'object' ? d.target.id : d.target;
        if (selectedNode && (srcId === selectedNode.id || tgtId === selectedNode.id)) {
          return 'url(#edgeGlow)';
        }
        return 'none';
      });

    nodeRef.current.selectAll('g').select('circle:not([fill="transparent"])')
      .transition()
      .duration(300)
      .attr('stroke-width', (d: any) => {
        if (highlightedNodes.has(d.id)) return 6;
        return selectedNode?.id === d.id ? 5 : 2;
      })
      .attr('stroke', (d: any) => {
        if (highlightedNodes.has(d.id)) {
          if (visualizationMode === 'path') return '#3b82f6';
          if (visualizationMode === 'flow') return '#8b5cf6';
          if (visualizationMode === 'kcore') return '#10b981';
          return '#f59e0b';
        }
        return selectedNode?.id === d.id ? '#00ff88' : '#ffffff';
      })
      .attr('fill-opacity', (d: any) => {
        if (highlightedNodes.size > 0) {
          return highlightedNodes.has(d.id) ? 1 : 0.25;
        }
        if (selectedNode?.id === d.id) return 1;
        return 0.95;
      })
      .attr('filter', (d: any) => {
        if (selectedNode?.id === d.id) return 'url(#nodeGlow)';
        if (highlightedNodes.has(d.id)) return 'url(#nodeShadow)';
        return 'none';
      });
  }, [selectedNode, highlightedNodes, highlightedEdges, visualizationMode]);

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

    // Add SVG filters for glow effects
    const defs = svg.append('defs');
    
    // Node glow filter (selected)
    defs.append('filter')
      .attr('id', 'nodeGlow')
      .attr('x', '-60%')
      .attr('y', '-60%')
      .attr('width', '220%')
      .attr('height', '220%')
      .append('feGaussianBlur')
      .attr('stdDeviation', '6')
      .attr('result', 'coloredBlur');
    
    defs.select('#nodeGlow')
      .append('feMerge')
      .selectAll('feMergeNode')
      .data([{}, {}])
      .enter()
      .append('feMergeNode')
      .attr('in', (_, i) => i === 0 ? 'coloredBlur' : 'SourceGraphic');

    // Node shadow filter (highlighted)
    defs.append('filter')
      .attr('id', 'nodeShadow')
      .attr('x', '-50%')
      .attr('y', '-50%')
      .attr('width', '200%')
      .attr('height', '200%')
      .append('feGaussianBlur')
      .attr('stdDeviation', '3')
      .attr('result', 'coloredBlur');
    
    defs.select('#nodeShadow')
      .append('feMerge')
      .selectAll('feMergeNode')
      .data([{}, {}])
      .enter()
      .append('feMergeNode')
      .attr('in', (_, i) => i === 0 ? 'coloredBlur' : 'SourceGraphic');

    // Drop shadow filter for depth
    defs.append('filter')
      .attr('id', 'dropShadow')
      .attr('x', '-50%')
      .attr('y', '-50%')
      .attr('width', '200%')
      .attr('height', '200%')
      .append('feDropShadow')
      .attr('dx', '2')
      .attr('dy', '2')
      .attr('stdDeviation', '3')
      .attr('flood-opacity', '0.3');

    // Edge glow filter
    defs.append('filter')
      .attr('id', 'edgeGlow')
      .attr('x', '-20%')
      .attr('y', '-20%')
      .attr('width', '140%')
      .attr('height', '140%')
      .append('feGaussianBlur')
      .attr('stdDeviation', '2')
      .attr('result', 'coloredBlur');

    // Zoom
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 8])
      .on('zoom', (event) => g.attr('transform', event.transform));
    svg.call(zoom);

    // Double-click to reset zoom
    svg.on('dblclick.zoom', () => {
      svg.transition()
        .duration(750)
        .call(zoom.transform as any, d3.zoomIdentity.translate(width / 2, height / 2).scale(1));
    });

    // Scale node sizes based on PageRank (more important = bigger)
    const maxPageRank = Math.max(...activeNodes.map(n => n.pagerank), 1);
    const sizeScale = d3.scaleSqrt()
      .domain([0, maxPageRank])
      .range([4, 30]);

    const simulation = d3.forceSimulation(activeNodes as any)
      .force('link', d3.forceLink(activeEdges as any)
        .id((d: any) => d.id)
        .distance((d: any) => {
          const s = typeof d.source === 'object' ? d.source : activeNodes.find(n => n.id === d.source);
          const t = typeof d.target === 'object' ? d.target : activeNodes.find(n => n.id === d.target);
          const avgPageRank = ((s?.pagerank || 0) + (t?.pagerank || 0)) / 2;
          return 160 + avgPageRank * 80;
        })
        .strength(0.1))
      .force('charge', d3.forceManyBody()
        .strength((d: any) => -500 * Math.sqrt(d.pagerank + 0.1))
        .distanceMax(1000)
        .theta(0.9))
      .force('center', d3.forceCenter(width / 2, height / 2).strength(0.03))
      .force('collision', d3.forceCollide()
        .radius((d: any) => sizeScale(d.pagerank) + 24)
        .strength(0.9)
        .iterations(2))
      .force('x', d3.forceX(width / 2).strength(0.005))
      .force('y', d3.forceY(height / 2).strength(0.005))
      .alphaDecay(0.02)
      .alphaMin(0.002)
      .velocityDecay(0.4);

    // Draw edges with curved paths and better interactivity
    const link = g.append('g')
      .selectAll('line')
      .data(activeEdges)
      .join('line')
      .attr('stroke', '#cbd5e1')
      .attr('stroke-width', 1.5)
      .attr('stroke-opacity', 0.35)
      .attr('class', 'edge-line')
      .on('mouseenter', function(_, d) {
        // Highlight connected nodes and edges on edge hover
        const srcId = typeof d.source === 'object' ? d.source.id : d.source;
        const tgtId = typeof d.target === 'object' ? d.target.id : d.target;
        
        d3.select(this)
          .transition()
          .duration(200)
          .attr('stroke-width', 3.5)
          .attr('stroke-opacity', 0.9)
          .attr('stroke', '#1e293b')
          .attr('filter', 'url(#edgeGlow)');

        nodeRef.current.selectAll('circle')
          .transition()
          .duration(200)
          .attr('fill-opacity', (node: any) => 
            node.id === srcId || node.id === tgtId ? 1 : 0.25
          )
          .attr('stroke-width', (node: any) =>
            node.id === srcId || node.id === tgtId ? 3.5 : 2
          );
      })
      .on('mouseleave', function(_, d) {
        d3.select(this)
          .transition()
          .duration(200)
          .attr('stroke', '#cbd5e1')
          .attr('stroke-width', 1.5)
          .attr('stroke-opacity', 0.35)
          .attr('filter', 'none');

        nodeRef.current.selectAll('circle')
          .transition()
          .duration(200)
          .attr('fill-opacity', 0.95)
          .attr('stroke-width', 2);
      });
    
    linkRef.current = link;

    // Draw nodes with better styling
    const nodeGroup = g.append('g')
      .selectAll('g')
      .data(activeNodes)
      .join('g')
      .attr('cursor', 'pointer');

    // Add gradient coloring based on PageRank
    const colorScale = d3.scaleLinear<string>()
      .domain([0, maxPageRank / 2, maxPageRank])
      .range(['#93c5fd', '#3b82f6', '#1e40af']);

    const node = nodeGroup.append('circle')
      .attr('r', (d) => sizeScale(d.pagerank))
      .attr('fill', (d) => getNodeColor(d.community))
      .attr('fill-opacity', 0.95)
      .attr('stroke', '#ffffff')
      .attr('stroke-width', 2)
      .attr('class', 'node-circle')
      .attr('cursor', 'grab')
      .attr('filter', 'url(#dropShadow)')
      .attr('pointer-events', 'none')
      .on('mouseenter', function(_, d) {
        d3.select(this)
          .transition()
          .duration(150)
          .attr('fill-opacity', 1)
          .attr('stroke-width', 4)
          .attr('r', (node) => sizeScale(node.pagerank) * 1.4)
          .attr('filter', 'url(#nodeGlow)');

        // Pulse effect animation
        d3.select(this)
          .transition()
          .duration(600)
          .attr('r', (node) => sizeScale(node.pagerank) * 1.35)
          .on('end', function() {
            d3.select(this)
              .transition()
              .duration(600)
              .attr('r', (node) => sizeScale(node.pagerank) * 1.4);
          });

        // Show connections
        const connectedIds = new Set<string>();
        activeEdges.forEach(e => {
          const src = typeof e.source === 'object' ? (e.source as any).id : e.source;
          const tgt = typeof e.target === 'object' ? (e.target as any).id : e.target;
          if (src === d.id || tgt === d.id) {
            connectedIds.add(src === d.id ? tgt : src);
          }
        });

        // Highlight connected edges
        linkRef.current
          .transition()
          .duration(150)
          .attr('stroke-width', (edge: any) => {
            const src = typeof edge.source === 'object' ? edge.source.id : edge.source;
            const tgt = typeof edge.target === 'object' ? edge.target.id : edge.target;
            return src === d.id || tgt === d.id ? 3 : 1.5;
          })
          .attr('stroke-opacity', (edge: any) => {
            const src = typeof edge.source === 'object' ? edge.source.id : edge.source;
            const tgt = typeof edge.target === 'object' ? edge.target.id : edge.target;
            return src === d.id || tgt === d.id ? 0.8 : 0.1;
          });

        nodeRef.current.selectAll('circle')
          .transition()
          .duration(150)
          .attr('fill-opacity', (node: any) =>
            node.id === d.id ? 1 : (connectedIds.has(node.id) ? 0.8 : 0.2)
          );

        // Show tooltip
        tooltip.style('display', 'block')
          .html(`
            <div class="font-bold text-white text-sm mb-2">${shortenAddress(d.id)}</div>
            <div class="text-xs text-gray-200 space-y-1">
              <div className="border-b border-gray-600 pb-1 mb-1">
                <div><span class="text-gray-400">Degree:</span> <span class="text-blue-300 font-bold">${d.degree}</span></div>
                <div><span class="text-gray-400">PageRank:</span> <span class="text-purple-300 font-bold">${d.pagerank.toFixed(6)}</span></div>
              </div>
              <div>
                <div><span class="text-gray-400">Community:</span> <span class="font-bold">${d.community}</span></div>
                <div><span class="text-gray-400">In-degree:</span> <span class="font-bold">${d.in_degree}</span></div>
                <div><span class="text-gray-400">Out-degree:</span> <span class="font-bold">${d.out_degree}</span></div>
              </div>
            </div>
          `);
      })
      .on('mousemove', (event) => {
        const offsetX = event.pageX - (containerRef.current?.getBoundingClientRect().left || 0);
        const offsetY = event.pageY - (containerRef.current?.getBoundingClientRect().top || 0);
        tooltip
          .style('left', (offsetX + 15) + 'px')
          .style('top', (offsetY - 10) + 'px');
      })
      .on('mouseleave', function(_, d) {
        d3.select(this)
          .transition()
          .duration(150)
          .attr('fill-opacity', 0.95)
          .attr('stroke-width', selectedNode?.id === d.id ? 4 : 2)
          .attr('r', (node) => sizeScale(node.pagerank))
          .attr('filter', selectedNode?.id === d.id ? 'url(#nodeGlow)' : 'url(#dropShadow)');

        linkRef.current
          .transition()
          .duration(150)
          .attr('stroke-width', 1.5)
          .attr('stroke-opacity', 0.35);

        nodeRef.current.selectAll('circle')
          .transition()
          .duration(150)
          .attr('fill-opacity', 0.95);

        tooltip.style('display', 'none');
      });

    // Add invisible larger circles for hit detection - attach all handlers here
    nodeGroup.append('circle')
      .attr('r', (d) => Math.max(sizeScale(d.pagerank) * 2.5, 25))
      .attr('fill', 'transparent')
      .attr('pointer-events', 'all')
      .attr('cursor', 'grab')
      .on('click', function(event, d) {
        event.stopPropagation();
        if (event.defaultPrevented) return; // Drag occurred
        console.log('Node clicked:', d.id);
        const newSelectedNode = selectedNode?.id === d.id ? null : d;
        onNodeSelect(newSelectedNode);
        
        // Freeze/unfreeze node position based on selection
        if (newSelectedNode) {
          d.fx = d.x;
          d.fy = d.y;
          simulation.alphaTarget(0.1).restart();
        } else {
          d.fx = null;
          d.fy = null;
          if (!simulation.alpha()) simulation.alpha(0.3).restart();
        }

        // Force immediate visual update
        if (nodeRef.current) {
          console.log('Forcing visual update for node:', d.id);
          nodeRef.current.selectAll('g').select('circle:not([fill="transparent"])')
            .transition()
            .duration(150)
            .attr('stroke-width', (node: any) => newSelectedNode?.id === node.id ? 4 : 2)
            .attr('stroke', (node: any) => newSelectedNode?.id === node.id ? '#00ff88' : '#ffffff')
            .attr('filter', (node: any) => newSelectedNode?.id === node.id ? 'url(#nodeGlow)' : 'none');
        }

        if (linkRef.current) {
          linkRef.current
            .transition()
            .duration(150)
            .attr('stroke-width', (edge: any) => {
              const srcId = typeof edge.source === 'object' ? edge.source.id : edge.source;
              const tgtId = typeof edge.target === 'object' ? edge.target.id : edge.target;
              return newSelectedNode && (srcId === newSelectedNode.id || tgtId === newSelectedNode.id) ? 3 : 1.5;
            })
            .attr('stroke', (edge: any) => {
              const srcId = typeof edge.source === 'object' ? edge.source.id : edge.source;
              const tgtId = typeof edge.target === 'object' ? edge.target.id : edge.target;
              return newSelectedNode && (srcId === newSelectedNode.id || tgtId === newSelectedNode.id) ? '#1f2937' : '#d1d5db';
            })
            .attr('stroke-opacity', (edge: any) => {
              const srcId = typeof edge.source === 'object' ? edge.source.id : edge.source;
              const tgtId = typeof edge.target === 'object' ? edge.target.id : edge.target;
              return newSelectedNode && (srcId === newSelectedNode.id || tgtId === newSelectedNode.id) ? 0.95 : 0.35;
            });
        }
      })
      .call(d3.drag<any, any>()
        .on('start', (event, d) => {
          draggingNodeRef.current = d.id;
          if (!event.active) {
            simulation.alphaTarget(0.3).restart();
          }
          d.fx = d.x; 
          d.fy = d.y;
          d3.select(event.sourceEvent.target).style('cursor', 'grabbing');
        })
        .on('drag', (event, d) => { 
          d.fx = event.x; 
          d.fy = event.y;
          // Update visible circle feedback
          const parentG = d3.select(event.sourceEvent.target.parentNode);
          const visibleCircle = parentG.select('circle:not([fill="transparent"])');
          visibleCircle
            .attr('fill-opacity', 1)
            .attr('stroke-width', 4);
        })
        .on('end', (event, d) => {
          // Don't clear immediately, let click handler use the position
          if (!event.active) {
            simulation.alphaTarget(0);
          }
          d.fx = null; 
          d.fy = null;
          d3.select(event.sourceEvent.target).style('cursor', 'grab');
          const parentG = d3.select(event.sourceEvent.target.parentNode);
          const visibleCircle = parentG.select('circle:not([fill="transparent"])');
          visibleCircle
            .attr('fill-opacity', 0.95)
            .attr('stroke-width', 2);
        })
      );

    nodeRef.current = nodeGroup;

    // Tooltip with better styling
    const tooltip = d3.select(containerRef.current)
      .append('div')
      .attr('class', 'absolute pointer-events-none bg-gray-900 text-white rounded-lg px-3 py-2 text-xs font-mono z-50 border border-gray-700 shadow-2xl')
      .style('display', 'none');

    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);
      nodeGroup.attr('transform', (d: any) => `translate(${d.x},${d.y})`);
    });

    return () => {
      simulation.stop();
      tooltip.remove();
    };
  }, [nodes, edges, dimensions, removedNodes, onNodeSelect, selectedNode]);

  return (
    <div ref={containerRef} className="relative w-full h-full grid-bg">
      <svg ref={svgRef} width={dimensions.width} height={dimensions.height} className="w-full h-full" />
    </div>
  );
}
