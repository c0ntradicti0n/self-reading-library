import { Button, Tour } from 'antd'
import React, { useState } from 'react'

function isVisible(e) {
   return true // e.offsetWidth > 0 && e.offsetHeight > 0
}
const Help = ({
   open,
   setOpen,
}: {
   open: boolean
   setOpen: (boolean) => void
}) => {
   let steps = [...document.querySelectorAll('[aria-description]')].map(
      (el) => {
         return {
            title: el.attributes['aria-description'].value,
            modal: el.attributes['aria-modal']?.value,

            description: el.attributes['aria-multiline']?.value
               ? el.attributes['aria-multiline'].value
               : undefined,
            cover: el.ariaAtomic ? <img src={el.ariaAtomic} /> : undefined,
            target: () => el,
         }
      },
   )
   const hasModal = steps.some((s) => s.modal)
   const hasNotModal = steps.some((s) => !s.modal)

   if (hasModal && hasNotModal) steps = steps.filter((s) => !s.modal)
   return <Tour open={open} onClose={() => setOpen(false)} steps={steps} />
}

const TourButton = () => {
   const [open, setOpen] = useState(false)

   return (
      <>
         {' '}
         {open ? <Help open={open} setOpen={setOpen} /> : null}
         <Button onClick={() => setOpen(!open)}>?</Button>
      </>
   )
}
export { Help, TourButton }
