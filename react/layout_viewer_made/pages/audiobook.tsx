import React, { useContext, useEffect, useState } from 'react'
import MacroComponentSwitch from './../src/components/MacroComponentSwitch'

const Audiobook = () => {
   return <MacroComponentSwitch component={'download'} url={'/audiobook'} />
}

export default Audiobook
