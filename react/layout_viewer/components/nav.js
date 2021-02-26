  import React from 'react';

  export default class Nav extends React.Component {
static async getInitialProps({ query }) {

  return { A:"HALLO!" }
}

    render() {
      return (
        <nav className="Nav">
          <div className="Nav__container">NAV
                           {JSON.stringify(this.props)}
          </div>
        </nav>
      );
    }
  }