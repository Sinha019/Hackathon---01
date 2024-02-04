// static/bot.js
function askQuestion() {
  var question = document.getElementById("question").value;

  if (!question) {
      appendMessage("Please enter a question.", "system");
      return;
  }

  appendMessage(question, "user");

  fetch('/ask', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: 'question=' + encodeURIComponent(question),
  })
  .then(response => response.json())
  .then(data => {
      appendMessage(data['Title'], "bot");
      appendMessage(data['Summary'], "bot");
  })
  .catch(error => console.error('Error:', error));
}

function appendMessage(message, sender) {
  var chatBody = document.getElementById("chat-body");
  var messageDiv = document.createElement("div");

  if (sender === "system") {
      messageDiv.className = "system-message";
  } else if (sender === "user") {
      messageDiv.className = "user-message";
  } else {
      messageDiv.className = "bot-message";
  }

  messageDiv.innerHTML = message;
  chatBody.appendChild(messageDiv);

  // Scroll to the bottom of the chat window
  chatBody.scrollTop = chatBody.scrollHeight;
}
