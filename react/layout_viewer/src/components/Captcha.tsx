import BoxAnnotator from './BoxAnnotator'
import Button from '@mui/material/Button'
import { BootstrapDialogTitle } from './BootstrapDialogueTitle'
import { DialogContent } from '@mui/material'
import { BootstrapDialog } from './BootstrapDialogue'
import { useState } from 'react'
import GeneralResource from '../resources/GeneralResource'

const Kind: {
  [kind: string]: {
    title: string
    component: any
  }
} = {
  layout: {
    title: 'Where is the text?',
    component: <BoxAnnotator service={new GeneralResource('layout_captcha')} />,
  },
}

export const Captcha = () => {
  let [open, setOpen] = useState(false)
  let [kind, setKind] = useState('layout')
  return (
    <div>
        <Button onClick={() => setOpen(true)}>Captcha</Button>
      <BootstrapDialog
        aria-labelledby="customized-dialog-title"
        open={open}
        fullWidth
        maxWidth={'xl'}
        style={{ marginRight: '30%', marginBottom: '30%' }}
        onClick={(e) => {
          e.preventDefault()
          e.stopPropagation()
          console.log('stop it!')
        }}>
        <BootstrapDialogTitle onClose={() => console.log('Closing dialogue')}>
          {Kind[kind].title}
        </BootstrapDialogTitle>
        <DialogContent dividers>{Kind[kind].component}</DialogContent>
        <Button variant="outlined" onClick={() => setOpen(false)}>
          Solved
        </Button>
      </BootstrapDialog>
    </div>
  )
}
