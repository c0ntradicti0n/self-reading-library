import React, { useState } from 'react'
import Captcha from './Captcha'
import { Slot } from '../contexts/SLOTS'
import { Button, Menu, Popover } from 'antd'
import Audiobook from './Audiobook'
import Url2Difference from './Url2Difference'
import UploadDocument from './Upload'
import {
   GlobalOutlined, QuestionCircleOutlined,
   RadarChartOutlined, RocketOutlined,
   SearchOutlined, SmileOutlined,
   SoundOutlined,
   UploadOutlined,
} from '@ant-design/icons'
import {Help} from "./Tour";
function getItem(label, key, icon, children=undefined) {
   return {
      key,
      icon,
      children,
      label,
   }
}
interface PropType {
   slot: Slot
   onClose: () => void
}

const NavigationContent = ({ slot, onClose }: PropType) => {
      const [open, setOpen] = useState(false)

   const items = [
      getItem(
         <a href="/knowledge">Browse differences</a>,
         'link1',
         <RadarChartOutlined />,
      ),
      getItem(
         <a href="/library">Universe of documents</a>,
         'link2',
         <GlobalOutlined />,
      ),
      getItem(<Captcha is_open={false} />, 'link3', <SmileOutlined />),
      getItem(<Url2Difference />, 'link4', <SearchOutlined />),
      getItem(<UploadDocument />, 'link5', <RocketOutlined />),
      getItem(<Audiobook />, 'a', <SoundOutlined />),
       getItem(        <>
         {' '}
         {open ? <Help open={open} setOpen={setOpen} /> : null}
         <Button onClick={() => setOpen(!open)}>?</Button>
      </>, "help", <QuestionCircleOutlined />
)
   ]
   return (
      <Menu
         theme="dark"
         defaultSelectedKeys={['1']}
         mode="inline"
         items={items}
      />
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
         placement="right"
         title={
            <>
               Navigation <a onClick={() => setOpen(false)}>✕</a>
            </>
         }
         trigger="click"
         open={open}
      >
         <Button
            id={'nav'}
            style={{
               position: 'fixed',
               fontSize: '1.5rem',
            }}
            type="primary"
            onClick={() => setOpen(true)}
         >
            Menu
         </Button>
      </Popover>
   )
}
export default NavigationContent
