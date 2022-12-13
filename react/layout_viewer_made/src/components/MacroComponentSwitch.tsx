import React, { forwardRef, useContext, useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import HtmlRenderer from './HtmlRenderer'
import AnnotationBox from './AnnotationBox'
import DownloadFile from './DownloadFile'
import {
   DocumentContext,
   DocumentContextType,
} from '../contexts/DocumentContext.tsx'
import dynamic from 'next/dynamic'
import Resource from '../resources/Resource'
import {CAPTCHA, NORMAL, Slot} from '../contexts/SLOTS'
import AnnotationSpan from './AnnotationSpan'
import { Knowledge } from './Knowledge'
import boolean from 'async-validator/dist-types/validator/boolean'
import Captcha from './Captcha'
import CirclePack from './2DCirclePack'

interface Props {
   component: string
   url: string
   value?: string
   slot?: Slot
   input?: any
}

const MacroComponentSwitch = forwardRef(
   ({ slot = NORMAL, ...props }: Props, ref): JSX.Element => {
      const Graph = dynamic(async () => await import('./Graph.js'), {
         loading: () => <p>...</p>,
         ssr: false,
      })
      const router = useRouter()
      const context = useContext<DocumentContextType>(DocumentContext)
      const [loading, setLoading] = useState(false)

      const component = props.component
      const service = new Resource(props.url, true, true, true, true, true)
      service.setSlot(slot)
      console.debug('MacroComponentSwitch', props, slot)
      useEffect(() => {
         const valueToFetch =
            props.value ?? (slot === NORMAL ? router.query.id : null)

         if (!props.input) {
            setLoading(true)
            service
               .getOne(
                  valueToFetch,
                  (val) => {
                     setLoading(false)
                     context?.setValueMetas(slot, val)
                  },
                  null,
               )
               .catch((e) => console.error('fetching ', e))
         } else context?.setValueMetas(slot, props.input)
      }, [])

      console.debug(context, props)
      if (loading && !slot === CAPTCHA) {
         console.log('Display captcha, load is taking some time')
         return <Captcha is_open={true}/>
      }
      if (!context.value[slot]) return null

      if (['upload_annotation', 'annotation'].includes(component)) {
         return <AnnotationBox ref={ref} service={service} slot={slot} />
      }

      if (['span_annotation'].includes(component)) {
         return <AnnotationSpan ref={ref} service={service} slot={slot} />
      }

      if (component === 'download') {
         return <DownloadFile data={context.value[slot]} />
      }

      if (component === 'knowledge') {
         return <Knowledge service={service} slot={slot} />
      }

      if (component === 'text') {
         return (
            <pre>
               {JSON.stringify(
                  {
                     value: context.value[slot],
                     meta: context.meta[slot],
                  },
                  null,
                  2,
               )}
            </pre>
         )
      }

      if (component === 'graph' && context.meta['normal'])
         return <CirclePack data={context.meta['normal']} />

      if (component === 'html')
         return <HtmlRenderer service={service} slot={slot} />
      else return <p>Component not found</p>
   },
)

export default MacroComponentSwitch
