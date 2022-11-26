import { useState } from 'react'

const SelectText = ({ children, onSelect = null }) => {
  const [selected, setSelected] = useState(null)

  const handleMouseUp = () => {
    const text = window.getSelection().toString()
    setSelected(text)
    console.log(`Selected text: ${text}`)

    if (onSelect) onSelect(text)
    console.log(`Selected text: ${text}`)
  }
  console.log(children)

  return (
    <div onMouseUp={handleMouseUp}>
      {typeof children === 'function'
        ? children(selected, setSelected)
        : children}
    </div>
  )
}

export default SelectText
