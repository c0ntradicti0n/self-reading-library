import React, { useEffect, useState } from 'react'
import Tree from 'react-d3-tree'
import * as d3 from 'd3'
import { width } from '@mui/system'

const d = {
   name: 'flare',
   children: [
      {
         name: 'analytics',
         children: [
            {
               name: 'cluster',
               children: [
                  { name: 'AgglomerativeCluster', size: 3938 },
                  { name: 'CommunityStructure', size: 3812 },
                  { name: 'HierarchicalCluster', size: 6714 },
                  { name: 'MergeEdge', size: 743 },
               ],
            },
            {
               name: 'graph',
               children: [
                  { name: 'BetweennessCentrality', size: 3534 },
                  { name: 'LinkDistance', size: 5731 },
                  { name: 'MaxFlowMinCut', size: 7840 },
                  { name: 'ShortestPaths', size: 5914 },
                  { name: 'SpanningTree', size: 3416 },
               ],
            },
            {
               name: 'optimization',
               children: [{ name: 'AspectRatioBanker', size: 7074 }],
            },
         ],
      },
      {
         name: 'animate',
         children: [
            { name: 'Easing', size: 17010 },
            { name: 'FunctionSequence', size: 5842 },
            {
               name: 'interpolate',
               children: [
                  { name: 'ArrayInterpolator', size: 1983 },
                  { name: 'ColorInterpolator', size: 2047 },
                  { name: 'DateInterpolator', size: 1375 },
                  { name: 'Interpolator', size: 8746 },
                  { name: 'MatrixInterpolator', size: 2202 },
                  { name: 'NumberInterpolator', size: 1382 },
                  { name: 'ObjectInterpolator', size: 1629 },
                  { name: 'PointInterpolator', size: 1675 },
                  { name: 'RectangleInterpolator', size: 2042 },
               ],
            },
            { name: 'ISchedulable', size: 1041 },
            { name: 'Parallel', size: 5176 },
            { name: 'Pause', size: 449 },
            { name: 'Scheduler', size: 5593 },
            { name: 'Sequence', size: 5534 },
            { name: 'Transition', size: 9201 },
            { name: 'Transitioner', size: 19975 },
            { name: 'TransitionEvent', size: 1116 },
            { name: 'Tween', size: 6006 },
         ],
      },
      {
         name: 'data',
         children: [
            {
               name: 'converters',
               children: [
                  { name: 'Converters', size: 721 },
                  { name: 'DelimitedTextConverter', size: 4294 },
                  { name: 'GraphMLConverter', size: 9800 },
                  { name: 'IDataConverter', size: 1314 },
                  { name: 'JSONConverter', size: 2220 },
               ],
            },
            { name: 'DataField', size: 1759 },
            { name: 'DataSchema', size: 2165 },
            { name: 'DataSet', size: 586 },
            { name: 'DataSource', size: 3331 },
            { name: 'DataTable', size: 772 },
            { name: 'DataUtil', size: 3322 },
         ],
      },
      {
         name: 'display',
         children: [
            { name: 'DirtySprite', size: 8833 },
            { name: 'LineSprite', size: 1732 },
            { name: 'RectSprite', size: 3623 },
            { name: 'TextSprite', size: 10066 },
         ],
      },
      { name: 'flex', children: [{ name: 'FlareVis', size: 4116 }] },
      {
         name: 'physics',
         children: [
            { name: 'DragForce', size: 1082 },
            { name: 'GravityForce', size: 1336 },
            { name: 'IForce', size: 319 },
            { name: 'NBodyForce', size: 10498 },
            { name: 'Particle', size: 2822 },
            { name: 'Simulation', size: 9983 },
            { name: 'Spring', size: 2213 },
            { name: 'SpringForce', size: 1681 },
         ],
      },
      {
         name: 'query',
         children: [
            { name: 'AggregateExpression', size: 1616 },
            { name: 'And', size: 1027 },
            { name: 'Arithmetic', size: 3891 },
            { name: 'Average', size: 891 },
            { name: 'BinaryExpression', size: 2893 },
            { name: 'Comparison', size: 5103 },
            { name: 'CompositeExpression', size: 3677 },
            { name: 'Count', size: 781 },
            { name: 'DateUtil', size: 4141 },
            { name: 'Distinct', size: 933 },
            { name: 'Expression', size: 5130 },
            { name: 'ExpressionIterator', size: 3617 },
            { name: 'Fn', size: 3240 },
            { name: 'If', size: 2732 },
            { name: 'IsA', size: 2039 },
            { name: 'Literal', size: 1214 },
            { name: 'Match', size: 3748 },
            { name: 'Maximum', size: 843 },
            {
               name: 'methods',
               children: [
                  { name: 'add', size: 593 },
                  { name: 'and', size: 330 },
                  { name: 'average', size: 287 },
                  { name: 'count', size: 277 },
                  { name: 'distinct', size: 292 },
                  { name: 'div', size: 595 },
                  { name: 'eq', size: 594 },
                  { name: 'fn', size: 460 },
                  { name: 'gt', size: 603 },
                  { name: 'gte', size: 625 },
                  { name: 'iff', size: 748 },
                  { name: 'isa', size: 461 },
                  { name: 'lt', size: 597 },
                  { name: 'lte', size: 619 },
                  { name: 'max', size: 283 },
                  { name: 'min', size: 283 },
                  { name: 'mod', size: 591 },
                  { name: 'mul', size: 603 },
                  { name: 'neq', size: 599 },
                  { name: 'not', size: 386 },
                  { name: 'or', size: 323 },
                  { name: 'orderby', size: 307 },
                  { name: 'range', size: 772 },
                  { name: 'select', size: 296 },
                  { name: 'stddev', size: 363 },
                  { name: 'sub', size: 600 },
                  { name: 'sum', size: 280 },
                  { name: 'update', size: 307 },
                  { name: 'variance', size: 335 },
                  { name: 'where', size: 299 },
                  { name: 'xor', size: 354 },
                  { name: '_', size: 264 },
               ],
            },
            { name: 'Minimum', size: 843 },
            { name: 'Not', size: 1554 },
            { name: 'Or', size: 970 },
            { name: 'Query', size: 13896 },
            { name: 'Range', size: 1594 },
            { name: 'StringUtil', size: 4130 },
            { name: 'Sum', size: 791 },
            { name: 'Variable', size: 1124 },
            { name: 'Variance', size: 1876 },
            { name: 'Xor', size: 1101 },
         ],
      },
      {
         name: 'scale',
         children: [
            { name: 'IScaleMap', size: 2105 },
            { name: 'LinearScale', size: 1316 },
            { name: 'LogScale', size: 3151 },
            { name: 'OrdinalScale', size: 3770 },
            { name: 'QuantileScale', size: 2435 },
            { name: 'QuantitativeScale', size: 4839 },
            { name: 'RootScale', size: 1756 },
            { name: 'Scale', size: 4268 },
            { name: 'ScaleType', size: 1821 },
            { name: 'TimeScale', size: 5833 },
         ],
      },
      {
         name: 'util',
         children: [
            { name: 'Arrays', size: 8258 },
            { name: 'Colors', size: 10001 },
            { name: 'Dates', size: 8217 },
            { name: 'Displays', size: 12555 },
            { name: 'Filter', size: 2324 },
            { name: 'Geometry', size: 10993 },
            {
               name: 'heap',
               children: [
                  { name: 'FibonacciHeap', size: 9354 },
                  { name: 'HeapNode', size: 1233 },
               ],
            },
            { name: 'IEvaluable', size: 335 },
            { name: 'IPredicate', size: 383 },
            { name: 'IValueProxy', size: 874 },
            {
               name: 'math',
               children: [
                  { name: 'DenseMatrix', size: 3165 },
                  { name: 'IMatrix', size: 2815 },
                  { name: 'SparseMatrix', size: 3366 },
               ],
            },
            { name: 'Maths', size: 17705 },
            { name: 'Orientation', size: 1486 },
            {
               name: 'palette',
               children: [
                  { name: 'ColorPalette', size: 6367 },
                  { name: 'Palette', size: 1229 },
                  { name: 'ShapePalette', size: 2059 },
                  { name: 'SizePalette', size: 2291 },
               ],
            },
            { name: 'Property', size: 5559 },
            { name: 'Shapes', size: 19118 },
            { name: 'Sort', size: 6887 },
            { name: 'Stats', size: 6557 },
            { name: 'Strings', size: 22026 },
         ],
      },
      {
         name: 'vis',
         children: [
            {
               name: 'axis',
               children: [
                  { name: 'Axes', size: 1302 },
                  { name: 'Axis', size: 24593 },
                  { name: 'AxisGridLine', size: 652 },
                  { name: 'AxisLabel', size: 636 },
                  { name: 'CartesianAxes', size: 6703 },
               ],
            },
            {
               name: 'controls',
               children: [
                  { name: 'AnchorControl', size: 2138 },
                  { name: 'ClickControl', size: 3824 },
                  { name: 'Control', size: 1353 },
                  { name: 'ControlList', size: 4665 },
                  { name: 'DragControl', size: 2649 },
                  { name: 'ExpandControl', size: 2832 },
                  { name: 'HoverControl', size: 4896 },
                  { name: 'IControl', size: 763 },
                  { name: 'PanZoomControl', size: 5222 },
                  { name: 'SelectionControl', size: 7862 },
                  { name: 'TooltipControl', size: 8435 },
               ],
            },
            {
               name: 'data',
               children: [
                  { name: 'Data', size: 20544 },
                  { name: 'DataList', size: 19788 },
                  { name: 'DataSprite', size: 10349 },
                  { name: 'EdgeSprite', size: 3301 },
                  { name: 'NodeSprite', size: 19382 },
                  {
                     name: 'render',
                     children: [
                        { name: 'ArrowType', size: 698 },
                        { name: 'EdgeRenderer', size: 5569 },
                        { name: 'IRenderer', size: 353 },
                        { name: 'ShapeRenderer', size: 2247 },
                     ],
                  },
                  { name: 'ScaleBinding', size: 11275 },
                  { name: 'Tree', size: 7147 },
                  { name: 'TreeBuilder', size: 9930 },
               ],
            },
            {
               name: 'events',
               children: [
                  { name: 'DataEvent', size: 2313 },
                  { name: 'SelectionEvent', size: 1880 },
                  { name: 'TooltipEvent', size: 1701 },
                  { name: 'VisualizationEvent', size: 1117 },
               ],
            },
            {
               name: 'legend',
               children: [
                  { name: 'Legend', size: 20859 },
                  { name: 'LegendItem', size: 4614 },
                  { name: 'LegendRange', size: 10530 },
               ],
            },
            {
               name: 'operator',
               children: [
                  {
                     name: 'distortion',
                     children: [
                        { name: 'BifocalDistortion', size: 4461 },
                        { name: 'Distortion', size: 6314 },
                        { name: 'FisheyeDistortion', size: 3444 },
                     ],
                  },
                  {
                     name: 'encoder',
                     children: [
                        { name: 'ColorEncoder', size: 3179 },
                        { name: 'Encoder', size: 4060 },
                        { name: 'PropertyEncoder', size: 4138 },
                        { name: 'ShapeEncoder', size: 1690 },
                        { name: 'SizeEncoder', size: 1830 },
                     ],
                  },
                  {
                     name: 'filter',
                     children: [
                        { name: 'FisheyeTreeFilter', size: 5219 },
                        { name: 'GraphDistanceFilter', size: 3165 },
                        { name: 'VisibilityFilter', size: 3509 },
                     ],
                  },
                  { name: 'IOperator', size: 1286 },
                  {
                     name: 'label',
                     children: [
                        { name: 'Labeler', size: 9956 },
                        { name: 'RadialLabeler', size: 3899 },
                        { name: 'StackedAreaLabeler', size: 3202 },
                     ],
                  },
                  {
                     name: 'layout',
                     children: [
                        { name: 'AxisLayout', size: 6725 },
                        { name: 'BundledEdgeRouter', size: 3727 },
                        { name: 'CircleLayout', size: 9317 },
                        { name: 'CirclePackingLayout', size: 12003 },
                        { name: 'DendrogramLayout', size: 4853 },
                        { name: 'ForceDirectedLayout', size: 8411 },
                        { name: 'IcicleTreeLayout', size: 4864 },
                        { name: 'IndentedTreeLayout', size: 3174 },
                        { name: 'Layout', size: 7881 },
                        { name: 'NodeLinkTreeLayout', size: 12870 },
                        { name: 'PieLayout', size: 2728 },
                        { name: 'RadialTreeLayout', size: 12348 },
                        { name: 'RandomLayout', size: 870 },
                        { name: 'StackedAreaLayout', size: 9121 },
                        { name: 'TreeMapLayout', size: 9191 },
                     ],
                  },
                  { name: 'Operator', size: 2490 },
                  { name: 'OperatorList', size: 5248 },
                  { name: 'OperatorSequence', size: 4190 },
                  { name: 'OperatorSwitch', size: 2581 },
                  { name: 'SortOperator', size: 2023 },
               ],
            },
            { name: 'Visualization', size: 16540 },
         ],
      },
   ],
}

function Pack(
   data,
   svgRef,
   {
      // data is either tabular (array of objects) or hierarchy (nested objects)
      path, // as an alternative to id and parentId, returns an array identifier, imputing internal nodes
      id = Array.isArray(data) ? (d) => d.id : null, // if tabular data, given a d in data, returns a unique identifier (string)
      parentId = Array.isArray(data) ? (d) => d.parentId : null, // if tabular data, given a node d, returns its parent’s identifier
      children, // if hierarchical data, given a d in data, returns its children
      value, // given a node d, returns a quantitative value (for area encoding; null for count)
      sort = (a, b) => d3.descending(a.value, b.value), // how to sort nodes prior to layout
      label, // given a leaf node d, returns the display name
      title, // given a node d, returns its hover text
      link, // given a node d, its link (if any)
      linkTarget = '_blank', // the target attribute for links, if any
      width = 640, // outer width, in pixels
      height = 400, // outer height, in pixels
      margin = 1, // shorthand for margins
      marginTop = margin, // top margin, in pixels
      marginRight = margin, // right margin, in pixels
      marginBottom = margin, // bottom margin, in pixels
      marginLeft = margin, // left margin, in pixels
      padding = 3, // separation between circles
      fill = '#dd0', // fill for leaf circles
      fillOpacity = 0.3, // fill opacity for leaf circles
      stroke = '#000', // stroke for internal circles
      strokeWidth = 2, // stroke width for internal circles
      strokeOpacity = 0.4, // stroke opacity for internal circles
   } = {},
) {

   // If id and parentId options are specified, or the path option, use d3.stratify
   // to convert tabular data to a hierarchy; otherwise we assume that the data is
   // specified as an object {children} with nested objects (a.k.a. the “flare.json”
   // format), and use d3.hierarchy.
   const root =
      path != null
         ? d3.stratify().path(path)(data)
         : id != null || parentId != null
         ? d3.stratify().id(id).parentId(parentId)(data)
         : d3.hierarchy(data, children)

   // Compute the values of internal nodes by aggregating from the leaves.
   value == null ? root.count() : root.sum((d) => Math.max(0, value(d)))

   // Compute labels and titles.
   const descendants = root.descendants()
   const leaves = descendants.filter((d) => !d.children)
   leaves.forEach((d, i) => (d.index = i))
   const L = label == null ? null : leaves.map((d) => label(d.data, d))
   const T = title == null ? null : descendants.map((d) => title(d.data, d))
   function handleZoom(e) {
      d3.select(svgRef.current).attr('transform', e.transform)
   }
   let zoom = d3.zoom().on('zoom', handleZoom)

   // Sort the leaves (typically by descending value for a pleasing layout).
   if (sort != null) root.sort(sort)

   // Compute the layout.
   d3
      .pack()
      .size([
         width - marginLeft - marginRight,
         height - marginTop - marginBottom,
      ])
      .padding(padding)(root)

   const svg = d3
      .select(svgRef.current)
      .attr('viewBox', [-marginLeft, -marginTop, width, height])
      .attr('width', width)
      .attr('height', height)
      .attr('style', 'max-width: 100%; height: auto; height: intrinsic;')
      .attr('font-family', 'sans-serif')
      .attr('font-size', 10)
      .attr('text-anchor', 'middle')
      .call(zoom)

   const node = svg
      .selectAll('a')
      .data(descendants)
      .join('a')
      .attr('xlink:href', link == null ? null : (d, i) => link(d.data, d))
      .attr('target', link == null ? null : linkTarget)
      .attr('transform', (d) => `translate(${d.x},${d.y})`)

   node
      .append('circle')
      .attr('fill', (d, n) =>
         d.children ? `#${(n + 3) % 9}${(n + 4) % 10}${(n + 5) % 11}` : fill,
      )
      .attr('fill-opacity', (d) => (d.children ? null : fillOpacity))
      // .attr("stroke", d => d.children ? stroke : null)
      // .attr("stroke-width", d => d.children ? strokeWidth : null)
      // .attr("stroke-opacity", d => d.children ? strokeOpacity : null)
      .attr('r', (d) => d.r)
      .on('click', (o) => console.log('Click!', o))

   if (T) node.append('title').text((d, i) => T[i])

   if (L) {
      // A unique identifier for clip paths (to avoid conflicts).
      const uid = `O-${Math.random().toString(16).slice(2)}`

      const leaf = node.filter(
         (d) => !d.children && d.r > 10 && L[d.index] != null,
      )

      leaf
         .append('clipPath')
         .attr('id', (d) => `${uid}-clip-${d.index}`)
         .append('circle')
         .attr('r', (d) => d.r)

      leaf
         .append('text')
         .attr(
            'clip-path',
            (d) => `url(${new URL(`#${uid}-clip-${d.index}`, location)})`,
         )
         .selectAll('tspan')
         .data((d) => `ÖÖÖÖ`.split(/\n/g))
         .join('tspan')
         .attr('x', 0)
         .attr('y', (d, i, D) => `${i - D.length / 2 + 0.85}em`)
         .attr('fill-opacity', (d, i, D) => (i === D.length - 1 ? 0.7 : null))
         .text((d) => d)

      const edges = d3
         .linkVertical()
         .x((d) => d.x)
         .y((d) => d.y)({
         source: 2,
         target: 67,
      })

      // Add the link with arrowhead at the end
      svg.append('path')
         .attr('d', edges)
         .attr('marker-end', 'url(#arrow)')
         .attr('stroke', 'black')
         .attr('fill', 'none')
   }

   return svg.node()
}

export default function BubbleGraph({ height = 1000, width = 1000 }) {
   const svgRef = React.useRef(null)

   const [svg, setSvg] = useState(null)
   useEffect(() => {
      const svg = Pack(d, svgRef, {
         value: (d) => d.size, // size of each node (file); null for internal nodes (folders)
         label: (d, n) =>
            [
               ...d.name.split(/(?=[A-Z][a-z])/g),
               n.value.toLocaleString('en'),
            ].join('\n'),
         title: (d, n) =>
            `${n
               .ancestors()
               .reverse()
               .map(({ data: d }) => d.name)
               .join('.')}\n${n.value.toLocaleString('en')}`,
         link: (d, n) => console.log(d, n),
         width: window.innerWidth * 0.9,
         height: window.innerHeight * 0.9,
      })
   }, [])
   return (
      // `<Tree />` will fill width/height of its container; in this case `#treeWrapper`.
      <div
         id="treeWrapper"
         style={{ width: '100%', height: '94%', overflow: 'hidden' }}
      >
         <svg
            style={{ width: '100%', height: '94%', overflow: 'hidden' }}
            ref={svgRef}
            width={width}
            height={height}
         />
         ;
      </div>
   )
}
