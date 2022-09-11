import React, {useContext, useEffect} from 'react'
import {useRouter, withRouter} from 'next/router'
import HtmlRenderer from './HtmlRenderer'
import BoxAnnotator from './BoxAnnotator'
import DownloadFile from './DownloadFile'
import {
    DocumentContext,
    DocumentContextType,
} from '../contexts/DocumentContext.tsx'
import dynamic from 'next/dynamic'
import Resource from '../resources/Resource'
import {NORMAL, Slot} from "../contexts/SLOTS";

const Graph = dynamic(() => import('./Graph.js'), {
    loading: () => <p>...</p>,
    ssr: false,
})

interface Props {
    component: string
    url: string
    value? : string
    slot: Slot
}

const MacroComponentSwitch = ({slot = NORMAL, ... props}: Props) => {
    const router = useRouter()
    const context = useContext<DocumentContextType>(DocumentContext)
    
    const component = props.component
    const service = new Resource(props.url, true, true, true, true, true, false)
    service.setSlot(slot)
    console.log ("MacroComponentSwitch", props, slot)
    useEffect(
        () => {
            const valueToFetch = props.value ?? (slot == NORMAL ? router.query.id : null) ;
            if (valueToFetch) {
                service.fetch_one(valueToFetch, (val) => context?.setValueMetas(slot, val))
            } else {
                service.fetch_one("any", (val) => context?.setValueMetas(slot, val))
            }
        }, [])

    console.log(context, props)
    if (!context.value[slot])
        return null

    if (["upload_annotation", "annotation"].includes(component)) {
        return <BoxAnnotator
            service={service} slot={slot}
        />
    }

    // @ts-ignore
    if (component === "download") {
        return <DownloadFile data={context.value[slot]} />
    }

    // @ts-ignore
    if (component === "text") {
        return JSON.stringify({value: context.value[slot], meta: context.meta[slot]})
    }

    // @ts-ignore
    if (component === "graph" && state.value)
        return <Graph/>

    // @ts-ignore
    if (component === "html")
        return <HtmlRenderer service={service} slot={slot}/>

    else return "Component not found"
}

// @ts-ignore
export default MacroComponentSwitch
    