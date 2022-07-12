import * as React from "react";
import Link from "next/link";
import Head from "next/head";
import Graph from "./Graph";
import FlutterDashIcon from "@mui/icons-material/FlutterDash";
import styled from "styled-components";
import Url2Difference from "./Url2Difference";

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
          <meta charSet="utf-8" />
          <meta
            name="viewport"
            content="initial-scale=1.0, width=device-width"
          />
          <link rel="icon" href="/favicon.ico" />
          <style>
            @import
            url('https://fonts.googleapis.com/css2?family=Roboto+Serif:ital,opsz,wght@0,8..144,300;0,8..144,400;1,8..144,300&display=swap');
          </style>
        </Head>

        <Mansonry>
          <ul>
            <Lib>
              <FlutterDashIcon />
              <Link href="/library">Universe of documents</Link>
            </Lib>
            <Lib>
              <FlutterDashIcon />
              <Link href="/difference">
                Random documents with library extracts
              </Link>
            </Lib>
            <Lib>
              <FlutterDashIcon />
              Analyse/Extract some page:
              <Url2Difference />
              <img src="/read_it.jpeg" />
            </Lib>
          </ul>
          {/*this.props.pages?.map((page, index) =>
                    <> <Link href={"/" + page} key={index}>
                        <a>{page}</a>
                    </Link> {' '} </>)
                */}

          {this.props.children}

          <Lib>
            <FlutterDashIcon />
            Source of papers: <a href={"http://arxiv.org"}>http://arxiv.org</a>
            <br />
            <img src="/source_of_papers.jpeg" />
          </Lib>
        </Mansonry>
      </div>
    );
  }
}
