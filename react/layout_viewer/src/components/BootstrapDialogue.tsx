import { styled as sty } from '@mui/material/styles'
import Dialog from '@mui/material/Dialog'

export const BootstrapDialog = sty(Dialog)(({ theme }) => ({
  '& .MuiDialogContent-root': {
    padding: theme.spacing(2),
    maxWidth: '90%',
    minHeight: '90vh',

    overflow: 'auto',
    wordWrap: 'normal',
    display: 'flex',
    flex: '1 1 auto',
    flexWrap: 'wrap',
  },
  '& .MuiDialogActions-root': {
    padding: theme.spacing(1),
  },
}))
