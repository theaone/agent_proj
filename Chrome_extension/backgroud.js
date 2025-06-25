chrome.commands.onCommand.addListener((command) => {
  chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
    if (tabs[0] && tabs[0].url.startsWith("http://localhost:8501")) {
      chrome.tabs.sendMessage(tabs[0].id, {action: command});
    }
  });
});