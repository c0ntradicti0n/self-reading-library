import React from "react";
import Layout from "../src/components/Layout";
import styled from "styled-components";
import { Button } from "@mui/material";

const PageTitle = styled.div`
  align: right;
  margin: 2em;
  padding: 2em;
`;

const H = styled.div`
  text-transform: capitalize;
  font-size: 1em;
  animation: color-change 10s infinite, background-color-change 10s infinite;
  border-radius: 30px;
  width: 55rem;
  height: 15rem;
`;

const CenterHorizontallyVertically = styled.div`
  padding: 70px 0;
  text-align: center;
`;

const Quote = styled.div`
  font-family: "Roboto", mono;
`;

export default class Index extends React.Component {
  render() {
    return (
      <Layout title="Home" pages={this.props.pages}>
        <PageTitle>
          <H>
            <CenterHorizontallyVertically>
              <h1>
                Library, that <i>learns</i>
                <Button href="https://plato.stanford.edu/entries/categories/">
                  what is different and what the same.
                </Button>
              </h1>
            </CenterHorizontallyVertically>
          </H>
          <p>
            People cannot think without oppositions, no decision, no approach,
            not any concept would there be, without knowing something about your
            consept A and what it makes something else from other things.
          </p>

          <p>
            This page tries to make you focussing on such things, while
            studying. It tries to read the text for you and offer it in various
            ways as:
            <ul>
              <li>PDF-Readerlike view on your papapers</li>
              <li>
                Put markup for{" "}
                <span className="span_SUBJECT">
                  concepts, beeing different{" "}
                </span>
                and{" "}
                <span className="span_CONTRAST">
                  {" "}
                  phrases, explaining something, that makes them different, here
                  we call them "contrasts".
                </span>
              </li>
              <li>Audiobooks</li>
              <li>Putting your notes on the text</li>
              <li>Get crosswords for your texts</li>
              <li>Enjoy word bubbles</li>
            </ul>
          </p>

          <p>
            <Quote>
              "It is impossible that the same thing belong and not belong to the
              same thing at the same time and in the same respect." (Aristotle,
              1005b19-20)
            </Quote>
          </p>

          <p>
            The "learning" is done with artificial intelligent algorithms.
            <ul>
              <li>NER-textextration</li>
              <li>
                Gaussian Clustering for making the thematical departments of all
                our documents
              </li>
              <li>Text2Speech with tacotron2</li>
              <li>
                Layout Recognitions with LayoutMV2 for recognizing where the
                actual text and title is in the text
              </li>
            </ul>
          </p>
        </PageTitle>
      </Layout>
    );
  }
}
