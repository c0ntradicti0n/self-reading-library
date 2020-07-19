import React, {Component} from 'react';
import logo from './logo.svg';
import './App.css';
import * as glob from "glob";



export default class App extends Component {

    async getPages() {
        return await glob('pages/**/*.ts', { cwd: __dirname })

    }
 
  render() {
      for (const [index, element] of foobar.entries()) {
          <div className="App">
          </div>

          console.log(index, element);

      }
  }
}

