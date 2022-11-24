export function httpGet(theUrl, callback) {
  let xmlhttp

  if (window.XMLHttpRequest) {
    // code for IE7+, Firefox, Chrome, Opera, Safari
    xmlhttp = new XMLHttpRequest()
  }

  xmlhttp.onreadystatechange = function () {
    if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
      return xmlhttp.responseText
    }
  }
  console.log(theUrl)
  xmlhttp.open('GET', theUrl, false)
  xmlhttp.setRequestHeader('X-Requested-With', 'XMLHttpRequest')
  xmlhttp.setRequestHeader('Access-Control-Allow-Origin', '*')
  console.log('beforesend')
  xmlhttp.send()
  console.log('html', xmlhttp.response)
  callback(xmlhttp.response)
}

export const getParam = (param) => {
  console.log(
    'HELLO',
    window,
    window.location,
    window.location.search,
    new URLSearchParams(window.location.search).get(param)
  )
  return new URLSearchParams(window.location.search).get(param)
}
