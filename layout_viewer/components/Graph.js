
import loadable from '@loadable/component'
import * as React from 'react'

const ForceGraphVR = loadable(() => import('./ForceGraph3d.js'))



export default class Graph extends React.Component  {
    constructor(props) {
        super(props);

        this.state = {
            graph: {
                "nodes": [
                    {
                        "id": "id1",
                        "name": "name1",
                        "val": 1
                    },
                    {
                        "id": "id2",
                        "name": "name2",
                        "val": 10
                    }
                ],
                "links": [
                    {
                        "source": "id1",
                        "target": "id2"
                    },
                ]
            }
        }
    }

    render()  {
           console.log("GRAPH DATA", this.props.graph??this.state.graph)
           return  (
               <ForceGraphVR graphData={ this.props.graph??this.state.graph}
               nodeAutoColorBy="group"
                  nodeThreeObject={node => {
                    const sprite = new SpriteText(node.id);
                    sprite.color = node.color;
                    sprite.textHeight = 8;
                    return sprite;
                  }}
               />)


    }
}