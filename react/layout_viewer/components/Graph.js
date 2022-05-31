import loadable from '@loadable/component'
import dynamic from 'next/dynamic'
import * as React from 'react'
import Router, {withRouter} from 'next/router'
import window from 'global'


// Having enourmous problems with these imports: one dynamic as recommended in the internet
const ForceGraph3D = dynamic(
    () => import('./ForceGraph3d.js'),
    {
        loading: () => <p>...</p>,
        ssr: false
    }
)

const ForwardedRefForceGraph3D = React.forwardRef((props, ref) => (
    <ForceGraph3D {...props} forwardedRef={ref}/>
))

// two for the text items... don't think, one of them is superflouus
// THIS IS THE TRICK: ONE IMPORT FOR SSR, ONE FOR THE 3D GRAPH ON CLIENT-SIDE
const SpriteText2 = dynamic(() =>
    import('../components/SpriteText.js'))
import SpriteText from './SpriteText.js'


class Graph extends React.Component {
    myRef = React.createRef();

    constructor(props) {
        super(props);

        console.log(props)
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

    handleClick(node) {
        // Aim at node from outside it
        const distance = 40;
        const distRatio = 1 + distance / Math.hypot(node.x, node.y, node.z);
        console.log("REF", this.myRef, this.state)

        this.myRef.then(r => r.cameraPosition(
            {x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio}, // new position
            node, // lookAt ({ x, y, z })
            3000  // ms transition duration
        ));


    }

    render() {

        console.log(this)
        return (
            <div><ul><li>Click left to focus</li><li>Click right to navigate to that document</li></ul> <ForwardedRefForceGraph3D
                ref={this.myRef}
                graphData={this.props.data ? this.props.data : this.state.graph}
                nodeLabel='name'
                nodeAutoColorBy='group'


                nodeThreeObject={(node) => {
                    const obj = new THREE.Mesh(
                        new THREE.SphereGeometry(10),
                        new THREE.MeshBasicMaterial({depthWrite: false, transparent: true, opacity: 0})
                    );
                    const sprite = new SpriteText(node.name);
                    sprite.color = node.color;
                    sprite.textHeight = 8;
                    obj.add(sprite);
                    return obj;
                }}
                onNodeClick={(node) => this.handleClick(node)}
                onNodeRightClick={(node) =>
                    Router.push({
                        pathname: '/difference/',
                        query: {...node}
                    })}

            />
            </div>
        )
    }
}

export default withRouter(Graph)