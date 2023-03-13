import React, { useContext, useEffect, useState } from 'react'
import Resource from '../resources/Resource'
import SelectText from './SelectText'
import Difference_AnnotationService from '../resources/Difference_AnnotationService'
import { httpGet } from '../helpers/httpGet'
import { DocumentContext } from '../contexts/DocumentContext.tsx'
import { Slot } from '../contexts/SLOTS'
import { AnnotationModal } from './AnnotationSpan'
import { FRONTEND_HOST } from '../../config/connection'
import Captcha from './Captcha'
import { Spin } from 'antd'

interface Props {
   service: Resource
   slot: Slot
}

const HtmlRenderer = (props: Props) => {
   const context = useContext<DocumentContext>(DocumentContext)

   const [htmlContent, setHtmlContent] = useState('')
   const [loading, setLoading] = useState(false)

   const [difference_AnnotationService] =
      useState<Difference_AnnotationService>(new Difference_AnnotationService())
   difference_AnnotationService.setSlot(props.slot)

   useEffect(() => {
      if (
         context.value[props.slot] &&
         !context.value[props.slot].includes('http')
      ) {
         httpGet(
            FRONTEND_HOST +
               '/' +
               context.value[props.slot].replace('.layouteagle', '') +
               '.html',
            setHtmlContent,
         )
         setLoading(false)
      } else {
         setLoading(true)
      }
   }, [context.value[props.slot]])

   return (
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
                  aria-description="Read the text and get the differences"
                  aria-multiline={`
               Differences are the building blocks of theories and for 
               you as the reader who wants that theory out of the text, this may be 
               the most important stuff. Because the mind will connect those oppositions
               of A vs B to a network and so you can infere from one difference to another
               and cook down your decisions to simple semaphores. 
               
               The markup should match the phrases where 'differences' are explained. 
               But the markup is at the moment not always 'perfect', so we have built a way, 
               how to teach the machine. You can <b>select text</b>, just as you would copy the text
               and it will open a portal! `}
                  aria-atomic={'difference-select-text.png'}
                  aria-modal={'false'}
                  style={{
                     display: 'flex',
                     alignItems: 'center',
                     justifyContent: 'center',
                     padding: '9em',
                     height: '100vh',
                     margin: '40px',
                  }}
               >
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
                     <Captcha />
                  )}
                  {htmlContent ? (
                     <div
                        id={'html_content'}
                        style={{ marginTop: '0px !important' }}
                     >
                        {' '}
                        <div
                           dangerouslySetInnerHTML={{ __html: htmlContent }}
                        />{' '}
                     </div>
                  ) : (
                     <Spin />
                  )}
               </div>
            </>
         )}
      </SelectText>
   )
}

export default HtmlRenderer
