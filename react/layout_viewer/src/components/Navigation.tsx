import React, { useContext } from 'react'
import Button from '@mui/material/Button'
import Router from 'next/router'
import Url2Difference from './Url2Difference'
import Audiobook from './Audiobook'

import styled from 'styled-components'
import { DocumentContext } from '../contexts/DocumentContext.tsx'
import { Captcha } from './Captcha'

const NavigationDiv = styled.div`
  position: fixed;
  margin-left: 70%;
  margin-right: 0;
  align: left;
  background: #fff !important;
  width: 17%;
  column-count: 1;
  flex-flow: column wrap;
  padding: 3%;
  z-index: 10000;
`

const Navigation = () => {
  const context = useContext<DocumentContext>(DocumentContext)
  const id = context.value
  const shortId = id?.replace('.layouteagle/', '')
  return (
    <NavigationDiv>
      <div>
        <Button
          style={{ marginLeft: '3vw' }}
          href="https://self-reading-library.science">
          <img
            style={{ width: '5vw', borderRadius: '60px' }}
            src="/react/layout_viewer/public/logo.jpeg"
            alt={'Logo'}
          />
        </Button>
      </div>
      <div>
        <Button href="/library">Universe of documents</Button>
      </div>

      <h3>Interactive formats</h3>
      <div>
        <Button href={'/difference?id=' + id}>Read annotated paper</Button>
      </div>
      <div>
        <Audiobook />
      </div>
      <div>
        <Button href={shortId}>Original PDF</Button>
      </div>
      <div>
        <Button href={'/upload_annotation?id=' + id}>
          Improve layout recognition
        </Button>
      </div>

      <h3>Navigate to other document</h3>

      <h5>Captcha game</h5>


      <div>
        <Captcha />
      </div>
      <h5>Read custom page here, paste URL</h5>

      <div>
        <Url2Difference />
      </div>

      <h5>Upload your own document</h5>
      <div>
        <form
          onSubmit={(e) => {
            console.log(e)
            Router.push({
                pathname: '/difference/',
                query: {id: (e.target as HTMLTextAreaElement).value},
            })
          }}>
          <input type="file" id="myfile" name="myfile" />
        </form>
      </div>
      <h3>Navigationigate to 3D-Library</h3>

      <div>
        <Button href={'/library'}>Library</Button>
      </div>
    </NavigationDiv>
  )
}

export default Navigation
