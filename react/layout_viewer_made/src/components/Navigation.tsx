import React, { useContext, useState } from 'react'
import Captcha from './Captcha'
import { NORMAL, Slot } from '../contexts/SLOTS'
import { Button, Menu, Popover } from 'antd'
import Audiobook from './Audiobook'
import Url2Difference from './Url2Difference'
import UploadDocument from './Upload'
import {
   GlobalOutlined,
   QuestionCircleOutlined,
   RadarChartOutlined,
   RocketOutlined,
   SearchOutlined,
   SmileOutlined,
   SoundOutlined,
   UploadOutlined,
} from '@ant-design/icons'
import { Help } from './Tour'
import { DocumentContext } from '../contexts/DocumentContext.tsx'
import { useRouter } from 'next/router'
function getItem(label, key, icon, children = undefined) {
   return {
      key,
      icon,
      children,
      label,
   }
}

const NavigationContent = () => {
   const [open, setOpen] = useState(false)
   const context = useContext<DocumentContext>(DocumentContext)
   console.log(context)
   const items = [
      getItem(
         <Button type="link" href="/knowledge">
            Browse differences
         </Button>,
         'link1',
         <RadarChartOutlined />,
      ),
      getItem(
         <Button type="link" href="/library">
            Universe of documents
         </Button>,
         'link2',
         <GlobalOutlined />,
      ),
      getItem(<Captcha is_open={false} />, 'link3', <SmileOutlined />),
      getItem(<Url2Difference />, 'link4', <SearchOutlined />),
      getItem(<UploadDocument />, 'link5', <RocketOutlined />),
      context.value[NORMAL]?.endsWith('pdf')
         ? getItem(<Audiobook />, 'link6', <SoundOutlined />)
         : null,
      getItem(
         <>
            {context.value[NORMAL]?.end}{' '}
            {open ? <Help open={open} setOpen={setOpen} /> : null}
            <Button type="link" onClick={() => setOpen(!open)}>
               Help me!
            </Button>
         </>,
         'link8',
         <QuestionCircleOutlined />,
      ),
   ].filter((x) => x)
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
