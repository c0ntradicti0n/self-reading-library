import React, { useEffect, useState } from 'react'

import dynamic from 'next/dynamic'

// Having enourmous problems with these imports: one dynamic as recommended in the internet
const ForceGraph2D = dynamic(() => import('./ForceGraph2d.js'), {
   loading: () => <p>...</p>,
   ssr: false,
})

import SpriteText from 'three-spritetext'

// two for the text items... don't think, one of them is superflouus
// THIS IS THE TRICK: ONE IMPORT FOR SSR, ONE FOR THE 3D GRAPH ON CLIENT-SIDE

export default function SceletonGraph({
   data = d,
   height = window.innerHeight * 0.9,
   width = window.innerWidth * 0.95,
}) {
   const svgRef = React.useRef(null)
   const [trick, setTrick] = useState(false)
   console.log(data)

   useEffect(() => {
      data.links = data.edges
      const unknow_nodes_s = data.edges
         .filter((e) => !data.nodes.find((n) => n.id == e.source))
         .map((e) => [{ id: e.source, label: e.label }])
         .flat()
      const unknow_nodes_t = data.edges
         .filter((e) => !data.nodes.find((n) => n.id == e.target))
         .map((e) => [{ id: e.target, label: e.label }])
         .flat()

      console.log('unknown nodes', unknow_nodes_t, unknow_nodes_s)
      data.nodes = [...data.nodes, ...unknow_nodes_s, ...unknow_nodes_t]
      data.nodes = data.nodes.map((n) => ({ ...n, x: 0, y: 0 })).reverse()
      setTrick(!trick)
   }, [data])

   return (
      <div style={{ width: '94%', height: '94%', overflow: 'hidden' , strokeWidth: "5"}}>
         {data.links && (
            <ForceGraph2D
               graphData={data}
               onNodeDragEnd={(node) => {
                  node.fx = node.x
                  node.fy = node.y
               }}
               nodeCanvasObject={(node, ctx, globalScale) => {
                  const label = node.label
                  const fontSize = 16 / globalScale
                  ctx.font = `${fontSize}px Computer Modern`
                  const textWidth = ctx.measureText(label).width
                  const bckgDimensions = [textWidth, fontSize].map(
                     (n) => n + fontSize * 0.2,
                  ) // some padding

                  ctx.fillStyle = 'rgba(255, 255, 255, 0.8)'
                  ctx.fillRect(
                     node.x - bckgDimensions[0] / 2,
                     node.y - bckgDimensions[1] / 2,
                     ...bckgDimensions,
                  )

                  ctx.textAlign = 'center'
                  ctx.textBaseline = 'middle'
                  ctx.fillStyle = node.color ?? 'black'
                  ctx.fillText(label, node.x, node.y)

                  node.__bckgDimensions = bckgDimensions // to re-use in nodePointerAreaPaint
               }}
               linkLabel = {(n) => n.label}
               linkWidth={5}
               linkColor={(n) =>  {
                  switch (n.label) {
                                          case "opposite": return "red"
                                                               case "...": return "blue"


                     case "equal": return "greenyellow"
                     default:
return "black"
                  }
                  }}
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
