export const ClickBoundary = ({ children }) => (
   <div
      style={{ height: '100%' }}
      onClick={(e) => {
         e.stopPropagation()
         e.preventDefault()
         console.debug('stop it! click')
      }}
      onMouseUp={(e) => {
         e.stopPropagation()
         e.preventDefault()
         console.debug('stop it! up')
      }}
      onChange={(e) => {
         e.stopPropagation()
         e.preventDefault()
         console.debug('stop it! change')
      }}
      onBlur={(e) => {
         e.stopPropagation()
         e.preventDefault()
         console.debug('stop it! blur')
      }}
   >
      {children}
   </div>
)
