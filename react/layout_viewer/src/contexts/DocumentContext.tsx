import React, { createContext, useState } from 'react'
import { Slot } from './SLOTS'

export interface DocumentContextType {
  value: any
  setValue?: (string) => void
  meta: any
  setMeta?: (any) => void
  setValueMetas?: (slot, [string, any]) => void
  setValueMeta?: (slot, string, any) => void
}

export type DocumentContextStateType = {
  [slot in Slot]: DocumentContextType
}

const DocumentContext = createContext<DocumentContextType>({
  value: null,
  meta: null,
})

const AppWrapper = ({ children }) => {
  let [state, setState] = useState<DocumentContextStateType>({captcha: undefined, normal: undefined})

  const setValueMeta = (slot: Slot, newValue: string, newMeta: any) => {
    state[slot] = { value: newValue, meta: newMeta }
    console.log('setState', state)

    setState({ ...state })
  }

  const meta = Object.fromEntries(
    Object.entries(state).map(([slot, entry]) => [slot, entry?.meta])
  )
  const value = Object.fromEntries(
    Object.entries(state).map(([slot, entry]) => [slot, entry?.value])
  )

  console.log('context', { children, value, meta })
  return (
    <DocumentContext.Provider
      value={{
        value,
        meta,
        setValueMetas: (slot, [value, meta]) => {
          console.log('setPlural',slot,  value, meta)
          setValueMeta(slot, value, meta)
        },
        setValueMeta: (slot, value, meta) => {
          console.log('setSingular', slot, value, meta)

          setValueMeta(slot,value, meta)
        },
      }}>
      {children}
    </DocumentContext.Provider>
  )
}


export { DocumentContext, AppWrapper}
