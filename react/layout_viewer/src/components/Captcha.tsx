import React, { useContext, useState } from 'react'
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
}

const Captcha = () => {
  const contextContext = useContext(ContextContext)
  console.log('contextContext', contextContext)

  const [open, __setOpen] = useState(false)
  const setOpen = (o) => {
    console.log('setOpen', o)

    if (o) contextContext.setSlot('captcha')
    else contextContext.setSlot('normal')
    __setOpen(o)
  }

  const [kind, setKind] = useState('annotation')

  return (
    <div data-backdrop="false">
      <a onClick={() => setOpen(true)}>Captcha</a>
      {open ? (
        <Modal
          title={'Human in the loop, please do'}
          open={open}
          onOk={() => setOpen(false)}
          onCancel={() => setOpen(false)}
          onClose={() => setOpen(false)}
          onClick={(e) => {
            e.preventDefault()
            e.stopPropagation()
            console.log('stop it!')
          }}>
          <MacroComponentSwitch
            component={kind}
            url={Kind[kind].url}
            slot={CAPTCHA}
          />
          <Button variant="outlined" onClick={() => setOpen(false)}>
            Solved
          </Button>
        </Modal>
      ) : null}
    </div>
  )
}

export default Captcha
