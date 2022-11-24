import React, { useContext, useEffect, useState } from 'react'
import Resource from '../resources/Resource'
import { ThreeCircles, Triangle } from 'react-loader-spinner'
import SelectText from './SelectText'
import Difference_AnnotationService from '../resources/Difference_AnnotationService'
import { httpGet } from '../helpers/httpGet'
import { DocumentContext } from '../contexts/DocumentContext.tsx'
import { Slot } from '../contexts/SLOTS'
import { AnnotationModal } from './AnnotationSpan'
import { FRONTEND_HOST } from '../../config/connection'

interface Props {
  service: Resource
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
    if (
      context.value[props.slot] &&
      !context.value[props.slot].includes('http')
    ) {
      console.log(
        'fetching static html',
        FRONTEND_HOST,
        '/' + context.value[props.slot].replace('.layouteagle/', '') + '.html',
        context.value[props.slot]
      )
      httpGet(
        FRONTEND_HOST +
          '/' +
          context.value[props.slot].replace('.layouteagle', '') +
          '.html',
        setHtmlContent
      )
    }
  }, [context.value[props.slot]])

  return (
    <div>
      <SelectText>
        {(selected, setSelected) => (
          <>
            {selected ? (
              <AnnotationModal
                text={selected}
                onClose={() => setSelected(null)}
                service={difference_AnnotationService}
              />
            ) : null}
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
          </>
        )}
      </SelectText>
    </div>
  )
}

export default HtmlRenderer
