const Phi = 1.6168
const golden_cut = (n, a) => a * Phi ** n
function fibonacci(n) {
  return n < 1 ? 0 : n <= 2 ? 1 : fibonacci(n - 1) + fibonacci(n - 2)
}
const GoldenSnake = ({ a = 20, children }) => {
  const n = children.length + 3

  let j = 0
  const writing_points = []
  const text_heights = []
  let h = 0
  let val = 0
  let old_val = 0
  let box_or_line = false
  return (
    <div style={{ padding: '100px', position: 'relative' }}>
      <div
        style={{
          padding: '0px',
          height: '100vh',
          width: '900px',
          position: 'relative',
        }}>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="100%"
          height="100%"
          preserveAspectRatio="xMinYMin meet">
          {[...Array(n).keys()].map((i, n) => {
            j += 1
            if (j > 2) j = -1
            h = old_val + h

            val = golden_cut(i, a)
            old_val = val
            let x1 = 10
            let y1 = h

            old_val = val

            let y2 = h + old_val
            let x2 = (x1 + val) * 2.7 + 100

            writing_points.push([(y1 + y2) / 2 + 100])

            box_or_line = !box_or_line

            text_heights.push([y1 + 5, y2 - 5])

            if (box_or_line)
              return (
                <line key={'n1' + n} x1={x1} y1={y1} x2={x1} y2={y2}></line>
              )
            else
              return (
                <g key={'g1' + n}>
                  <line key={'n1' + n} x1={x1} y1={y1} x2={x2} y2={y1}></line>
                  <line key={'n2' + n} x1={x2} y1={y1} x2={x2} y2={y2}></line>
                  <line key={'n3' + n} x1={x2} y1={y2} x2={x1} y2={y2}></line>
                </g>
              )
          })}
        </svg>
        {text_heights.slice(1).map(([y1, y2], i) => {
          const fib_1 = fibonacci(i + 4) - 2
          const fib_0 = fibonacci(i + 3) - 2
          const nodes = children.slice(fib_0, fib_1)

          return (
            <div
              key={'b' + i}
              style={{
                verticalAlign: 'middle',
                display: 'table-cell',

                position: 'absolute',
                left: '20px',
                top: y1.toString() + 'px',
                height: (y2 - y1).toString() + 'px',
              }}>
              {nodes}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default GoldenSnake
