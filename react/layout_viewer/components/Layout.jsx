import * as React from "react";
import Head from "next/head";
import styled from "styled-components";
import Url2Difference from "./Url2Difference";
import {Button} from "@mui/material";

const layoutStyle = {
    margin: 20,
    padding: 20,
    display: "flex",
};

const Lib = styled.div`
  //border: 3px solid black;
  height: 10em;
  grid-column-end: span 2;
  margin: 10px;
`;

const Mansonry = styled.div`
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: masonry;
  gap: 10px;

  font-family: "Roboto Serif", serif;
`;

export default class Layout extends React.Component {
    render() {
        let title = "Automatic library";

        return (
            <div style={layoutStyle}>
                <Head>
                    <title>{title}</title>
                    <meta charSet="utf-8"/>
                    <meta
                        name="viewport"
                        content="initial-scale=1.0, width=device-width"
                    />
                    <link rel="icon" href="/favicon.ico"/>
                    <style>
                        @import
                        url('https://fonts.googleapis.com/css2?family=Roboto+Serif:ital,opsz,wght@0,8..144,300;0,8..144,400;1,8..144,300&display=swap');
                    </style>
                </Head>

                <Mansonry>
                    <ul>
                        <Lib>
                            <Button href="/library">Universe of documents</Button>
                        </Lib>
                        <Lib>
                            <Button href="/difference">
                                Random documents with library extracts
                            </Button>
                        </Lib>
                        <Lib>
                            Read a webpage for me:
                            <Url2Difference/>
                            <img src="/read_it.jpeg"/>
                        </Lib>
                    </ul>
                    {/*this.props.pages?.map((page, index) =>
                    <> <Link href={"/" + page} key={index}>
                        <a>{page}</a>
                    </Link> {' '} </>)
                */}

                    {this.props.children}

                    <Lib>
                        Some source of papers: <Button href={"http://arxiv.org"}>http://arxiv.org</Button>
                        <br/>
                        <img src="/source_of_papers.jpeg"/>
                    </Lib>
                    <Lib>

                        Some other websites featuring <i> differences </i>
                        <ul>
                            <li><Button
                                href={"http://www.differencebetween.net/"}>http://www.differencebetween.net/</Button>
                            </li>
                            <li><Button
                                href={"http://www.differencebetween.com/"}>http://www.differencebetween.com/</Button>
                            </li>
                        </ul>
                    </Lib>

                </Mansonry>
            </div>
        );
    }
}
