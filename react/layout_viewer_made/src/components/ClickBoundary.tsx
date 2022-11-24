export const ClickBoundary = ({ children }) => (
  <div
    style={{ height: '100%' }}
    onClick={(e) => {
      e.stopPropagation()
      e.preventDefault()
      console.log('stop it! click')
    }}
    onMouseUp={(e) => {
      e.stopPropagation()
      e.preventDefault()
      console.log('stop it! up')
    }}
    onChange={(e) => {
      e.stopPropagation()
      e.preventDefault()
      console.log('stop it! change')
    }}
    onBlur={(e) => {
      e.stopPropagation()
      e.preventDefault()
      console.log('stop it! blur')
    }}>
    {children}
  </div>
)
