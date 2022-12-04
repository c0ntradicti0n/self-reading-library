import React, { useEffect } from 'react'
import * as d3 from 'd3'
import {
   invalidation,
   forceSimulation,
   forceLink,
   forceManyBody,
} from 'd3-force'

import forceBoundary from 'd3-force-boundary'

function wrap(text, width) {
   text.each(function () {
      var text = d3.select(this),
         words = text.text().split(/\s+/).reverse(),
         word,
         line = [],
         lineNumber = 0,
         lineHeight = 1.1, // ems
         x = text.attr('x'),
         y = text.attr('y'),
         dy = 0, //parseFloat(text.attr("dy")),
         tspan = text
            .text(null)
            .append('tspan')
            .attr('x', x)
            .attr('y', y)
            .attr('dy', dy + 'em')
      while ((word = words.pop())) {
         line.push(word)
         tspan.text(line.join(' '))
         if (tspan.node().getComputedTextLength() > width) {
            line.pop()
            tspan.text(line.join(' '))
            line = [word]
            tspan = text
               .append('tspan')
               .attr('x', x)
               .attr('y', y)
               .attr('dy', ++lineNumber * lineHeight + dy + 'em')
               .text(word)
         }
      }
   })
}

// https://observablehq.com/@d3/force-directed-graph
//https://stackoverflow.com/questions/13364566/labels-text-on-the-nodes-of-a-d3-force-directed-graph
// http://bl.ocks.org/eyaler/10586116
function ForceGraph(
   ref,
   {
      nodes, // an iterable of node objects (typically [{id}, …])
      links, // an iterable of link objects (typically [{source, target}, …])
   },
   {
      nodeId = (d) => d.id, // given d in nodes, returns a unique identifier (string)
      nodeGroup, // given d in nodes, returns an (ordinal) value for color
      nodeGroups, // an array of ordinal values representing the node groups
      nodeTitle, // given d in nodes, a title string
      nodeFill = 'currentColor', // node stroke fill (if not using a group color encoding)
      nodeStroke = '#fff', // node stroke color
      nodeStrokeWidth = 1.5, // node stroke width, in pixels
      nodeStrokeOpacity = 1, // node stroke opacity
      nodeRadius = 25, // node radius, in pixels
      nodeStrength,
      linkSource = ({ source }) => source, // given d in links, returns a node identifier string
      linkTarget = ({ target }) => target, // given d in links, returns a node identifier string
      linkStroke = '#999', // link stroke color
      linkStrokeOpacity = 0.6, // link stroke opacity
      linkStrokeWidth = 1.5, // given d in links, returns a stroke width in pixels
      linkStrokeLinecap = 'round', // link stroke linecap
      linkStrength,
      colors = d3.schemeTableau10, // an array of color strings, for the node groups
      width = 640, // outer width, in pixels
      height = 400, // outer height, in pixels
      invalidation, // when this promise resolves, stop the simulation
   } = {},
) {
   d3.selectAll('svg > *').remove()

   // Compute values.
   const N = d3.map(nodes, nodeId).map(intern)
   const LS = d3.map(links, linkSource).map(intern)
   const LT = d3.map(links, linkTarget).map(intern)
   if (nodeTitle === undefined) nodeTitle = (_, i) => N[i]
   const T = nodeTitle == null ? null : d3.map(nodes, nodeTitle)
   const G = nodeGroup == null ? null : d3.map(nodes, nodeGroup).map(intern)
   const W =
      typeof linkStrokeWidth !== 'function'
         ? null
         : d3.map(links, linkStrokeWidth)
   const L = typeof linkStroke !== 'function' ? null : d3.map(links, linkStroke)

   // Replace the input nodes and links with mutable objects for the simulation.
   nodes = d3.map(nodes, (_, i) => ({ id: N[i] }))
   links = d3.map(links, (_, i) => ({ source: LS[i], target: LT[i] }))

   // Compute default domains.
   if (G && nodeGroups === undefined) nodeGroups = d3.sort(G)

   // Construct the scales.
   const color = nodeGroup == null ? null : d3.scaleOrdinal(nodeGroups, colors)

   // Construct the forces.
   const forceNode = d3.forceManyBody()
   const forceLink = d3.forceLink(links).id(({ index: i }) => N[i])
   if (nodeStrength !== undefined) forceNode.strength(nodeStrength)
   if (linkStrength !== undefined) forceLink.strength(linkStrength)

   const simulation = d3
      .forceSimulation(nodes)
      .force('link', forceLink)
      .force('charge', forceNode)
      .force('box', forceBoundary(0, -height / 2, width, height / 2))
      .on('tick', ticked)

   const svg = d3
      .select(ref.current)
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', [-0.1 * width, -height / 2, width, height])
      .attr('style', 'max-width: 100%; height: auto; height: intrinsic;')

   const link = svg
      .append('g')
      .attr('stroke', typeof linkStroke !== 'function' ? linkStroke : null)
      .attr('stroke-opacity', linkStrokeOpacity)
      .attr(
         'stroke-width',
         typeof linkStrokeWidth !== 'function' ? linkStrokeWidth : null,
      )
      .attr('stroke-linecap', linkStrokeLinecap)
      .selectAll('line')
      .data(links)
      .join('line')

   const node = svg
      .append('g')
      .attr('fill', nodeFill)
      .attr('stroke', nodeStroke)
      .attr('stroke-opacity', nodeStrokeOpacity)
      .attr('stroke-width', nodeStrokeWidth)
      .selectAll('circle')
      .data(nodes)
      .join('circle')
      .attr('r', nodeRadius)
      .call(drag(simulation))

   var texts = svg
      .selectAll('text.label')
      .data(nodes)
      .enter()
      .append('text')
      .attr('class', 'label')
      .attr('fill', 'black')
      .text(function (d) {
         return T[d.index]
      })

   if (W) link.attr('stroke-width', ({ index: i }) => W[i])
   if (L) link.attr('stroke', ({ index: i }) => L[i])
   if (G) node.attr('fill', ({ index: i }) => color(G[i]))

   if (invalidation != null) invalidation.then(() => simulation.stop())

   function intern(value) {
      return value !== null && typeof value === 'object'
         ? value.valueOf()
         : value
   }

   function ticked() {
      link
         .attr('x1', (d) => d.source.x)
         .attr('y1', (d) => d.source.y)
         .attr('x2', (d) => d.target.x)
         .attr('y2', (d) => d.target.y)

      node.attr('cx', (d) => d.x).attr('cy', (d) => d.y)

      texts.attr('transform', function (d) {
         return 'translate(' + d.x + ',' + d.y + ')'
      })
   }

   function drag(simulation) {
      function dragStart(event) {
         if (!event.active) simulation.alphaTarget(0.3).restart()
         event.subject.fx = event.subject.x
         event.subject.fy = event.subject.y
      }

      function dragged(event) {
         event.subject.fx = event.x
         event.subject.fy = event.y
      }

      function dragEnd(event) {
         if (!event.active) simulation.alphaTarget(0)
         event.subject.fx = null
         event.subject.fy = null
      }

      return d3
         .drag()
         .on('start', dragStart)
         .on('drag', dragged)
         .on('end', dragEnd)
   }

   simulation.on('tick', () => {
      link
         .attr('x1', (d) => d.source.x)
         .attr('y1', (d) => d.source.y)
         .attr('x2', (d) => d.target.x)
         .attr('y2', (d) => d.target.y)

      node.attr('cx', (d) => d.x).attr('cy', (d) => d.y)

      texts.attr('transform', function (d) {
         return 'translate(' + d.x + ',' + d.y + ')'
      })
   })

   //ZOOM
   const zoomRect = svg
      .append('rect')
      .attr('width', width)
      .attr('height', height)
      .style('fill', 'none')
      .style('pointer-events', 'all')

   //ZOOM
   const zoom = d3
      .zoom()
      .scaleExtent([1 / 2, 64])
      .on('zoom', zoomed)

   //ZOOM
   //zoomRect.call(zoom).call(zoom.translateTo, 0, 0)

   //ZOOM
   function zoomed(e) {
      node.attr('transform', e.transform)
      link.attr('transform', e.transform)
      texts.attr('transform', e.transform)
   }

   return Object.assign(svg.node(), { scales: { color } })
}

export default function SceletonGraph({
   data = d,
   height = window.innerHeight * 0.9,
   width = window.innerWidth * 0.95,
}) {
   const svgRef = React.useRef(null)
   console.log(data)
   useEffect(() => {
      data.links = data.edges
      data.nodes = data.nodes.map((n) => ({ ...n, x: 0, y: 0 })).reverse()

      ForceGraph(svgRef, data, {
         nodeId: (d) => d.id,
         nodeGroup: (d) => d.group,
         nodeTitle: (d) => `${d.label}`,
         linkStrokeWidth: (l) => Math.sqrt(l.value),
         nodeStrength: -900,
         linkStrength: 0.2,
         width,
         height,
         invalidation, // a promise to stop the simulation when the cell is re-run
      })
   }, [data])
   return (
      <div style={{ width: '94%', height: '94%', overflow: 'hidden' }}>
         <svg
            ref={svgRef}
            width={window.innerWidth}
            height={window.innerHeight}
         />
      </div>
   )
}
