import React, { version } from 'react'
import App from 'next/app'
import * as glob from 'glob'
import 'antd/dist/antd.css'
import '../src/App.css'

import NoSSR from '../src/components/NoSSR'
import { AppWrapper } from '../src/contexts/DocumentContext.tsx'
import { ContextWrapper } from '../src/contexts/ContextContext'

import Navigation from '../src/components/Navigation'
import { NORMAL } from '../src/contexts/SLOTS'

console.log(version)

class MyApp extends App {
  static async getInitialProps(appContext) {
    if (process.browser) {
      return __NEXT_DATA__.props.pageProps
    }
    console.log('apps get initial props is run...')
    const pages = glob
      .sync('pages/**/*', { cwd: './' })
      .map((path) => path.match('pages\\/(.+)..sx?')[1])
      .filter((fname) => !fname.startsWith('_'))

    // calls page's `getInitialProps` and fills `appProps.pageProps`
    const appProps = await App.getInitialProps(appContext)
    return { pageProps: { pages } }
  }

  render() {
    const { Component, appProps } = this.props
    // Workaround for https://github.com/zeit/next.js/issues/8592

    return (
      <div id="comp-wrapp">
        <NoSSR>
          <ContextWrapper>
            <AppWrapper>
              <Navigation slot={NORMAL} />
              <Component {...this.props.pageProps} slot={NORMAL} />
            </AppWrapper>
          </ContextWrapper>
        </NoSSR>
      </div>
    )
  }
}

export default MyApp
