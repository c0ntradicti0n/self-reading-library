import React, { useContext, useEffect } from 'react'
import { useRouter } from 'next/router'
import HtmlRenderer from './HtmlRenderer'
import BoxAnnotator from './BoxAnnotator'
import DownloadFile from './DownloadFile'
import {
  DocumentContext,
  DocumentContextType,
} from '../contexts/DocumentContext.tsx'
import dynamic from 'next/dynamic'
import Resource from '../resources/Resource'
import { NORMAL, Slot } from '../contexts/SLOTS'

const Graph = dynamic(async () => await import('./Graph.js'), {
  loading: () => <p>...</p>,
  ssr: false,
})

interface Props {
  component: string
  url: string
  value?: string
  slot: Slot
  input?: any
}

const MacroComponentSwitch = ({
  slot = NORMAL,
  ...props
}: Props): JSX.Element => {
  const router = useRouter()
  const context = useContext<DocumentContextType>(DocumentContext)

  const component = props.component
  const service = new Resource(props.url, true, true, true, true, true)
  service.setSlot(slot)
  console.log('MacroComponentSwitch', props, slot)
  useEffect(() => {
    const valueToFetch =
      props.value ?? (slot === NORMAL ? router.query.id : null)

    if (!props.input)
      service
        .fetch_one(valueToFetch, (val) => context?.setValueMetas(slot, val))
        .catch((e) => console.error('fetching ', e))
    else context?.setValueMetas(slot, props.input)
  }, [])

  console.log(context, props)
  if (!context.value[slot]) return null

  if (['upload_annotation', 'annotation'].includes(component)) {
    return <BoxAnnotator service={service} slot={slot} />
  }

  if (component === 'download') {
    return <DownloadFile data={context.value[slot]} />
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
          2
        )}
      </pre>
    )
  }

  if (component === 'graph' && context.meta['normal'])
    return <Graph data={context.meta['normal']} />

  if (component === 'html')
    return <HtmlRenderer service={service} slot={slot} />
  else return <p>Component not found</p>
}

export default MacroComponentSwitch
