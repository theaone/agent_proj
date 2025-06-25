chrome.runtime.onMessage.addListener((message) => {
  if (message.action === "open_qa") {
    window.location.pathname = "/pages/小智问答";
  } else if (message.action === "go_home") {
    window.location.pathname = "/";
  }
});