import React from 'react'

import Search from 'antd/lib/input/Search'
import Router from 'next/router'

export default class Url2Difference extends React.Component {
  render() {
    return (
      <Search
        onSearch={(esearch) => Router.push('/difference?id=' + esearch)}
        name="id"
        placeholder="Put URL to be scanned as document"
      />
    )
  }
}
