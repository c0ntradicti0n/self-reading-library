import React from 'react'
import ReactDOM from 'react-dom'
import './index.css'
import App from './App'
import * as serviceWorker from './serviceWorker'
require('colors')

if (window) {
  console.log(window)
  window.addEventListener('beforeunload', function (e) {
    window.sessionStorage.tabId = window.tabId
    console.log('beforeunload', window)

    return null
  })

  window.addEventListener('load', function (e) {
    if (window.sessionStorage.tabId) {
      window.tabId = window.sessionStorage.tabId
      window.sessionStorage.removeItem('tabId')
    } else {
      window.tabId = Math.floor(Math.random() * 1000000)
    }
    console.log('load', window)

    return null
  })
}

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
)

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister()
