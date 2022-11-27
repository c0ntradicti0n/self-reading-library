import React from 'react'

import Search from 'antd/lib/input/Search'
import Router from 'next/router'
import { ClickBoundary } from './ClickBoundary'

export default class Url2Difference extends React.Component {
   render() {
      return (
         <ClickBoundary>
            <Search
               onSearch={(search) =>
                  Router.push('/difference?id=' + search).then(() =>
                     Router.reload(),
                  )
               }
               name="id"
               placeholder="Put URL to be scanned as document"
            />
         </ClickBoundary>
      )
   }
}
