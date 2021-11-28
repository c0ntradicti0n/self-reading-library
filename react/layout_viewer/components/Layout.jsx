import * as React from 'react'
import Link from 'next/link'
import Head from 'next/head'
import Graph from "./Graph";


const layoutStyle = {
    margin: 20,
    padding: 20,
    border: '1px solid #DDD',
    display: "flex"
}

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
                <nav>
                    {this.props.pages?.map((page, index) =>
                        <> <Link href={"/" + page} key={index}>
                            <a>{page}</a>
                        </Link>) {' '} </>)
                    }
                </nav>
            </header>
            {/*<Graph input={this.props.pages}></Graph>*/}

            {this.props.children}
        </div>)
    }


}
