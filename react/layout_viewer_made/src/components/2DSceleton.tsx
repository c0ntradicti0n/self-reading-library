import React, { useEffect, useState } from 'react'
import * as d3 from 'd3'
import {
   invalidation,
   forceSimulation,
   forceLink,
   forceManyBody,
} from 'd3-force'
import { DocumentContext } from '../contexts/DocumentContext.tsx'

const drag = (simulation) => {
   function dragstarted(event, d) {
      if (!event.active) simulation.alphato(0.3).restart()
      d.fx = d.x
      d.fy = d.y
   }

   function dragged(event, d) {
      d.fx = event.x
      d.fy = event.y
   }

   function dragended(event, d) {
      if (!event.active) simulation.alphato(0)
      d.fx = null
      d.fy = null
   }

   return d3
      .drag()
      .on('start', dragstarted)
      .on('drag', dragged)
      .on('end', dragended)
}
function linkArc(d) {
   const r = Math.hypot(d.to.x - d.from.x, d.to.y - d.from.y)
   return `
    M${d.from.x},${d.from.y}
    A${r},${r} 0 0,1 ${d.to.x},${d.to.y}
  `
}
const chart = (ref, { data, height, width, color }) => {
   console.log("Chart", { data, height, width, color })
   const links = data.edges.map((d) => Object.create(d))
   const nodes = data.nodes.map((d) => Object.create(d))

   const idsEdges = links.map(l => [l.from, l.to]).flat()
   const idsNodes = nodes.map(n => n.id)
   const notIn = idsEdges.filter(i => ! idsNodes.includes(i))

   console.log(notIn, idsNodes, idsEdges)
   
   const simulation = d3
      .forceSimulation(nodes)
      .force(
         'link',
         d3.forceLink(links).id((d) => d.id),
      )
      .force('charge', d3.forceManyBody().strength(-400))
      .force('x', d3.forceX())
      .force('y', d3.forceY())

   const svg = d3
      .select(ref.current)
      .attr('viewBox', [-width / 2, -height / 2, width, height])

   // Per-type markers, as they don't inherit styles.
   svg.append('defs')
      .selectAll('marker')
      .join('marker')
      .attr('id', (d) => `arrow-${d}`)
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 15)
      .attr('refY', -0.5)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('fill', color)
      .attr('d', 'M0,-5L10,0L0,5')

   const link = svg
      .append('g')
      .attr('fill', 'none')
      .attr('stroke-width', 1.5)
      .selectAll('path')
      .data(links)
      .join('path')
      .attr('stroke', (d) => color(d.type))
      .attr('marker-end', (d) => d.type)

   const node = svg
      .append('g')
      .attr('fill', 'currentColor')
      .attr('stroke-linecap', 'round')
      .attr('stroke-linejoin', 'round')
      .selectAll('g')
      .data(nodes)
      .join('g')
      .call(drag(simulation))

   node
      .append('circle')
      .attr('stroke', 'white')
      .attr('stroke-width', 1.5)
      .attr('r', 4)

   node
      .append('text')
      .attr('x', 8)
      .attr('y', '0.31em')
      .text((d) => d.id)
      .clone(true)
      .lower()
      .attr('fill', 'none')
      .attr('stroke', 'white')
      .attr('stroke-width', 3)

   simulation.on('tick', () => {
      link.attr('d', linkArc)
      node.attr('transform', (d) => `translate(${d.x},${d.y})`)
   })

   //invalidation.then(() => simulation.stop())

   return svg.node()
}

const d = {
   nodes: [
      { id: 'Microsoft' },
      { id: 'Amazon' },
      { id: 'HTC' },
      { id: 'Samsung' },
      { id: 'Apple' },
      { id: 'Motorola' },
      { id: 'Nokia' },
      { id: 'Kodak' },
      { id: 'Barnes & Noble' },
      { id: 'Foxconn' },
      { id: 'Oracle' },
      { id: 'Google' },
      { id: 'Inventec' },
      { id: 'LG' },
      { id: 'RIM' },
      { id: 'Sony' },
      { id: 'Qualcomm' },
      { id: 'Huawei' },
      { id: 'ZTE' },
      { id: 'Ericsson' },
   ],
   edges: [
      { source: 'Microsoft', target: 'Amazon', type: 'licensing' },
      { source: 'Microsoft', target: 'HTC', type: 'licensing' },
      { source: 'Samsung', target: 'Apple', type: 'suit' },
      { source: 'Motargetrola', target: 'Apple', type: 'suit' },
      { source: 'Nokia', target: 'Apple', type: 'resolved' },
      { source: 'HTC', target: 'Apple', type: 'suit' },
      { source: 'Kodak', target: 'Apple', type: 'suit' },
      { source: 'Microsoft', target: 'Barnes & Noble', type: 'suit' },
      { source: 'Microsoft', target: 'Foxconn', type: 'suit' },
      { source: 'Oracle', target: 'Google', type: 'suit' },
      { source: 'Apple', target: 'HTC', type: 'suit' },
      { source: 'Microsoft', target: 'Inventec', type: 'suit' },
      { source: 'Samsung', target: 'Kodak', type: 'resolved' },
      { source: 'LG', target: 'Kodak', type: 'resolved' },
      { source: 'RIM', target: 'Kodak', type: 'suit' },
      { source: 'Sony', target: 'LG', type: 'suit' },
      { source: 'Kodak', target: 'LG', type: 'resolved' },
      { source: 'Apple', target: 'Nokia', type: 'resolved' },
      { source: 'Qualcomm', target: 'Nokia', type: 'resolved' },
      { source: 'Apple', target: 'Motargetrola', type: 'suit' },
      { source: 'Microsoft', target: 'Motargetrola', type: 'suit' },
      { source: 'Motargetrola', target: 'Microsoft', type: 'suit' },
      { source: 'Huawei', target: 'ZTE', type: 'suit' },
      { source: 'Ericsson', target: 'ZTE', type: 'suit' },
      { source: 'Kodak', target: 'Samsung', type: 'resolved' },
      { source: 'Apple', target: 'Samsung', type: 'suit' },
      { source: 'Kodak', target: 'RIM', type: 'suit' },
      { source: 'Nokia', target: 'Qualcomm', type: 'suit' },
   ],
}

export default function SceletonGraph({
   data = d,
   height = 1000,
   width = 1000,
}) {
   const svgRef = React.useRef(null)
   console.log(data)
   useEffect(() => {
      chart(svgRef, {
         data,
         color: (d) => '#678',
         width: 500,
         height: 100,
      })
   }, [])
   return (
      <div style={{ width: '100%', height: '94%', overflow: 'hidden' }}>
         <svg ref={svgRef} width={width} height={height} />;
      </div>
   )
}
