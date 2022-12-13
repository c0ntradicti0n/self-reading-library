import React, { useContext, useState } from 'react'
import { DocumentContext } from '../contexts/DocumentContext.tsx'
import Captcha from './Captcha'
import { Slot } from '../contexts/SLOTS'
import { Button, Popover } from 'antd'
import Audiobook from './Audiobook'
import Url2Difference from './Url2Difference'
import UploadDocument from './Upload'
import GoldenSnake from './GoldenSnake'

interface PropType {
   slot: Slot
   onClose: () => void
}

const NavigationContent = ({ slot, onClose }: PropType) => {
   const context = useContext<DocumentContext>(DocumentContext)
   const id = context.value[slot]
   const shortId = (id ?? '').replace('.layouteagle/', '')
   return (
      <GoldenSnake onClick={onClose}>
         <div>
            <a href="/library">Universe of documents</a>
         </div>
         <div>
            <a href={'/difference?id=' + id}>Read annotated paper</a>
         </div>
         <div>
            <a href={shortId}>Original PDF</a>
         </div>
         <div>
            <a href={'/upload_annotation?id=' + id}>
               Improve layout recognition
            </a>
         </div>
         <div>
            <Captcha is_open={false} />
         </div>
         <div>
            <Url2Difference />
         </div>
          <div><UploadDocument /></div>
                   <div>
            <Audiobook />
         </div>
      </GoldenSnake>
   )
}

const Navigation = (props: PropType) => {
   const [open, setOpen] = useState(false)

   return (
      <Popover
         content={
            <div>
               <NavigationContent {...props} onClose={() => setOpen(false)} />
            </div>
         }
         placement="rightBottom"
         title={
            <>
               Navigation <a onClick={() => setOpen(false)}>✕</a>
            </>
         }
         trigger="click"
         open={open}
      >
         <Button
             id={"nav"}
            style={{
               position: 'fixed',
               top: '0px',
               right: '0px',
                fontSize: "1.5rem"
            }}
            type="primary"
            onClick={() => setOpen(true)}
         >
            Menu
         </Button>
      </Popover>
   )
}
export default Navigation
