import React from 'react';
import App from 'next/app';
import * as glob from 'glob';
import '../src/App.css';
import NoSSR from '../src/components/NoSSR';
import { AppWrapper } from '../src/contexts/DocumentContext.tsx';
import Navigation from '../src/components/Navigation';

import { version } from 'react';

console.log(version);

class MyApp extends App {
  static async getInitialProps(appContext) {
    if (process.browser) {
      return __NEXT_DATA__.props.pageProps;
    }
    console.log('apps get initial props is run...');
    let pages = glob
      .sync('pages/**/*', { cwd: './' })
      .map((path) => path.match('pages\\/(.+)..sx?')[1])
      .filter((fname) => !fname.startsWith('_'));

    // calls page's `getInitialProps` and fills `appProps.pageProps`
    const appProps = await App.getInitialProps(appContext);
    return { pageProps: { pages: pages } };
  }

  render() {
    const { Component, appProps } = this.props;
    // Workaround for https://github.com/zeit/next.js/issues/8592

    return (
      <div id="comp-wrapp">
        <NoSSR>
          <AppWrapper>
            <Navigation
              forward={() =>
                this.props.service.ok(null, '', {}, () =>
                  window.location.reload()
                )
              }
              goto={(form_data) =>
                this.props.service.fetch_one(form_data, () =>
                  console.log('will display content...')
                )
              }
              upload={(form_data) =>
                this.props.service.upload(new FormData(form_data), () =>
                  console.log('will display content...')
                )
              }
              data={this.props}
            />
            <Component {...this.props.pageProps} />
          </AppWrapper>
        </NoSSR>
      </div>
    );
  }
}

export default MyApp;
