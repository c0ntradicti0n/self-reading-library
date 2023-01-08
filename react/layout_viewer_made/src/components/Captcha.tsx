import React, { useContext, useRef, useState } from 'react'
import { Button, Modal } from 'antd'
import MacroComponentSwitch from './MacroComponentSwitch'
import { ContextContext } from '../contexts/ContextContext'
import {CAPTCHA, NORMAL} from '../contexts/SLOTS'
import {Help} from "./Tour";

const Kind: {
   [kind: string]: {
      title: string
      url: string
   }
} = {
   annotation: {
      title: 'Where is the text?',
      url: '/layout_captcha',
   },
   span_annotation: {
      title: 'Where is the difference?',
      url: '/difference_captcha',
   },
}

const switch_it = {
   annotation: 'span_annotation',
   span_annotation: 'annotation',
}

const Captcha = ({ is_open = true }) => {
   const contextContext = useContext(ContextContext)
   const ref = useRef(null) // ref => { current: null }
   const [open, __setOpen] = useState(is_open)
      const [hopen, sethOpen] = useState(false)

   const [kind, setKind] = useState('annotation')

   const setOpen = (o) => {
      if (o) contextContext.setSlot('captcha')
      else contextContext.setSlot('normal')
      __setOpen(o)
   }

   return (
      <div>
         {!is_open && (
            <Button type="link" onClick={() => setOpen(true)}>
               Captcha
            </Button>
         )}
         {open ? (
            <Modal
               style={{ height: '100% !important' }}
               open={open}
               onCancel={() => setOpen(false)}
               footer={[
                  <Button
                     aria-description={
                        "If you don't know, how to label this, you can skip it here"
                     }
                     key="back"
                     onClick={() => {
                        if (ref?.current?.onCloseDiscard())
                           setKind(switch_it[kind])
                     }}
                  >
                     Don't know the solution
                  </Button>,
                  <Button
                     aria-description={
                        'If you finished with this one, go here. The next one will come'
                     }
                     key="submit"
                     type="primary"
                     onClick={() => {
                        if (ref?.current?.onCloseSave())
                           setKind(switch_it[kind])
                     }}
                  >
                     All is right now
                  </Button>,
                  <Button
                     aria-description={
                        'If you want to get out of here, click here'
                     }
                     onClick={() => setOpen(false)}
                  >
                     I grew the dataset enough
                  </Button>,
                   <>
            {open ? <Help open={hopen} setOpen={sethOpen} /> : null}
            <Button type="link" onClick={() => sethOpen(!hopen)}>
               Help me!
            </Button>
         </>
               ]}
            >
               <div style={{ zIndex: 10000 }}>
                  <MacroComponentSwitch
                     ref={ref}
                     component={kind}
                     url={Kind[kind].url}
                     slot={CAPTCHA}
                  />
               </div>
            </Modal>
         ) : null}
      </div>
   )
}

export default Captcha
