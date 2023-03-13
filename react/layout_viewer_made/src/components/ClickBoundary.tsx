export const ClickBoundary = ({ children }) => (
   <div
      style={{ height: '100%' }}
      onClick={(e) => {
         e.stopPropagation()
         e.preventDefault()
      }}
      onMouseUp={(e) => {
         e.stopPropagation()
         e.preventDefault()
      }}
      onChange={(e) => {
         e.stopPropagation()
         e.preventDefault()
      }}
      onBlur={(e) => {
         e.stopPropagation()
         e.preventDefault()
      }}
   >
      {children}
   </div>
)
