import React, { useContext, useEffect, useState } from 'react'
import ServerResource from '../resources/GeneralResource'
import { ThreeCircles, Triangle } from 'react-loader-spinner'
import SelectText from './SelectText'
import { AppSettings } from '../../config/connection'
import Difference_AnnotationService from '../resources/Difference_AnnotationService'
import { httpGet } from '../helpers/httpGet'
import { DocumentContext } from '../contexts/DocumentContext.tsx'

interface Props {
  service: ServerResource<any>
}

const HtmlRenderer = (props: Props) => {
  const [htmlContent, setHtmlContent] = useState<string>('')
  const [difference_AnnotationService] = useState<Difference_AnnotationService>(
    new Difference_AnnotationService()
  )

  const context = useContext<DocumentContext>(DocumentContext)
  console.log('CONTEXT', context)
  useEffect(() => {
    if (context.value && !context.value.includes('http')) {
      console.log('fetching static html', context.value)
      setHtmlContent(
        httpGet(
          AppSettings.FRONTEND_HOST +
            '/' +
            context.value.replace('.layouteagle/', '') +
            '.html'
        )
      )
    }
  }, [context.value])

  console.log('HtmlRenderer', context, props, 'ASDASDA')

  //       <Captcha />
  console.log(htmlContent, context.value)
  return (
    <div>
      <SelectText service={difference_AnnotationService}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '9em',
          }}>
          {context.meta ? (
            <style
              dangerouslySetInnerHTML={{
                __html:
                  context.meta.css +
                  `\n\n
                   #page-container { 
                   background-color: transparent !important;
                   background-image: none !important;
                   }`,
              }}
            />
          ) : (
            <ThreeCircles
              color="red"
              outerCircleColor="blue"
              middleCircleColor="green"
              innerCircleColor="grey"
            />
          )}
          {htmlContent ? (
            <div dangerouslySetInnerHTML={{ __html: htmlContent }} />
          ) : (
            <Triangle ariaLabel="loading-indicator" />
          )}
        </div>
      </SelectText>
    </div>
  )
}

export default HtmlRenderer
