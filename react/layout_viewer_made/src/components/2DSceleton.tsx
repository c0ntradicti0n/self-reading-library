import React, { useEffect, useState } from 'react'
import * as d3 from 'd3'
import { equal } from 'lodash'
import dynamic from 'next/dynamic'

// Having enourmous problems with these imports: one dynamic as recommended in the internet

function getLines(ctx, text, maxWidth) {
   var words = text.split(' ')
   var lines = []
   var currentLine = words[0]

   for (var i = 1; i < words.length; i++) {
      var word = words[i]
      var width = ctx.measureText(currentLine + ' ' + word).width
      if (width < maxWidth) {
         currentLine += ' ' + word
      } else {
         lines.push(currentLine)
         currentLine = word
      }
   }
   lines.push(currentLine)
   return lines
}

import SpriteText from 'three-spritetext'
import { ForceGraph2D } from 'react-force-graph'
import { getUniqueBy } from '../helpers/array'

// two for the text items... don't think, one of them is superflouus
// THIS IS THE TRICK: ONE IMPORT FOR SSR, ONE FOR THE 3D GRAPH ON CLIENT-SIDE

export default function SceletonGraph({
   graphData,
   height = window.innerHeight * 0.9,
   width = window.innerWidth * 0.95,
   onExpand,
}) {
   const [data, setData] = useState(graphData)

   const [ForceGraph2D, setFG] = useState(
      require('react-force-graph').ForceGraph2D,
   )
   const fgRef = React.useRef(null)
   const [trick, setTrick] = useState(false)

   useEffect(() => {
      setData(graphData)
   }, [graphData])

   function preprocessData(data) {
      data.links = data.edges
      const unknow_nodes_s = data.edges
         .filter((e) => !data.nodes.find((n) => n.id == e.source))
         .map((e) => [{ id: e.source, label: e.label }])
         .flat()
      const unknow_nodes_t = data.edges
         .filter((e) => !data.nodes.find((n) => n.id == e.target))
         .map((e) => [{ id: e.target, label: e.label }])
         .flat()

      data.nodes = [...data.nodes, ...unknow_nodes_s, ...unknow_nodes_t]
      data.nodes = data.nodes
         .map((n) => ({ ...n, x: 0, y: 0, value: 100 }))
         .reverse()
   }

   useEffect(() => {
      preprocessData(data)
      setTrick(!trick)
   }, [data])

   useEffect(() => {
      if (fgRef && fgRef.current) {
         fgRef.current.d3Force('charge', d3.forceManyBody().strength(-10))
         fgRef.current.d3Force('link', d3.forceManyBody().strength(-100))
         fgRef.current.d3Force('center', d3.forceManyBody().strength(-20))
      }
   }, [fgRef])

   return (
      <div
         style={{
            width: '94%',
            height: '94%',
            overflow: 'hidden',
            strokeWidth: '5',
         }}
      >
         {data.links && (
            <ForceGraph2D
               forceEngine={'ngraph'}
               d3AlphaDecay={0.005}
               graphData={data}
               onNodeDragEnd={(node) => {
                  node.fx = node.x
                  node.fy = node.y
               }}
               autoPauseRedraw={false}
               onNodeRightClick={(node) => {
                  onExpand(node)
                  ;(async () => {
                     console.log(node)
                     console.log(data)
                     const more = await onExpand(node)
                     preprocessData(more)

                     console.log('more', more)
                     /*if (
                        getUniqueBy(data.nodes, 'id').size ==
                        getUniqueBy([...data.nodes, ...more.nodes], 'id').size
                         &&
                     )
                        return
*/
                     const newData = {
                        nodes: getUniqueBy(
                           [...data.nodes, ...more.nodes],
                           'id',
                        ),
                        edges: getUniqueBy(
                           [...data.edges, ...more.edges],
                           'id',
                        ),
                     }

                     setData(newData)
                  })()
               }}
               nodeCanvasObject={(node, ctx, globalScale) => {
                  const label = node.label
                  const fontSize =
                     2 * Math.sqrt(Math.sqrt(Math.sqrt(globalScale)))
                  ctx.font = `${fontSize}px Computer Modern`
                  const textWidth = ctx.measureText(label).width
                  const bckgDimensions = [textWidth, fontSize].map(
                     (n) => n + fontSize * 0.2,
                  ) // some padding

                  ctx.fillStyle = 'rgba(150,150,150, 0.4)'
                  ctx.beginPath()
                  ctx.arc(node.x, node.y, 10, 0, 2 * Math.PI, false)
                  ctx.fill()

                  ctx.textAlign = 'center'
                  ctx.textBaseline = 'middle'
                  ctx.fillStyle = node.color ?? 'black'
                  const lines = getLines(ctx, label, 100)
                  const lineheight = fontSize
                  for (var i = 0; i < lines.length; i++)
                     ctx.fillText(
                        lines[i],
                        node.x,
                        node.y + (-lines.length / 2 + i) * lineheight,
                     )
                  node.__bckgDimensions = bckgDimensions // to re-use in nodePointerAreaPaint
               }}
               linkLabel={(n) => n.label}
               linkWidth={2}
               linkColor={(n) => {
                  switch (n.label) {
                     case 'http://polarity.science/SUBJECT':
                        return 'red'
                     case 'http://polarity.science/CONTRAST':
                        return 'blue'

                     case 'http://polarity.science/equal':
                        return 'greenyellow'
                     case 'http://polarity.science/forward_difference':
                        return 'orange'
                     default:
                        return 'black'
                  }
               }}
               nodeRelSize={600}
               enableNavigationControls={true}
               showNavInfo={true}
               nodePointerAreaPaint={(node, color, ctx) => {
                  ctx.fillStyle = color
                  const bckgDimensions = node.__bckgDimensions
                  bckgDimensions &&
                     ctx.fillRect(
                        node.x - bckgDimensions[0] / 2,
                        node.y - bckgDimensions[1] / 2,
                        ...bckgDimensions,
                     )
               }}
            />
         )}
      </div>
   )
}
