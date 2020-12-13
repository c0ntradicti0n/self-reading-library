import loadable from '@loadable/component'
import dynamic from 'next/dynamic'
import * as React from 'react'
import Router, { withRouter } from 'next/router'


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
const ForwardedRefForceGraph3D = React.forwardRef((props, ref) => (
  <ForceGraph3D {...props} forwardedRef={ref} />
))
// const ForceGraph3D = loadable(() => )
//import SpriteText from './SpriteText.js'


class Graph extends React.Component  {
    constructor(props) {
        super(props);

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
           console.log("REF", this.myRef, this.state)

          this.myRef.then(r => r.cameraPosition(
            { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio }, // new position
            node, // lookAt ({ x, y, z })
            3000  // ms transition duration
          ));


    }

    render()  {
                this.myRef = React.createRef();

          console.log(this)
           return  (
               <ForwardedRefForceGraph3D
                  ref={(ref) => this.myRef = ref}


                  graphData={ this.props.graph??this.state.graph}
                  nodeLabel = 'name'
                  nodeAutoColorBy = 'group'
/*
                  nodeThreeObject = {(node) =>
                            {
                                          const obj = new THREE.Mesh(
                                new THREE.SphereGeometry(10),
                                new THREE.MeshBasicMaterial({ depthWrite: false, transparent: true, opacity: 0 })
                              );

                          // add text sprite as child
                          //const sprite = new SpriteText(node.name);
                          //sprite.color = node.color;
                          //sprite.textHeight = 8;
                          //obj.add(sprite);

                          return obj;
                        }}
                onNodeClick={(node) => this.handleClick(node)}
                onNodeRightClick={(node) =>
                    Router.push({
                    pathname: '/markup',
                    query: { ... node }
                })}*/

               />)
    }
}

export default withRouter(Graph)