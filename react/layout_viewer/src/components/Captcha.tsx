import Button from '@mui/material/Button'
import { BootstrapDialogTitle } from './BootstrapDialogueTitle'
import { DialogContent } from '@mui/material'
import { BootstrapDialog } from './BootstrapDialogue'
import {useContext, useState} from 'react'
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
  console.log("contextContext", contextContext)

  let [open, __setOpen] = useState(false)
  const setOpen = (o) => {
      console.log("setOpen", o)

    if (o)
      contextContext.setSlot("captcha")
    else
      contextContext.setSlot("normal")
    __setOpen(o)
  }

  let [kind, setKind] = useState('annotation')

  return (
    <div>
      <Button onClick={() => setOpen(true)}>Captcha</Button>
        {open ?
      <BootstrapDialog
        aria-labelledby="customized-dialog-title"
        open={open}
        fullWidth
        maxWidth={'xl'}
        sx={{ marginRight: '30%', marginBottom: '30%' , maxHeight: 'none !important'}}
        onClose={()=> setOpen(false)}
        onClick={(e) => {
          e.preventDefault()
          e.stopPropagation()
          console.log('stop it!')
        }}>



        <BootstrapDialogTitle onClose={() => console.log('Closing dialogue')}>
          {Kind[kind].title}
        </BootstrapDialogTitle>
        <DialogContent dividers>
          {
            <MacroComponentSwitch component={kind} url={Kind[kind].url} slot={CAPTCHA} value="new" />
            }
        </DialogContent>
        <Button variant="outlined" onClick={() => setOpen(false)}>
          Solved
        </Button>
      </BootstrapDialog> : null}
    </div>
  )
}

export default Captcha
