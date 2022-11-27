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
   xmlhttp.open('GET', theUrl, false)
   xmlhttp.setRequestHeader('X-Requested-With', 'XMLHttpRequest')
   xmlhttp.setRequestHeader('Access-Control-Allow-Origin', '*')
   xmlhttp.send()
   callback(xmlhttp.response)
}

export const getParam = (param) => {
   return new URLSearchParams(window.location.search).get(param)
}
