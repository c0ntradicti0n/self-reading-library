import { useRef, useState } from 'react'

const Phi = 1.6168
const golden_cut = (n, a) => a * Phi ** n

function fibonacci(n) {
   return n < 1 ? 0 : n <= 2 ? 1 : fibonacci(n - 1) + fibonacci(n - 2)
}

const GoldenSnake = ({ a = 40, children, ...props }) => {
   const ref = useRef(null)
   const n = children.length + 3

   let j = 0
   let fib_sum = 0
   const writing_points = []
   let text_heights = []
   let val = 0
   let path = []
   let x_sum = 0
   let y_sum = 0
   const e = -0.04
   const f = 0.8
   const g = 0.13
   const h = 0.6
   const w = ref.current?.offsetWidth

   for (let i = 0; i < 11; i++) {
      val = golden_cut(i, a) * Phi
      let r_l = i % 2
      const _one = r_l ? 1 : -1

      const dx = (r_l ? -val : +val) * 0.4
      const dy = val

      if (i > 0)
         text_heights.push([
            x_sum + 400 + (600 / (dy / 100)) * _one,
            y_sum + (i == 2 ? -50 : 0),
            x_sum + dx,
            y_sum + dy,
            r_l,
         ])
      x_sum += dx
      y_sum += dy

      const a0 = [dx * h, _one * -e * dx]
      const a1 = [dx * f, dy * g]
      const a2 = [-dx * g, _one * e * dx]

      const b0 = [dx * (1 - g), _one * -e * dx]
      const b1 = [dx * f, dy * (1 - g)]
      const b2 = [-dx * h, _one * e * dx]
      path.push([...a0, ...b0, dx, 0])
      path.push([...a1, ...b1, 0, dy])
      path.push([...a2, ...b2, -dx, 0])
   }
   path = path.map((p) => p.map(Math.round))
   text_heights = text_heights.map((p) => p.map((p) => p * 0.37))

   console.log(ref)

   const pathD = 'M 0 50 c ' + path.map((t, i) => t.join(' ')).join('\n c ')
   return (
      <div
         ref={ref}
         style={{ position: 'relative', width: '500px', height: '2000px' }}
         {...props}
      >
         <div
            style={{
               padding: '0px',
               height: '150vh',
               width: '900px',
               position: 'relative',
            }}
         >
            <svg
               xmlns="http://www.w3.org/2000/svg"
               width="510px"
               height="1500px"
               preserveAspectRatio="xMinYMin meet"
               viewBox={`-250 0 250 1500`}
            >
               <path
                  rx="10px"
                  ry="10px"
                  stroke-linejoin="round"
                  stroke-linecap="round"
                  d={pathD}
                  fill="none"
                  stroke="black"
                  stroke-width="10"
               />
            </svg>
            {text_heights.slice(1).map(([x1, y1, x2, y2, r_l], i) => {
               const fib = fibonacci(i + 1)
               const nodes = children.slice(fib_sum, fib_sum + fib)
               fib_sum += fib
               return (
                  <div
                     key={'b' + i}
                     style={{
                        display: 'table-cell',
                        position: 'absolute',
                        top: y1.toString() + 'px',
                        height: (y2 - y1).toString() + 'px',
                        textAlign: r_l ? 'left' : 'right',
                        left: +x1.toString() + 'px',
                     }}
                  >
                     <div
                        style={{
                           position: 'relative',
                           top: '50%',

                           transform: 'translateY(-50%)',
                        }}
                     >
                        {' '}
                        {nodes}
                     </div>
                  </div>
               )
            })}
         </div>
      </div>
   )
}

export default GoldenSnake
