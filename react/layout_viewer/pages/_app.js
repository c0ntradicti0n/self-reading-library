import React from 'react'
import App from 'next/app'
import * as glob from 'glob'
import '../src/App.css';
import NoSSR from "../components/NoSSR";


class MyApp extends App {
    // Only uncomment this method if you have blocking data requirements for
    // every single page in your application. This disables the ability to
    // perform automatic static optimization, causing every page in your app to
    // be server-side rendered.
    //
    static async getInitialProps(appContext) {
        if (process.browser) {
            return __NEXT_DATA__.props.pageProps;
        }
        console.log("apps get initial props is run...")
        let pages = glob.sync('pages/**/*', {cwd: "./"}).map(path => path.match("pages\\/(.+)\..sx?")[1]).filter(fname => !fname.startsWith("_"))


        // calls page's `getInitialProps` and fills `appProps.pageProps`
        const appProps = await App.getInitialProps(appContext);
        return {pageProps: {pages: pages}}
    }

    render() {
        const {Component, appProps} = this.props
        // Workaround for https://github.com/zeit/next.js/issues/8592

        return (
            <div id="comp-wrapp">
                <NoSSR>
                    <Component {...this.props.pageProps} />
                </NoSSR>
            </div>
        )
    }
}

export default MyApp