import Document, { Head, Main, NextScript } from 'next/document';

export default class MyDocument extends Document {
  static getInitialProps({ renderPage }) {
    return {html : "asdabc"}
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
