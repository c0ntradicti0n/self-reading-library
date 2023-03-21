import { Fragment, useEffect, useRef, useState } from 'react'
import cytoscape from 'cytoscape'
import coseBilkent from 'cytoscape-cose-bilkent'

cytoscape.use(coseBilkent)
const CytoscapeGraph = ({ graphData, onExpand }) => {
   const [data, setData] = useState(graphData)
   const [cdata, setCData] = useState(null)

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

      console.log(data.nodes)
      const cydata = [
         ...data.nodes.map((n) => ({ group: 'nodes', data: { ...n }})),
         ...data.edges.map((e) => ({
            group: 'edges',
            data: { id: e.id + 'xxx', source: e.source, target: e.target },
         })),
      ]
      console.log({ data, cydata })
      setCData(cydata)
      data.nodes = [...data.nodes, ...unknow_nodes_s, ...unknow_nodes_t]
      data.nodes = data.nodes
         .map((n) => ({ ...n, x: 0, y: 0, value: 100 }))
         .reverse()
   }

   useEffect(() => {
      preprocessData(data)
   }, [data])
   const graphRef = useRef(null)

   console.log('hallo', cdata)

   const drawGraph = () => {
      if (!cdata) return

      console.log([cdata[0], cdata[1], cdata[58]])
      const cy = cytoscape({
         container: graphRef.current,
         ready: function () {
            this.nodes().forEach(function (node) {
               let width = [30, 70, 110]
               let size = width[Math.floor(Math.random() * 3)]
               node.css('width', size)
               node.css('height', size)
            })
            this.layout({ name: 'cose-bilkent', animationDuration: 1000 }).run()
         },

         style: [
            {
               selector: 'node',
               style: {
                  'text-wrap': 'wrap',
                  'text-max-width': '100px',
                  label: 'data(label)',
                  'text-valign': 'center',
                  'text-halign': 'center',
                  'background-color': '#abcdef',
               },
            },

            {
               selector: ':parent',
               style: {
                  'background-opacity': 0.1,
               },
            },

            {
               selector: 'edge',
               style: {
                  width: 3,
                  'line-color': '#030810',
               },
            },
         ],

         elements: cdata,
      })
   }

   useEffect(() => {
      drawGraph()
   }, [cdata])
   if (!cdata) return null

   return (
      <Fragment>
         <h2>Graph Test</h2>
         <div ref={graphRef} style={{ width: '100%', height: '80vh' }}></div>
         {JSON.stringify(cdata, null, null)}
      </Fragment>
   )
}

export default CytoscapeGraph
