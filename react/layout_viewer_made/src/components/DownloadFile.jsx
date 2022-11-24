import * as React from 'react'
import Button from '@mui/material/Button'
import { BACKEND_HOST } from '../../config/connection'

export default class DownloadFile extends React.Component {
  render() {
    console.log(this.props)
    return (
      <form
        method="POST"
        target="_blank"
        action={BACKEND_HOST + '/' + this.props.kind}>
        <input value={this.props.id} id="id" name="id" type={'text'} hidden />
        <Button type="submit">Download {this.props.children}</Button>
      </form>
    )
  }
}
