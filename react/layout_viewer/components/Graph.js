import loadable from '@loadable/component'
import dynamic from 'next/dynamic'
import * as React from 'react'
import Router, {withRouter} from 'next/router'
import window from 'global'


// Having enourmous problems with these imports: one dynamic as recommended in the internet
const ForceGraph3D = dynamic(() => import('./ForceGraph3d.js'), {
    loading: () => <p>...</p>, ssr: false
})

const ForwardedRefForceGraph3D = React.forwardRef((props, ref) => (<ForceGraph3D {...props} forwardedRef={ref}/>))

// two for the text items... don't think, one of them is superflouus
// THIS IS THE TRICK: ONE IMPORT FOR SSR, ONE FOR THE 3D GRAPH ON CLIENT-SIDE
const SpriteText2 = dynamic(() => import('../components/SpriteText.js'))
import SpriteText from './SpriteText.js'


class Graph extends React.Component {
    myRef = React.createRef();

    constructor(props) {
        super(props);

        console.log(props)
        this.state = {
            graph: {
                "nodes": [{
                    "id": "id1", "name": "name1", "val": 1
                }, {
                    "id": "id2", "name": "name2", "val": 10
                }], "links": [{
                    "source": "id1", "target": "id2"
                },]
            },


            highlightNodes: new Set(),
            highlightLinks: new Set(),
            hoverNode: null
        }
    }

    componentDidMount() {



        const data = this.props.data ? this.props.data : this.state.graph

        console.log(data, "TATA data")
        data.links.forEach(link => {
            const a = data.nodes.find((n) => n.id == link.source)
            const b = data.nodes.find((n) => n.id == link.target)
            if (! a)
               console.log(a , link)
            !a.neighbors && (a.neighbors = []);
            !b.neighbors && (b.neighbors = []);
            a.neighbors.push(b);
            b.neighbors.push(a);

            !a.links && (a.links = []);
            !b.links && (b.links = []);
            a.links.push(link);
            b.links.push(link);
        })
        this.setState({graph: data})

    }


    setHighlightNodes = (val) => this.setState({highlightNodes: val})
    setHighlightLinks = (val) => this.setState({highlightLinks: val})
    setHoverNode = (val) => this.setState({hoverNode: val})


    updateHighlight = () => {
        this.setHighlightNodes(this.state.highlightNodes);
        this.setHighlightLinks(this.state.highlightLinks);
    };

    handleNodeHover = node => {
        this.state.highlightNodes.clear()
        this.state.highlightLinks.clear();
        if (node) {
            this.state.highlightNodes.add(node);
            node.neighbors.forEach(neighbor => this.state.highlightNodes.add(neighbor));
            node.links.forEach(link => this.state.highlightLinks.add(link));
        }

        this.setHoverNode(node || null);
        this.updateHighlight();
    };

    handleLinkHover = link => {
        this.state.highlightNodes.clear();
        this.state.highlightLinks.clear();

        if (link) {
            this.state.highlightLinks.add(link);
            this.state.highlightNodes.add(link.source);
            this.state.highlightNodes.add(link.target);
        }

        this.updateHighlight();
    }

    paintRing = (node, ctx) => {
        // add ring just for highlighted nodes
        ctx.beginPath();
        ctx.arc(node.x, node.y, NODE_R * 1.4, 0, 2 * Math.PI, false);
        ctx.fillStyle = node === hoverNode ? 'red' : 'orange';
        ctx.fill();
    }

    handleClick = (node) => {
        // Aim at node from outside it
        const distance = 40;
        const distRatio = 1 + distance / Math.hypot(node.x, node.y, node.z);
        console.log("REF", this.myRef, this.state)

        this.myRef.then(r => r.cameraPosition({x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio}, // new position
            node, // lookAt ({ x, y, z })
            3000  // ms transition duration
        ));
    }

    render() {
        return (<div>
            <ul>
                <li>Click left to focus</li>
                <li>Click right to navigate to that document</li>
            </ul>

            <ForwardedRefForceGraph3D
                ref={this.myRef}
                graphData={this.state.graph}
                nodeLabel='name'


                nodeThreeObject={(node) => {
                    const obj = new THREE.Mesh(new THREE.SphereGeometry(10), new THREE.MeshBasicMaterial({
                        depthWrite: false,
                        transparent: true,
                        opacity: 0
                    }));
                    const sprite = new SpriteText(node.title ?? node.name);
                    sprite.color = node.color;
                    sprite.textHeight = 3;
                    obj.add(sprite);
                    return obj;
                }}
                onNodeClick={(node) => this.handleClick(node)}
                onNodeRightClick={(node) => Router.push({
                    pathname: '/difference/', query: {...node}
                })}
                autoPauseRedraw={false}
                linkWidth={link => this.state.highlightLinks.has(link) ? 5 : 1}
                linkDirectionalParticles={4}
                linkDirectionalParticleWidth={link => this.state.highlightLinks.has(link) ? 4 : 0}
                nodeCanvasObjectMode={node => this.state.highlightNodes.has(node) ? 'before' : undefined}
                nodeCanvasObject={this.paintRing}
                onNodeHover={this.handleNodeHover}
                onLinkHover={this.handleLinkHover}

            />
        </div>)
    }
}

/*


 */

export default withRouter(Graph)