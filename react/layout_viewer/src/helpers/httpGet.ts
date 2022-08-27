export function httpGet(theUrl) {
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
  xmlhttp.open('GET', theUrl, false)
  xmlhttp.send()

  return xmlhttp.response
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
