import React, { useEffect, useState } from 'react'
import * as d3 from 'd3'
import { useRouter } from 'next/router'
function wrap(text, width) {
   const _dy = -1
   text.each(function () {
      let text = d3.select(this),
         words = text.text().split(/\s+/).reverse(),
         word,
         line = [],
         lineNumber = 0,
         lineHeight = 2.0, // ems
         y = text.attr('y'),
         r = text._groups[0][0].__data__.r
      let tspan = text
         .text(null)
         .append('tspan')
         .attr('x', 0)
         .attr('y', -Math.log10(r / 20) * 130)
         .attr('dy', _dy + 'em')
      console.log('text', y, r, text.r, r, text._groups[0][0].__data__)

      while ((word = words.pop())) {
         const str_line = line.join(' ')
         lineNumber += 1
         line.push(word)
         tspan.text(line.join(' '))
         if (str_line.length > width) {
            line.pop()
            tspan.text(line.join(' '))
            line = [word]
            tspan = text
               .append('tspan')
               .attr('x', 0)
               .attr('y', r * 140)
               .attr('dy', _dy + lineHeight + 'em')
               .text(r.toString() + word + 'hal')
         }
      }
   })
}

const pack = (data, width, height) =>
   d3.pack().size([width, height]).padding(3)(
      d3
         .hierarchy(data)
         .sum((d) => d.value)

         .sort((a, b) => b.value - a.value),
   )

const color = d3
   .scaleLinear()
   .domain([0, 5])
   .range(['hsl(152,80%,80%)', 'hsl(228,30%,40%)'])
   .interpolate(d3.interpolateHcl)

const rec_hierarchy = (name, data, value = 100, visited = []) => {
   if (visited.includes(name))
      return [
         {
            name: '--->>',
            id: 'recursive',
            value,
            children: [],
         },
      ]
   visited.push(name)

   const edges = data.links
      .filter((l) => l.source === name)
      .map((n) => {
         let res = rec_hierarchy(n.target, data, value * 4, visited)
         if (res.length === 1) {
            res = res?.[0]
            return res
         }
         return { name: n.target, children: res }
      })

   let node = data.nodes.find((n) => n.id === name)
   node = { ...node, value, children: [] }

   return !node.title
      ? edges
      : [
           {
              name: node.title,
              id: node.id,
              value,
              children: [],
           },
        ]
}
const chart = (data, ref, width, height, router) => {
   let root = pack(data, width, height)
   let focus = root
   let view
   d3.select(ref.current).selectAll('*').remove()
   const svg = d3
      .select(ref.current)

      .attr('viewBox', `-${width / 2} -${height / 2} ${width} ${height}`)
      .style('display', 'block')
      .style('margin', '0 -14px')
      .style('background', color(0))
      .style('cursor', 'pointer')
      .on('click', (event) => zoom(event, root))

   const node = svg
      .append('g')
      .selectAll('circle')
      .data(root.descendants())
      .join('circle')
      .attr('fill', (d) => (d.children ? color(d.depth) : 'white'))
      //.attr('pointer-events', (d) => (!d.children ? 'none' : null))
      .on('mouseover', function () {
         d3.select(this).attr('stroke', '#000')
      })
      .on('mouseout', function () {
         d3.select(this).attr('stroke', null)
      })

      .on('click', function (event, d) {
         if (!d.children) {
            router.push('/difference?id=' + d.data.id)
         } else focus !== d && (zoom(event, d), event.stopPropagation())
         event.stopPropagation()
      })

   let textWidth = 10
   const label = svg
      .append('g')
      .style('font', '0.8rem sans-serif')
      .attr('text-anchor', 'middle')
      .selectAll('text')
      .data(root.descendants())
      .join('text')
      .style('fill-opacity', (d) =>
         d.parent === root || root.children[0].children.includes(d) ? 1 : 1,
      )
      .style('width', (d) => '30')

      .style('display', (d) =>
         d.parent === root ||
         root.children[0].children.includes(d) ||
         root.children.includes(d)
            ? 'inline'
            : 'none',
      )

      .text((d) => d.data.name)

      .on('click', (d) => console.log('node', d))
      .call(wrap, textWidth)

   zoomTo([root.x, root.y, root.r * 2])

   function zoomTo(v) {
      const k = Math.min(height, width) / v[2]

      view = v

      label.attr(
         'transform',
         (d) => `translate(${(d.x - v[0]) * k},${(d.y - v[1]) * k})`,
      )
      node.attr(
         'transform',
         (d) => `translate(${(d.x - v[0]) * k},${(d.y - v[1]) * k})`,
      )
      node.attr('r', (d) => d.r * k)
   }

   function zoom(event, d) {
      focus = d

      const transition = svg
         .transition()
         .duration(event.altKey ? 7500 : 750)
         .tween('zoom', (d) => {
            const i = d3.interpolateZoom(view, [focus.x, focus.y, focus.r * 2])
            return (t) => zoomTo(i(t))
         })

      label
         .filter(function (d) {
            return d.parent === focus || this.style.display === 'inline'
         })
         .transition(transition)
         .style('fill-opacity', (d) => (d.parent === focus ? 1 : 0))
         .on('start', function (d) {
            if (d.parent === focus) this.style.display = 'inline'
         })
         .on('end', function (d) {
            if (d.parent !== focus) this.style.display = 'none'
         })
   }

   return svg.node()
}

export default function CirclePack({ data }) {
   const [trick, setTrick] = useState(false)
   useEffect(() => {
      function handleResize() {
         setTrick(!trick)
      }

      window.addEventListener('resize', handleResize)
   })
   const svgRef = React.useRef(null)
   const router = useRouter()
   useEffect(() => {
      const hierarchy = {
         name: 'library',
         children: [
            {
               name: '',
               children: data.links
                  .filter((l) => l.source === 'root')
                  .map((n) => ({
                     name: n.target,
                     children: rec_hierarchy(n.target, data),
                  })),
            },
         ],
      }
      chart(
         hierarchy,
         svgRef,
         window.innerWidth,
         window.innerHeight * 0.97,
         router,
      )
   }, [trick])
   return (
      // `<Tree />` will fill width/height of its container; in this case `#treeWrapper`.
      <div
         aria-description="Navigate to documents"
         aria-multiline={`
                  Click on the circles to zoom in and discover topics. And if you found one 
                  of the smallest circles, then click on the label to navigate to the document.`}
         id="treeWrapper"
         style={{
            marginTop: 'auto',
            marginLeft: 'auto',
            marginRight: 'auto',
            marginBottom: 'auto',

            width: window.innerWidth * 0.97,
            overflow: 'hidden',
         }}
      >
         <svg ref={svgRef} />
      </div>
   )
}
