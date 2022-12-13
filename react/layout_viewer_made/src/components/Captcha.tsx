import React, { useContext, useRef, useState } from 'react'
import { Button, Modal } from 'antd'
import MacroComponentSwitch from './MacroComponentSwitch'
import { ContextContext } from '../contexts/ContextContext'
import { CAPTCHA } from '../contexts/SLOTS'

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

const Captcha = ({is_open=true}) => {
   const contextContext = useContext(ContextContext)
   const ref = useRef(null) // ref => { current: null }
   const [open, __setOpen] = useState(is_open)
   const [kind, setKind] = useState('annotation')

   const setOpen = (o) => {
      if (o) contextContext.setSlot('captcha')
      else contextContext.setSlot('normal')
      __setOpen(o)
   }

   return (
      <div data-backdrop="false">
         {!is_open && <a onClick={() => setOpen(true)}>Captcha</a> }
         {open ? (
            <Modal
               open={open}
               footer={[
                  <Button
                     key="back"
                     onClick={() => {
                        if (ref?.current?.onCloseDiscard())
                           setKind(switch_it[kind])
                     }}
                  >
                     Don't know the solution
                  </Button>,
                  <Button
                     key="submit"
                     type="primary"
                     onClick={() => {
                        if (ref?.current?.onCloseSave())
                           setKind(switch_it[kind])
                     }}
                  >
                     All is right now
                  </Button>,
                  <Button onClick={() => setOpen(false)}>I grew the dataset enough</Button>,
               ]}
            >
               <MacroComponentSwitch
                  ref={ref}
                  component={kind}
                  url={Kind[kind].url}
                  slot={CAPTCHA}
               />
            </Modal>
         ) : null}
      </div>
   )
}

export default Captcha
