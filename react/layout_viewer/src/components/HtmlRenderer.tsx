import React, { useContext, useEffect, useState } from 'react'
import Resource from '../resources/Resource'
import { ThreeCircles, Triangle } from 'react-loader-spinner'
import SelectText from './SelectText'
import { AppSettings } from '../../config/connection'
import Difference_AnnotationService from '../resources/Difference_AnnotationService'
import { httpGet } from '../helpers/httpGet'
import { DocumentContext } from '../contexts/DocumentContext.tsx'
import { Slot } from '../contexts/SLOTS'

interface Props {
  service: Resource<any>
  slot: Slot
}

const HtmlRenderer = (props: Props) => {
  const [htmlContent, setHtmlContent] = useState<string>('')
  const [difference_AnnotationService] = useState<Difference_AnnotationService>(
    new Difference_AnnotationService()
  )
  difference_AnnotationService.setSlot(props.slot)

  const context = useContext<DocumentContext>(DocumentContext)
  useEffect(() => {
    if (context.value[props.slot] && !context.value[props.slot].includes('http')) {
      console.log('fetching static html', context.value[props.slot])
      setHtmlContent(
        httpGet(
          AppSettings.FRONTEND_HOST +
            '/' +
            context.value[props.slot].replace('.layouteagle/', '') +
            '.html'
        )
      )
    }
  }, [context.value[props.slot]])

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
          {context.meta[props.slot] ? (
            <style
              dangerouslySetInnerHTML={{
                __html:
                  context.meta[props.slot].css +
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
