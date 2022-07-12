import React from 'react'
import Layout from '../components/Layout'
import styled from 'styled-components'

const PageTitle = styled.div`
  align: right;
  margin: 2em;
  padding: 2em;
`;

const H = styled.div`
  text-transform: capitalize;
  font-size: 1em;
`;


const Quote = styled.div`
  font-family: 'Roboto', mono
`;

export default  class Index extends React.Component  {
    render () {
        return (
            <Layout title="Home" pages={this.props.pages}>
                <PageTitle>
                    <H><h1>Library, that <i>learns</i> <a href="https://plato.stanford.edu/entries/categories/">what is different and what the same.</a></h1></H>
                    <p>Democratic systems tend to devide voters into two big parties or groups. Red vs. blue. Green vs Yellow are typical oppositions.
                    And they try to oppose in each point. So as a voter we have often no chance to cherrypick from their programs.</p>

                    <p>And similarly science often looks like big blocks and big blocks block our understanding, because we have no systematic view into the details, that form pros and cons of different approaches.</p>

                    <p>Or in our more or less enlighted being we want to know, if it really makes a big difference to use B instead of A or not.</p>

                    <p>This page tries to deal thus with filtering out "differences" make a system out of that and so to see, how manifold we can get with: <Quote>"It is impossible that the same thing belong and not belong to the same thing at the same time and in the same respect." (Aristotle, 1005b19-20)</Quote>
                       If we speak out all those respects to the things.</p>

                                           <p>The "learning" is done with artificial intelligent algorithms. <ol>
                                           <li>NER-textextration</li>
                                           <li>Gaussian Clustering for making the thematical departments of all our documents</li>
                                           <li>Text2Speech with tacotron2</li>
                                           <li>Layout Recognitions with LayoutMV2 for recognizing where the actual text and title is in the text</li>
</ol>
                                           </p>
                </PageTitle>
            </Layout>
        )
    }
}
