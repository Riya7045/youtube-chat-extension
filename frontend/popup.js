document.addEventListener('DOMContentLoaded', () => {
  const logBtn = document.getElementById('logBtn');
  const messageDiv = document.getElementById('messageDiv');
  const messageInput = document.getElementById('messageInput');

  logBtn.addEventListener('click', () => {
    const message = messageInput.value.trim();

    if (!message) {
      messageDiv.textContent = 'Please enter a message.';
      return;
    }

    logBtn.disabled = true;
    logBtn.textContent = 'Processing...';
    messageDiv.textContent = 'Loading...';

    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs.length === 0) {
        messageDiv.textContent = 'No active tab found.';
        logBtn.disabled = false;
        logBtn.textContent = logBtn.getAttribute('data-default-text');
        return;
      }

      const currentUrl = tabs[0].url;
      const videoIdMatch = currentUrl.match(/[?&]v=([^&]+)/);

      if (videoIdMatch && videoIdMatch[1]) {
        const videoId = videoIdMatch[1];
        const data = {
          query: message,
          videoId: videoId
        };

        fetch('http://127.0.0.1:8000/videochat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(data)
        })
          .then(response => response.json())
          .then(jsonData => {
            messageDiv.textContent = jsonData.answer;
            logBtn.disabled = false;
            logBtn.textContent = logBtn.getAttribute('data-default-text');
          })
          .catch(error => {
            messageDiv.textContent = 'Error: ' + error.message;
            logBtn.disabled = false;
            logBtn.textContent = logBtn.getAttribute('data-default-text');
          });
      } else {
        messageDiv.textContent = 'Open a YouTube video to use this extension.';
        logBtn.disabled = false;
        logBtn.textContent = logBtn.getAttribute('data-default-text');
      }
    });
  });
});
