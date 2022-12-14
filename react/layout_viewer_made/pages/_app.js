import React, { version } from "react";
import App from "next/app";
import * as glob from "glob";
import "../src/App.css";

import NoSSR from "../src/components/NoSSR";
import { AppWrapper } from "../src/contexts/DocumentContext.tsx";
import { ContextWrapper } from "../src/contexts/ContextContext";

import Navigation from "../src/components/Navigation";
import {TourButton} from "../src/components/Tour";

import { NORMAL } from "../src/contexts/SLOTS";
import {ConfigProvider, theme} from "antd";


class MyApp extends App {
  static async getInitialProps(appContext) {
    const appProps = await App.getInitialProps(appContext);
    return { pageProps: {  } , appProps};
  }

  render() {
    const { Component, appProps } = this.props;
    return (
      <div id="comp-wrapp">
        <NoSSR>
          <ConfigProvider
    theme={{
      algorithm: theme.defaultAlgorithm,
    }}
  >
          <ContextWrapper>
            <AppWrapper>
              <Navigation slot={NORMAL} />
              <TourButton />
              <Component {...this.props.pageProps} slot={NORMAL} />
            </AppWrapper>
          </ContextWrapper>
          </ConfigProvider>
        </NoSSR>
      </div>
    );
  }
}

export default MyApp;
