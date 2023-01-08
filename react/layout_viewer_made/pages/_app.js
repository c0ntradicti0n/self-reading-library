import React, { useEffect, useState } from 'react'
import '../src/App.css'

import NoSSR from '../src/components/NoSSR'
import { AppWrapper } from '../src/contexts/DocumentContext.tsx'
import { ContextWrapper } from '../src/contexts/ContextContext'

import Navigation from '../src/components/Navigation'
import { TourButton } from '../src/components/Tour'

import { NORMAL } from '../src/contexts/SLOTS'
import { ConfigProvider, Divider, Layout, Space, theme } from 'antd'

const mobileAndTabletCheck = function () {
   var match = window.matchMedia || window.msMatchMedia
   if (match) {
      var mq = match('(pointer:coarse)')
      return mq.matches
   }
   return false
}
const MyApp = ({ Component }) => {
   const [collapsed, setCollapsed] = useState(true)
   useEffect(() => {
      setMobile(mobileAndTabletCheck())
      setCollapsed(mobileAndTabletCheck())
   }, [])
   const [mobile, setMobile] = useState()
   const { Sider, Content } = Layout

   return (
      <Layout
         style={{
            minHeight: '100vh',
         }}
      >
         <NoSSR>
            <ConfigProvider
               theme={{
                  algorithm: theme.defaultAlgorithm,
               }}
            >
               <ContextWrapper>
                  <AppWrapper>
                     <Layout>
                        <Sider
                           width={300}
                           collapsible
                           collapsed={collapsed}
                           onCollapse={(value) => setCollapsed(value)}
                        >
                           <div
                              style={{
                                 height: 32,
                                 margin: 16,
                                 background: 'rgba(255, 255, 255, 0.2)',
                              }}
                           >
                              <img src="logo.jpg" style={{ width: '50px' }} />
                           </div>

                           {!mobile ? (
                              <>
                                 {' '}
                                 <Divider /> <Divider /> <Divider /> <Divider />{' '}
                                 <Divider /> <Divider />{' '}
                              </>
                           ) : null}

                           <Navigation />
                        </Sider>

                        <Content
                           style={{ marginLeft: collapsed ? '50px' : '300px' }}
                        >
                           <Component slot={NORMAL} />
                        </Content>
                     </Layout>
                  </AppWrapper>
               </ContextWrapper>
            </ConfigProvider>
         </NoSSR>
      </Layout>
   )
}

export default MyApp
