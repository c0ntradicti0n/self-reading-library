import React, {useContext, useEffect} from 'react'
import {withRouter} from 'next/router'
import HtmlRenderer from './HtmlRenderer'
import BoxAnnotator from './BoxAnnotator'
import DownloadFile from './DownloadFile'
import {DocumentContext, DocumentContextType} from "../contexts/DocumentContext.tsx";
import dynamic from 'next/dynamic'
import ServerResource from "../resources/GeneralResource";


const Graph = dynamic(
    () => import('./Graph.js'),
    {
        loading: () => <p>...</p>,
        ssr: false
    }
)

interface Props {
    router?: any
    component: string,
    url: string
}

const MacroComponentSwitch = (props: Props) => {
    const context = useContext<DocumentContextType>(DocumentContext)
    const component = props.component
    const service = new ServerResource(props.url, true, true, true, true, true, false)

    useEffect(
        () => {
            if (props.router.query.id) {
                service.fetch_one(props.router.query.id, context?.setValueMetas)
            } else {
                service.fetch_one("any", context?.setValueMetas)
            }
        }, [])

    if (!context.value)
        return null

    if (["upload_annotation", "annotation"].includes(component)) {
        return <BoxAnnotator
                service={service}
            />
    }

    // @ts-ignore
    if (component === "download") {
        return <DownloadFile data={context.value}/>
    }

    // @ts-ignore
    if (component === "text") {
        return JSON.stringify({value: context.value, meta: context.meta})
    }

    // @ts-ignore
    if (component === "graph" && state.value)
        return <Graph/>

    // @ts-ignore
    if (component === "html") 
        return <HtmlRenderer service={service}  />
    
    else return null
}

// @ts-ignore
export default withRouter(MacroComponentSwitch)
    