import React, { createContext, useState } from 'react'

export interface DocumentContextType {
   value: string
   setValue?: (string) => void
   meta: any
   setMeta?: (any) => void
   setValueMetas?: ([string, any]) => void
   setValueMeta?: (string, any) => void
}

const DocumentContext = createContext<DocumentContextType>({
   value: null,
   meta: null,
})

const AppWrapper = ({ presetValue = null, children }) => {
   let [value, setValue] = useState(presetValue)
   let [meta, setMeta] = useState(null)

   return (
      <DocumentContext.Provider
         value={{
            value,
            setValue,
            meta,
            setMeta,
            setValueMetas: ([value, meta]) => {
               console.debug('setPlural', value, meta)
               setValue(value)
               setMeta(meta)
            },
            setValueMeta: (value, meta) => {
               console.debug('setSingular', value, meta)

               setValue(value)
               setMeta(meta)
            },
         }}
      >
         {children}
      </DocumentContext.Provider>
   )
}

export { AppWrapper, DocumentContext }
