document.addEventListener('DOMContentLoaded', () => {
  const logBtn = document.getElementById('logBtn');
  const messageDiv = document.getElementById('messageDiv');
  const messageInput = document.getElementById('messageInput');

  logBtn.addEventListener('click', async () => {
    const message = messageInput.value.trim();
    if (!message) {
      messageDiv.textContent = 'Please enter a message.';
      return;
    }

    logBtn.disabled = true;
    logBtn.textContent = 'Processing...';
    messageDiv.textContent = 'Loading...';

    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab || !tab.url.includes('youtube.com/watch')) {
        messageDiv.textContent = 'Open a YouTube video to use this extension.';
        resetButton();
        return;
      }

      const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => {
          const title = document.querySelector('#title yt-formatted-string');
          const otherDetails = document.getElementById('top-row');
          const description = document.querySelector('#expanded yt-attributed-string');
          const transcript = document.getElementById('panels');

          let titleText = title ? title.textContent : 'Title not found';
          let descriptionText = description ? description.innerText.trim() : 'Description not found';
          let otherDetailsText = transcript ? transcript.innerText : 'Transcript not found';
          let transcriptText = otherDetails ? otherDetails.innerText : 'Details not found';


          return ` VideoTitle: \n\n ${titleText} \n\n Description: \n\n ${descriptionText} \n\n otherDetails: \n\n ${otherDetailsText} \n\n Transcript: \n\n ${transcriptText} `
        }
      });

      const vidDetails = results[0].result;
      const data = { query: message, vidDetails: vidDetails };
      console.log(data);

      const response = await fetch('https://youtube-chat-extensioin-backend.onrender.com/videochat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      const jsonData = await response.json();
      messageDiv.textContent = jsonData.answer || 'No answer received.';
    } catch (error) {
      messageDiv.textContent = 'Error: ' + error.message;
    }

    resetButton();
  });

  function resetButton() {
    logBtn.disabled = false;
    logBtn.textContent = logBtn.getAttribute('data-default-text') || 'Submit';
  }
});