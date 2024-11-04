document.getElementById('extract-url').addEventListener('click', () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const currentTab = tabs[0];
        const url = currentTab.url;

        // Display the URL in the popup
        document.getElementById('output').textContent = url;

        // Optionally, send the URL to the background script or do something else
        chrome.runtime.sendMessage({ url: url });
    });
});
