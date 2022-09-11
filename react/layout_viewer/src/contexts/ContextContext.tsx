import React, {createContext, useState} from 'react'

export interface ContextContextType {
    slot
    setSlot?: (val) => void
}

const ContextContext = createContext<ContextContextType>(null)

const ContextWrapper = ({children}) => {
    let [slot, setSlot] = useState("normal")

    return (
        <ContextContext.Provider
            value={{
                slot,
                setSlot
            }}>
            {children}
        </ContextContext.Provider>
    )
};

export {ContextWrapper, ContextContext}

