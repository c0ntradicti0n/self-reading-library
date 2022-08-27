import React, { createContext, useEffect, useState } from 'react'
import { getParam } from '../helpers/httpGet'

export interface DocumentContextType {
  value: string
  setValue?: (string) => void
  meta: any
  setMeta?: (any) => void
  setValueMetas?: ([string, any]) => void
  setValueMeta?: (string, any) => void
}

export const DocumentContext = createContext<DocumentContextType>({
  value: null,
  meta: null,
})

export const AppWrapper = ({ children }) => {
  let [value, setValue] = useState(null)
  let [meta, setMeta] = useState(null)


  return (
    <DocumentContext.Provider
      value={{
        value,
        setValue,
        meta,
        setMeta,
        setValueMetas: ([value, meta]) => {
          console.log('setPlural', value, meta)
          setValue(value)
          setMeta(meta)
        },
        setValueMeta: (value, meta) => {
          console.log('setSingular', value, meta)

          setValue(value)
          setMeta(meta)
        },
      }}>
      {children}
    </DocumentContext.Provider>
  )
}
