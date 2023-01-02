import React, { createContext, useState } from 'react'
import { Slot } from './SLOTS'
import { TourProps } from 'antd'

export interface DocumentContextType {
   value: any
   setValue?: (string) => void
   meta: any
   setMeta?: (any) => void
   setValueMetas?: (slot, [string, any]) => void
   setValueMeta?: (slot, string, any) => void
   helpSteps?: TourProps['steps']
   setHelpSteps?: (steps: TourProps['steps']) => void
}

export type DocumentContextStateType = {
   [slot in Slot]: DocumentContextType
}

const DocumentContext = createContext<DocumentContextType>({
   value: null,
   meta: null,
   helpSteps: null,
})

const AppWrapper = ({ children }) => {
   let [state, setState] = useState<DocumentContextStateType>({
      captcha: undefined,
      normal: undefined,
   })

   let [helpSteps, setHelpSteps] = useState<TourProps['steps']>()

   const setValueMeta = (slot: Slot, newValue: string, newMeta: any) => {
      state[slot] = { value: newValue, meta: newMeta }

      setState({ ...state })
   }

   const meta = Object.fromEntries(
      Object.entries(state).map(([slot, entry]) => [slot, entry?.meta]),
   )
   const value = Object.fromEntries(
      Object.entries(state).map(([slot, entry]) => [slot, entry?.value]),
   )

   const references = (ref) => {
      ref
   }
   return (
      <DocumentContext.Provider
         value={{
            value,
            meta,
            setValueMetas: (slot, value_meta) => {
               const [value, meta] = value_meta ?? [null, null]
               setValueMeta(slot, value, meta)
            },
            setValueMeta: (slot, value, meta) => {
               setValueMeta(slot, value, meta)
            },
            setHelpSteps,
            helpSteps,
            references,
         }}
      >
         {children}
      </DocumentContext.Provider>
   )
}

export { DocumentContext, AppWrapper }
