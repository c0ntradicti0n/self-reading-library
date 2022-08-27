import { useState } from 'react'
import SpanAnnotation from './SpanAnnotation'

const SelectText = ({ service, children }) => {
  const [selected, setSelected] = useState(null)

  const handleMouseUp = () => {
    setSelected(window.getSelection().toString())
    console.log(`Selected text: ${window.getSelection().toString()}`)
  }

  return (
    <div onMouseUp={handleMouseUp}>
      {selected && (
        <SpanAnnotation
          text={selected}
          onClose={() => setSelected(null)}
          service={service}
        />
      )}
      {children}
    </div>
  )
}

export default SelectText
