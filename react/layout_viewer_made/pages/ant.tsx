import React, { useContext, useEffect, useState } from 'react'
import MacroComponentSwitch from './../src/components/MacroComponentSwitch'

const Ant = () => {
   return <MacroComponentSwitch component={'graph'} url={'/ant'} />
}

export default Ant
