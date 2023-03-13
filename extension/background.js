
function openTab() {
    console.log("write mail")
    ;(async () => {
const [tab] = await browser.tabs.query({active: true, currentWindow: true});
  const differenceLocation = 'http://polarity.science/difference?id=' + encodeURIComponent(tab.url);

        if (!mymail || ! name || !bday )
            browser.runtime.openOptionsPage()
        else
            browser.tabs.create({
                url: differenceLocation,
                active: true
            })
    })()
}

browser.browserAction.onClicked.addListener(openTab)

