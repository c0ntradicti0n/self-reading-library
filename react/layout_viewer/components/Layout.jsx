import * as React from 'react'
import Link from 'next/link'
import Head from 'next/head'
import Graph from "./Graph";
import FlutterDashIcon from '@mui/icons-material/FlutterDash';
import styled from 'styled-components'

const layoutStyle = {
    margin: 20,
    padding: 20,
    border: '1px solid #DDD',
    display: "flex"
}


const Lib = styled.p`
  background: 'yellow';
`;

export default class Layout extends React.Component {
    render() {
        let title = "CRAZY APP";

        return (<div style={layoutStyle}>
            <Head>
                <title>{title}</title>
                <meta charSet="utf-8"/>
                <meta name="viewport" content="initial-scale=1.0, width=device-width"/>
            </Head>
            <header>
                <ul>
                    <Lib><FlutterDashIcon/><Link href="/library">universe of documents</Link></Lib>
                    <Lib><FlutterDashIcon/><Link href="/difference">preread document</Link></Lib>
                    <Lib><FlutterDashIcon/><Link href="/birds">
                        <a>Birds Example</a>
                    </Link></Lib>
                    <Lib><FlutterDashIcon/><Link href="/boxes">
                        <a>Boxes Example</a>
                    </Link></Lib>
                </ul>
                {/*this.props.pages?.map((page, index) =>
                    <> <Link href={"/" + page} key={index}>
                        <a>{page}</a>
                    </Link> {' '} </>)
                */}
            </header>


            {
                this.props.children
            }

            Source of papers: <a href={'http://arxiv.org'}>http://arxiv.org</a>
        </div>)
    }


}
