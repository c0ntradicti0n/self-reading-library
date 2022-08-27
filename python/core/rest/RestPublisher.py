import itertools
import logging
import os

from core.rest.Resource import Resource
from core.rest.react import react
from core.pathant.PathAnt import PathAnt
from core.pathant.PathSpec import PathSpec

from flask import jsonify, Blueprint

bp = Blueprint('blueprint', __name__, template_folder='templates')


class RestPublisher(PathSpec, react):
    def __call__(self, pipeline, arg):
        if not isinstance(arg[0], list) and not len(arg[0]) == 2:
            arg = [(a, {}) for a in arg]
        return list(
            zip(
                *list(pipeline(list(arg)))))

    # deliver paths
    def on_post(self, *args, **kwargs):  # get one
        print(args, kwargs)

        source_node, what_to_put_first = self.answer_or_ask_neighbors(None)
        self.ant(source_node, self, what_to_put_first)

        self.logger.error("rest call on abstract publisher!")
        return jsonify(meta=self.meta), 200

    def on_get(self, *args, **kwargs):  # get all
        print(args, kwargs)
        self.logger.error("rest call on abstract publisher!")
        return jsonify(meta=self.meta), 400

    # get html
    def on_post(self, i):

        self.logger.error("rest call on abstract publisher!")
        return jsonify(page=self.data[i]), 200

    # upload
    def on_put(self, file, meta_data):

        self.logger.error("rest call on abstract publisher!")
        with open(self.upload_docs + self.new_path(), "w") as f:
            f.write(file)

    # correction
    def on_patch(self, text, location, annotation):

        self.logger.error("rest call on abstract publisher!")
        with open(self.upload_docs + self.new_annotation(), "w") as f:
            raise NotImplementedError()

    # hide... or delete all mentioned paths
    def on_delete(self, i):
        self.data.pop(i)
        self.meta.pop(i)
        self.logger.error("rest call on abstract publisher!")

    def __init__(self,
                 *args,
                 port=7770,
                 url="localhost",
                 resource: Resource = None,
                 **kwargs):

        try:
            react.__init__(self, *args, **kwargs)
        except:
            logging.error("Could not create react app", exc_info=True)
        PathSpec.__init__(self, *args, **kwargs)
        assert resource and isinstance(resource, Resource)
        self.url = url
        self.port = port
        self.resource = resource
        self.contents = []
        self.logger.warning(f"REST-publishing {self.resource.title}")

        try:
            with open("/".join([self.npm_resources, self.resource.Title + "Service.ts"]), "w") as f:
                f.write(
                    self.server_resource_code.format(**self.resource, port=self.port, url=self.url, **self.resource.access))
        except:
            logging.error(f"Could not create javascript resource file {self.resource.Title}", exc_info=True)

        try:
            with open("/".join([self.npm_pages, self.resource.title + ".tsx"]), "w") as f:
                f.write(self.page_code.format(**self.resource, port=self.port, url=self.url, **self.resource.access))
        except:
            logging.error(f"Could not write {self.resource.title}.tsx", exc_info=True)


    def __iter__(self, incoming):
        if not self.contents:
            self.contents = list(incoming)

    server_resource_code = \
        """
import ServerResource from './GeneralResource'


export default class ??Title!!Service extends ServerResource<any> {
    constructor () {
        super(
         '/??title!!', 
         ??access[fetch]!!, 
         ??access[read]!!, 
         ??access[upload]!!,
         ??access[correct]!!,
         ??access[delete]!!,
         ??access[add_id]!!
        )
    }
}

""".replace("{", "{{").replace("}", "}}").replace("??", r"{").replace("!!", "}")

    page_code = """
import React, {useContext, useEffect, useState} from 'react'
import {withRouter} from 'next/router'
import ??Title!!Service from '../src/resources/??Title!!Service'
import HtmlRenderer from './../src/components/HtmlRenderer'
import BoxAnnotator from './../src/components/BoxAnnotator'
import DownloadFile from './../src/components/DownloadFile'
import {DocumentContext, DocumentContextType} from "../src/contexts/DocumentContext.tsx";

import dynamic from 'next/dynamic'


const Graph = dynamic(
    () => import('./../src/components/Graph.js'),
    {
        loading: () => <p>...</p>,
        ssr: false
    }
)

interface Props {
    router?: any
}

const ??Title!! = (props: Props) => {
    const context = useContext<DocumentContextType>(DocumentContext)
    const component = "??type!!"
    const service = new ??Title!!Service()
    useEffect(
        () => {
            let service = new ??Title!!Service()
            console.log("get " + props.router.query.id)
            if (props.router.query.id) {
                console.log("query", props.router.query)
                service.fetch_one(props.router.query.id, context?.setValueMetas)
            } else {
                service.fetch_all(context?.value, context?.setValueMetas)
            }
        }, [])
    console.log("Created component", component, context)

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
        return <HtmlRenderer service={??Title!!Service}  />
    
    else return null

}

    
    
export default withRouter(??Title!!)    
    """ \
        .replace("{", "{{") \
        .replace("}", "}}") \
        .replace("??", r"{") \
        .replace("!!", "}")

    components = {
        "??Title!!Container": """
        ??access[fetch]!!Container extends TemplateContainer {
            
        }
        """.replace("{", "{{").replace("}", "}}").replace("??", r"{").replace("!!", "}"),
        "??resource!!Fetch": """
    ??access[fetch]!!Container extends TemplateContainer {

    }
    """.replace("{", "{{").replace("}", "}}").replace("??", r"{").replace("!!", "}")
    }

import unittest


class TestPaperPublisher(unittest.TestCase):

    def setUp(self):
        self.ant = PathAnt()
        self.model_pipe = self.ant(itertools.cycle(["arxiv.org"]), "keras")
        self.prediction_pipe = self.ant("pdf", "latex.html")

    def test_make_model(self):
        model_pipe = self.ant(itertools.cycle(["arxiv.org"]), "keras")
        print(list(model_pipe("https://arxiv.org")))

    def test_rest(self):
        os.system(" git clone https://github.com/matt-sm/create-react-flask.git ")
        model_pipe = self.ant(itertools.cycle(["arxiv.org"]), "keras")


if __name__ == '__main__':
    unittest.main()
