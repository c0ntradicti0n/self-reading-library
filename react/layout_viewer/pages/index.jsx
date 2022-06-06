import React from 'react'
import Layout from '../components/Layout'
import styled from 'styled-components'

const H1 = styled.div`
  border: 2px solid palevioletred;
  align: right;
  font-size: 2em;
  margin: 2em;
  padding: 2em;
  text-transform: capitalize;
  display: flex; 
  justify-content: flex-end
`;


export default  class Index extends React.Component  {
    render () {
        return (
            <Layout title="Home" pages={this.props.pages}>
                <H1>self-reading library</H1>
            </Layout>
        )
    }
}
