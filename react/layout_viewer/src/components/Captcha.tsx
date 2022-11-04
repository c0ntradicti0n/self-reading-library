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

const Captcha = () => {
  const contextContext = useContext(ContextContext)
  const ref = useRef(null) // ref => { current: null }
  const [open, __setOpen] = useState(false)
  const [kind, setKind] = useState('annotation')

  const setOpen = (o) => {
    if (o) contextContext.setSlot('captcha')
    else contextContext.setSlot('normal')
    __setOpen(o)
  }

  return (
    <div data-backdrop="false">
      <a onClick={() => setOpen(true)}>Captcha</a>
      {open ? (
        <Modal
          open={open}
          footer={[
            <Button
              key="back"
              onClick={() => {
                setKind(switch_it[kind])
                ref?.current?.onCloseDiscard()
              }}>
              Unclear
            </Button>,
            <Button
              key="submit"
              type="primary"
              onClick={() => {
                setKind(switch_it[kind])
                ref?.current?.onCloseSave()
              }}>
              Submit
            </Button>,
            <Button onClick={() => setOpen(false)}>Finish game</Button>,
          ]}>
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
