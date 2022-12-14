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
   let steps = [...document.querySelectorAll('[aria-description]')]
      .map((el) => {
         console.log(el.attributes["aria-description"].value, el)
         return {
            title: el.attributes["aria-description"].value,
            modal: el.attributes["aria-modal"]?.value,

            description: el.attributes["aria-multiline"]?.value ? el.attributes["aria-multiline"].value : undefined,
            cover: el.ariaAtomic ? <img src={el.ariaAtomic} /> : undefined,
            target: () => el,
         }
      })
    const hasModal = steps.some(s => s.modal)
        console.log(hasModal, steps)
    const hasNotModal = steps.some(s => !s.modal)
    console.log(hasModal, steps)

    if (hasModal && hasNotModal)
        steps = steps.filter(s => !s.modal)
   return <Tour placement={"leftTop"} open={open} onClose={() => setOpen(false)} steps={steps} />
}

const TourButton = () => {
   const [open, setOpen] = useState(false)

   return (
      <>
         {' '}
         {open ? <Help open={open} setOpen={setOpen} /> : null}
         <Button id={'tour'} type="primary" onClick={() => setOpen(!open)}>
            ?
         </Button>
      </>
   )
}
export { Help, TourButton }
