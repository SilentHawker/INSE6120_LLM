chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.url) {
        console.log('Extracted URL:', request.url);
        // You can store it, process it, or send it to another service here
    }
});
