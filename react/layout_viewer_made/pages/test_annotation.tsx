import React from 'react'
import MacroComponentSwitch from './../src/components/MacroComponentSwitch'
import { annotation_data } from '../src/tests/data/box.annotation'

const Annotation = () => {
   return (
      <MacroComponentSwitch
         input={annotation_data}
         component={'annotation'}
         url={'/annotation'}
      />
   )
}

export default Annotation
