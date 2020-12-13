import Document, { Head, Main, NextScript } from 'next/document';
import glob from 'glob'


export default class MyDocument extends Document {
  constructor(props) {
    super(props);
    this.state = {
      pages : []
    }

    let a = (async () => {
  try {
    result =  await glob('pages/**/*.js', {cwd: './'}, (res) => this.setState({pages:res}));
  } catch(e) {}
})()
  }

   static getInitialProps({ renderPage }) {
    return {html : "", ... this.state}
  }


  render() {
    return (
      <html>
        <body>
          <Main />
          <NextScript />
        </body>
      </html>
    );
  }
}
