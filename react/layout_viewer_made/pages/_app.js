import React, {useState} from "react";
import "../src/App.css";

import NoSSR from "../src/components/NoSSR";
import { AppWrapper } from "../src/contexts/DocumentContext.tsx";
import { ContextWrapper } from "../src/contexts/ContextContext";

import Navigation from "../src/components/Navigation";
import {TourButton} from "../src/components/Tour";

import { NORMAL } from "../src/contexts/SLOTS";
import {ConfigProvider, Divider, Layout, Space, theme} from "antd";



const MyApp = ({Component}) => {
      const [collapsed, setCollapsed] = useState(false);
      const { Sider, Content } = Layout;

    return (
      <Layout
            style={{
        minHeight: '100vh',
      }}>
        <NoSSR>
          <ConfigProvider
    theme={{
      algorithm: theme.defaultAlgorithm,
    }}
  >
          <ContextWrapper>
            <AppWrapper>
              <Sider
               width={250}
               collapsible collapsed={collapsed} onCollapse={(value) => setCollapsed(value)}>
                          <div
          style={{
            height: 32,
            margin: 16,
            background: 'rgba(255, 255, 255, 0.2)',
          }}
        ><img src='logo.jpg' style={{width:"100%"}}/>
                          </div>  {collapsed?null:<> <Divider/>           <Divider/>     <Divider/>     <Divider/>     <Divider/>   </> }  <Navigation slot={NORMAL} />
                </Sider>
                <Content>
              <Component slot={NORMAL} />
                    </Content>
            </AppWrapper>
          </ContextWrapper>
          </ConfigProvider>
        </NoSSR>
      </Layout>
    );

}

export default MyApp;
