import loadable from '@loadable/component'
import dynamic from 'next/dynamic'
import * as React from 'react'

if (typeof window === 'undefined') {
    global.window = {}
}


// const ForceGraph3D = loadable(() => )
const ForceGraph3D = dynamic(
    () => import('./ForceGraph3d.js'),
    {
        loading: () => <p>...</p>,
        ssr: false
    }
)
// const ForceGraph3D = loadable(() => )
import SpriteText from './SpriteText.js'


export default class Graph extends React.Component  {
    constructor(props) {
        super(props);
        this.myRef = React.createRef();

        console.log(props)
        this.state = {
            graph: this.props.data ?? {
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

        this.handleClick = this.handleClick.bind(this)
    }

    /* */

    handleClick (node)  {
        // Aim at node from outside it
          const distance = 40;
          const distRatio = 1 + distance/Math.hypot(node.x, node.y, node.z);
          console.log("HANDLE CLICKs")
          this.myRef.current.cameraPosition(
            { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio }, // new position
            node, // lookAt ({ x, y, z })
            3000  // ms transition duration
          );
    }

    render()  {
           console.log("REF", this.myRef, this.state)
           return  (
               <ForceGraph3D
                  ref={this.myRef}

                  graphData={ this.props.graph??this.state.graph}
                  nodeLabel = 'id'
                  nodeAutoColorBy = 'group'

        nodeThreeObject = {(node) =>
        {
                      const obj = new THREE.Mesh(
            new THREE.SphereGeometry(10),
            new THREE.MeshBasicMaterial({ depthWrite: false, transparent: true, opacity: 0 })
          );

          // add text sprite as child
          const sprite = new SpriteText(node.id);
          sprite.color = node.color;
          sprite.textHeight = 8;
          obj.add(sprite);

          return obj;
        }}
                        onNodeClick={(node) => this.handleClick(node)}
                        onNodeRightClick={(node) => console.log("FORWARD To DOCUMENT")}

               />)

/*

 */
    }
}