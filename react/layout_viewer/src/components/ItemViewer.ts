class TemplateComponent extends React.Component {
  constructor(props) {
    super(props)
    this.html = require(props.template)
  }

  render() {
    return <div dangerouslySetInnerHTML={{__html: this.html}} style={this.state.styleObj}/>
  }

