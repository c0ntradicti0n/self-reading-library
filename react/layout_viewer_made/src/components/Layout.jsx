import * as React from 'react'
import Head from 'next/head'
import { useRouter } from 'next/router'

const Layout = () => {
   const router = useRouter()

   const title = ['Difference network', router.pathname]
      .filter((x) => x)
      .join(' - ')

   return (
      <>
         <Head>
            <title>{title}</title>
            <meta charSet="utf-8" />
            <meta
               name="viewport"
               content="initial-scale=1.0, width=device-width"
            />
            <link rel="icon" href="/react/layout_viewer/public/favicon.ico" />
         </Head>
      </>
   )
}
export default Layout
