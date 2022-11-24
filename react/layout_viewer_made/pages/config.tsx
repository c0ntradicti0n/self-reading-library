
import React, {useContext, useEffect, useState} from 'react'
import MacroComponentSwitch from './../src/components/MacroComponentSwitch'

const Config = () => {
     return <MacroComponentSwitch component={"dict"} url={'/config'} />
}

export default Config    
    