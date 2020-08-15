
import loadable from '@loadable/component'
import * as React from 'react'

if (typeof window === 'undefined') {
    global.window = {}
}
import SpriteText from 'three-spritetext';


const ForceGraph3D = loadable(() => import('./ForceGraph3d.js'))

export default class Graph extends React.Component  {
    constructor(props) {
        super(props);
        this.myRef = React.createRef();


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
           console.log(this.myRef)
           return  (
               <ForceGraph3D
                  ref={this.myRef}

                  graphData={ this.props.graph??this.state.graph}
                  nodeLabel = 'id'
                  nodeAutoColorBy = 'group'

        nodeThreeObject = {(node) =>
        {

            // extend link with text sprite
            const sprite = new SpriteText(`${node.name}`)


            const obj = new THREE.Mesh(
                new THREE.SphereGeometry(10),
                new THREE.MeshBasicMaterial({depthWrite: false, transparent: true, opacity: 0})
            );

            // add text sprite as child
            sprite.color = node.color;
            sprite.textHeight = 1;
            obj.add(sprite);
            return obj
        }}
                        onNodeClick={(node) => this.handleClick(node)}
                        onNodeRightClick={(node) => console.log("FORWARD To DOCUMENT")}

               />)

/*

 */
    }
}