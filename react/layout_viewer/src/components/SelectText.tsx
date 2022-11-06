import { useState } from 'react'
import AnnotationSpan, { AnnotationModal } from './AnnotationSpan'

const SelectText = ({ children, onSelect = null }) => {
  const [selected, setSelected] = useState(null)

  const handleMouseUp = () => {
    setSelected(window.getSelection().toString())
    if (onSelect) onSelect(selected)
    console.log(`Selected text: ${window.getSelection().toString()}`)
  }
  console.log(children)

  return <div onMouseUp={handleMouseUp}>{
    (typeof children === 'function') ? children(selected, setSelected): children}</div>
}

export default SelectText
