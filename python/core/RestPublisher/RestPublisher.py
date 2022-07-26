import logging
import os

from core.RestPublisher.Resource import Resource
from core.RestPublisher.react import react
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
        self.logger.warning("publishing")

        self.logger.warning(f"Creating service for {self.resource.title}")

        try:
            with open("/".join([self.npm_resources, self.resource.Title + "Service.ts"]), "w") as f:
                f.write(
                    self.server_resource_code.format(**self.resource, port=self.port, url=self.url, **self.resource.access))
        except:
            logging.error(f"Could not create javascript resource file {self.resource.Title}")
        self.logger.warning(f"Creating components for {self.resource.title}")

        self.write_components("/".join([self.npm_components, self.resource.title + ".tsx"]))

        self.logger.warning(f"Creating model object for {self.resource.Title}")

        self.logger.warning(f"Creating page for {self.resource.title}")

        try:
            with open("/".join([self.npm_pages, self.resource.title + ".tsx"]), "w") as f:
                f.write(self.page_code.format(**self.resource, port=self.port, url=self.url, **self.resource.access))
        except:
            logging.error(f"Could not write {self.resource.title}.tsx")
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
import React from 'react'
import Router from 'next/router'
import { withRouter } from "next/router";
import ??title!!Service from '../resources/??Title!!Service'
import HtmlRenderer from './../components/HtmlRenderer'
import BoxAnnotator from './../components/BoxAnnotator'
import DownloadFile from './../components/DownloadFile'

import dynamic from 'next/dynamic'
const Graph = dynamic(
    () => import('./../components/Graph.js'),
    {
        loading: () => <p>...</p>,
        ssr: false
    }
)

interface ??Title!!State {
    ??title!!: any
    ??title!!s: any
    meta: any
    value: any
}

interface ??Title!!Props {
    router?: any
}

class ??title!! extends React.Component<??Title!!Props, ??Title!!State> {
    ??title!!Service : ??title!!Service
   
    constructor (props)  {
        super(props)
        this.??title!!Service = new ??title!!Service()

        this.state = {
            ??title!!: null,
            ??title!!s: null,
            meta: null,
            value: null
        }
        
        if (this.props.router.query.id) {
            console.log("query", this.props.router.query)
        // @ts-ignore
            this.??title!!Service.fetch_one(this.props.router.query.id, this.set_??title!!s)
        }
        
        else {    
        // @ts-ignore
            this.??title!!Service.fetch_all(this.set_??title!!s)
        }
    }
    
    set_??title!!s = async (v) => {
        const prom = await v

        console.log('Setting values', prom.response, prom)
        
        
        const [value, meta] = prom
        console.log (value, meta)
        
        this.setState({
            ??title!!s: prom.response,
            value,
            meta    
            })
    }
    
    set_??title!! = async (v) => {
        
        if (v instanceof Promise) {
            await v.then(prom => {
                console.log('Set value', prom.response)
    
                this.setState({
                    ??title!!: prom.response}
                )
            })
        } else {
            this.setState({
                ??title!!: v}
            )
        }
    }
    
    render ()  {
        console.log("Created component", this, "??type!!" )
        
        if (["upload_annotation", "annotation"].includes("??type!!") )  {
            return (<>
                <BoxAnnotator 
                    superState={this.state} 
                    service={this.??title!!Service}
                    setFullState={this.set_??title!!s}
                />
            </>)
        }
        
        // @ts-ignore
        if ("??type!!" === "download")  {
            return <DownloadFile data={this.state.value} />
        }
        
        // @ts-ignore
        if ("??type!!" === "text")  {
            return (<>
                {JSON.stringify(this.state)} 
            </>)
        }
        
        // @ts-ignore
        if ("??type!!" === "graph" && this.state.value)  
            return <Graph data={this.state.value}/>
        
        // @ts-ignore
        if ("??type!!" === "html") {
            return <HtmlRenderer 
                data={this.state}
                service={this.??title!!Service}
            />
        }
        else return null
    }
} 
    
export default withRouter(??title!!)    
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

    def write_components(self, param):
        written_componens = []
        for component, code in self.components.items():
            try:
                with open("/".join([self.npm_resources, self.resource.title + ".s"]), "w") as f:
                    f.write(code.format(**self.resource, port=self.port, url=self.url, **self.resource.access))
                    written_componens.append(component)
            except:
                logging.error(f"Could not write { self.resource.title }")

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
