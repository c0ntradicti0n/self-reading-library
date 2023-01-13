import React from 'react'
import styled from 'styled-components'

import Url2Difference from '../src/components/Url2Difference'
import { Card, Col, Row } from 'antd'

const Item = ({ children }) => (
   <Col flex="1 0 25%">
      <Card style={{ margin: 10, height: '200px' }}> {children} </Card>
   </Col>
)

const Index = () => {
   return (
      <Row className="row">
         <Item>
            <a href="/knowledge">Browse differences</a>
         </Item>
         <Item>
            <a href="/library">Universe of documents</a>
         </Item>

         <Item>
            Browse a page with annotation
            <br />
            <Url2Difference />
         </Item>
         <Item>
            Some source of papers
            <br />
            <a href={'http://arxiv.org'}>http://arxiv.org</a>
         </Item>
         <Item>
            {' '}
            <a href="https://plato.stanford.edu/entries/categories/">
               https://plato.stanford.edu/entries/categories/
            </a>
         </Item>
         <Item>
            Some other websites featuring <i> differences </i>
            <ul>
               <li>
                  <a
                     href={'http://www.differencebetween.net/'}
                     target="_blank"
                     rel="noopener noreferrer"
                  >
                     http://www.differencebetween.net/
                  </a>
               </li>
               <li>
                  <a
                     href={'http://www.differencebetween.com/'}
                     target="_blank"
                     rel="noopener noreferrer"
                  >
                     http://www.differencebetween.com/
                  </a>
               </li>
            </ul>
         </Item>
      </Row>
   )
}

export default Index
