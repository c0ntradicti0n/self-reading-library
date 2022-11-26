import React from "react";
import Layout from "../src/components/Layout";
import styled from "styled-components";

import { Button } from "@mui/material";
import { DASH_HOST } from "../config/connection";

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
  font-family: serif;
`;

export default class Index extends React.Component {
  render() {
    return (
      <Layout title="Home" pages={this.props.pages}>
        <iframe
          style={{ width: "60vw", border: "none" }}
          src={DASH_HOST}
          width="60vw"
          height="100%"
        >
          {" "}
        </iframe>
        <PageTitle>
          <p>
            People cannot think without oppositions, no decision, no approach,
            not any concept would there be, without knowing something about your
            consept A and what it makes something else from other things.
          </p>
          <p>
            <ul>
              <li>
                Legend markup for{" "}
                <span className="span_SUBJECT">opposites (a "subject")</span>
                and{" "}
                <span className="span_CONTRAST">
                  {" "}
                  explanation of opposition (a "contrast")
                </span>
              </li>
              <li>Audiobooks</li>
              <li>Layout</li>
            </ul>
          </p>
          <p>
            <Quote>
              "It is impossible that the same thing belong and not belong to the
              same thing at the same time and in the same respect." (Aristotle,
              1005b19-20)
            </Quote>
          </p>
          Content follows form
        </PageTitle>
      </Layout>
    );
  }
}
