import React from 'react'

import Search from 'antd/lib/input/Search'
import Router from 'next/router'
import { ClickBoundary } from './ClickBoundary'

const Url2Difference = () => {
   return (
      <ClickBoundary>
         <Search
            onSearch={(search) => {
               Router.push('/difference?id=' + search).then(() =>
                  Router.reload(),
               )
            }}
            name="id"
            placeholder="Put URL to be scanned as document"
         />
      </ClickBoundary>
   )
}

export default Url2Difference
