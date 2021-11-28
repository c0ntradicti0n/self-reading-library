import React from 'react'
import Layout from '../components/Layout'



export default  class Index extends React.Component  {
    render () {
        return (
            <Layout title="Home" pages={this.props.pages}>
                <h1>Hello Next.js 👋</h1>
            </Layout>
        )
    }
}
