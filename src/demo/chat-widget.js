(function() {
  const style = document.createElement('style');
  style.innerHTML = `
  #safqore-chat-wrapper {
    position: relative;
    font-family: Arial, sans-serif;
    font-size: 16px;
    line-height: 1.4;
  }

  /* Chat window - default hidden state */
  #safqore-chat-wrapper .chat-window {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 426px;
    min-width: 350px;
    min-height: 400px;
    background: #fff;
    border: none;
    border-radius: 10px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
    display: none;
    flex-direction: column;
    z-index: 9999;
    overflow: hidden;
    font-size: 1.0rem;
    color: #333333;
    font-family: "Arial", sans-serif;
    transform: translateY(100%);
    transition: transform 0.3s ease, opacity 0.3s ease;
    opacity: 0;
    border: 1px solid #e0e0e0;
  }

  /* Open state */
  #safqore-chat-wrapper .chat-window.open {
    display: flex;
    transform: translateY(0);
    opacity: 1;
  }

  /* Chat bubble - using green from Subscribe button */
  #safqore-chat-wrapper .chat-bubble {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: #ffc000;
    color: white;
    border: none;
    padding: 12px 20px;
    border-radius: 8px;
    cursor: pointer;
    font-family: "Arial", sans-serif;
    font-size: 1rem;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
    z-index: 9999;
    animation: pulse-button 4s infinite;
    transition: background 0.3s ease, opacity 0.3s ease;
  }

  #safqore-chat-wrapper .chat-bubble:hover {
    background: #e6ac00;
    transform: scale(1.05);
  }

  /* Pulse animation using green */
  @keyframes pulse-button {
    0% {
      box-shadow: 0 0 0 0 rgba(255, 192, 0, 0.7);
    }
    50% {
      box-shadow: 0 0 15px 10px rgba(255, 192, 0, 0.3);
    }
    100% {
      box-shadow: 0 0 0 0 rgba(255, 192, 0, 0.7);
    }
  }

  #safqore-chat-wrapper .chat-bubble .icon {
    margin-right: 8px;
  }

  /* For larger screens */
  @media (min-width: 600px) {
    #safqore-chat-wrapper .chat-window {
      height: 80vh;
    }
  }

  /* Mobile responsiveness */
  @media (max-width: 600px) {
    #safqore-chat-wrapper .chat-window {
      width: 100%;
      height: 100%;
      right: 0;
      bottom: 0;
      border-radius: 0;
      max-height: none;
    }
  }

  /* Header with primary blue background */
  #safqore-chat-wrapper .chat-header {
    background: #ffc000;
    color: #fff;
    font-family: "Arial", sans-serif;
    font-size: 1.1rem;
    padding: 16px;
    position: relative;
    border-bottom: 2px solid #003355;
  }

  #safqore-chat-wrapper .chat-header .header-text h2 {
    margin: 0 0 4px 0;
    font-size: 1.1rem;
    font-weight: bold;
  }

  #safqore-chat-wrapper .close-btn {
    position: absolute;
    top: 5px;
    right: 8px;
    background: transparent;
    border: none;
    color: #fff;
    font-size: 2.4rem;
    cursor: pointer;
    opacity: 0.8;
    transition: opacity 0.2s;
  }

  #safqore-chat-wrapper .close-btn:hover {
    opacity: 1;
  }

  /* Message styling */
  #safqore-chat-wrapper .chat-body {
    font-family: "Arial", sans-serif;
    color: #333333;
    flex: 1;
    padding: 15px;
    overflow-y: auto;
    background: #fff;
    line-height: 1.5;
  }

  #safqore-chat-wrapper .chat-message {
    margin-bottom: 15px;
    line-height: 1.4;
  }

  /* User messages - using secondary green */
  #safqore-chat-wrapper .chat-message.user {
    text-align: right;
    padding-right: 7px;
    margin-left: auto;
    max-width: 85%;
  }

  #safqore-chat-wrapper .chat-message.user span {
    display: inline-block;
    background: #ffc000;
    color: #333;
    padding: 10px 15px;
    border-radius: 12px 12px 0 12px;
    word-wrap: break-word;
    line-height: 1.5;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  }

  /* Bot messages - using light background */
  #safqore-chat-wrapper .chat-message.bot {
    text-align: left;
    margin-right: auto;
    margin-left: 5px;
    max-width: 90%;
    background: #f8f9fa;
    padding: 12px;
    border-radius: 12px 12px 12px 0;
    border: 1px solid #e0e0e0;
    box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.05);
  }

  #safqore-chat-wrapper .chat-message.bot span {
    display: inline-block;
    background: transparent;
    color: #333333;
    word-wrap: break-word;
  }

  /* Bot Response Styling */
  #safqore-chat-wrapper .formatted-response h3 {
    font-size: 1rem;
    color: #004D80;
    margin: 5px 0;
    font-weight: bold;
  }

  #safqore-chat-wrapper .formatted-response h4 {
    font-size: 0.9rem;
    color: #333;
    margin: 4px 0;
  }

  #safqore-chat-wrapper .formatted-response ul {
    list-style-type: disc;
    margin: 5px 0;
    padding-left: 20px;
  }

  #safqore-chat-wrapper .formatted-response ol {
    list-style-type: decimal;
    margin: 5px 0;
    padding-left: 20px;
  }

  #safqore-chat-wrapper .formatted-response li {
    margin-bottom: 3px;
    line-height: 1.5;
  }

  #safqore-chat-wrapper .formatted-response strong {
    font-weight: bold;
    color: #333;
  }

  #safqore-chat-wrapper .formatted-response br {
    margin-bottom: 2px;
  }

  /* Footer styling */
  #safqore-chat-wrapper .chat-footer {
    padding: 12px;
    background: #fff;
    border-top: 1px solid #e0e0e0;
    display: flex;
    flex-direction: column;
    gap: 8px;
    position: relative;
  }

  /* Input styling */
  #safqore-chat-wrapper .input-row {
    display: flex;
    align-items: center;
    background: #f8f9fa;
    border-radius: 25px;
    padding: 5px 10px;
    border: 1px solid #ddd;
  }

  #safqore-chat-wrapper .chat-input {
    flex: 1;
    border: none;
    background: transparent;
    outline: none;
    padding: 8px 12px;
    font-size: 1.0rem;
    color: #333333;
  }

  /* Send button - using orange from CTA */
  #safqore-chat-wrapper .send-btn {
    background: #ffc000;
    border: none;
    cursor: pointer;
    color: white;
    font-size: 1.1rem;
    width: 36px;
    height: 36px;
    text-align: center;
    line-height: 36px;
    padding: 0;
    border-radius: 50%;
    transition: background 0.2s ease;
  }

  #safqore-chat-wrapper .send-btn:hover {
    background: #e6ac00;
  }

  /* Typing indicator - using primary blue */
  #safqore-chat-wrapper .typing-indicator {
    display: flex;
    align-items: flex-end;
    gap: 5px;
    font-size: 0.85rem;
    color: #004D80;
  }

  #safqore-chat-wrapper .typing-indicator .dot {
    width: 6px;
    height: 6px;
    background-color: #004D80;
    border-radius: 50%;
    animation: bounce 1.4s infinite ease-in-out;
    margin-bottom: 2px;
  }

  #safqore-chat-wrapper .typing-indicator .dot:nth-child(1) {
    animation-delay: -0.32s;
  }
  #safqore-chat-wrapper .typing-indicator .dot:nth-child(2) {
    animation-delay: -0.16s;
  }
  #safqore-chat-wrapper .typing-indicator .dot:nth-child(3) {
    animation-delay: 0;
  }

  @keyframes bounce {
    0%, 80%, 100% {
      transform: scale(0);
    }
    40% {
      transform: scale(1);
    }
  }

  /* Links - using primary blue */
  #safqore-chat-wrapper a {
    color: #004D80;
    text-decoration: none;
    font-weight: bold;
  }

  #safqore-chat-wrapper a:hover {
    text-decoration: underline;
  }

  /* Timestamps */
  #safqore-chat-wrapper .message-timestamp-user {
    font-size: 0.75rem;
    color: #666;
    margin-top: 4px;
    text-align: right;
  }

  #safqore-chat-wrapper .message-timestamp-bot {
    font-size: 0.75rem;
    color: #666;
    margin-top: -8px;
    margin-left: 12px;
    text-align: left;
    padding-bottom: 12px;
  }

  /* Powered by link - using secondary green */
  #safqore-chat-wrapper .powered-by {
    font-size: 0.75rem;
    color: #666;
    text-align: center;
  }

  #safqore-chat-wrapper .powered-by a {
    color: #4CAF50;
    text-decoration: none;
  }

  #safqore-chat-wrapper .powered-by a:hover {
    text-decoration: underline;
    color: #45a049;
  }
  `;
  document.head.appendChild(style);

  const wrapper = document.createElement('div');
  wrapper.id = 'safqore-chat-wrapper';
  wrapper.innerHTML = `
    <div class="chat-bubble" id="chat-bubble">
      <span class="icon">💬</span>Any Questions? Let's Chat!
    </div>
    <div class="chat-window" id="chat-window">
      <div class="chat-header">
        <div class="header-text">
          <h2>Premier Suites - AI Assistant 🐾</h2>
        </div>
        <button id="close-chat" class="close-btn">&times;</button>
      </div>
      <div class="chat-body">
        <div class="chat-message bot">
          <span>
            <b>Welcome to Premiere Suites</b><br><br>
            I can help you with booking inquiries, and general FAQs.<br><br>
            Try asking something like "Why should I choose premiere suites?" or "What is included in a furnished apartment?" to get started.
          </span>
        </div>
      </div>
      <div class="chat-footer">
        <div class="typing-indicator" id="typing-indicator" style="display: none;">
          <div>Agent is typing</div>
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
        </div>
        <div class="input-row">
          <input type="text" placeholder="Send a message..." class="chat-input"/>
          <button class="send-btn" title="Send">➤</button>
        </div>
        <div class="powered-by">Powered By <a href="https://www.safqore.com" target="_blank">Safqore AI</a></div>
      </div>
    </div>
  `;
  document.body.appendChild(wrapper);

  function formatLLMResponse(text) {
    return text
      .replace(/(\s*<br>\s*)+/g, '<br>')
      .replace(/^##\s(.+)$/gm, '<h3>$1</h3>')
      .replace(/^###\s(.+)$/gm, '<h4>$1</h4>')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/^- (.+)$/gm, '<li>$1</li>')
      .replace(/^(\d+)\.\s(.+)$/gm, '<li>$2</li>')
      .replace(/<\/li>\n<li>/g, '</li><li>')
      .replace(/<li>.*<\/li>/g, '<ul>$&</ul>')
      .replace(/<\/ul>\n<ul>/g, '')
      .replace(/\n/g, '<br>');
  }
  
  const chatBubble = wrapper.querySelector('#chat-bubble');
  const chatWindow = wrapper.querySelector('#chat-window');
  const closeChat = wrapper.querySelector('#close-chat');
  const sendBtn = wrapper.querySelector('.send-btn');
  const chatInput = wrapper.querySelector('.chat-input');
  const chatBody = wrapper.querySelector('.chat-body');
  const typingIndicator = wrapper.querySelector('#typing-indicator');

  chatBubble.addEventListener('click', () => {
    chatBubble.style.opacity = '0';
    chatBubble.style.pointerEvents = 'none';
    chatWindow.classList.add('open');
    chatInput.focus();
  });
  
  closeChat.addEventListener('click', () => {
    chatWindow.classList.remove('open');
    setTimeout(() => {
      chatBubble.style.opacity = '1';
      chatBubble.style.pointerEvents = 'auto';
    }, 300);
  });

  function getLocalTimestamp() {
    const now = new Date();
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const day = days[now.getDay()];
    const hours = now.getHours().toString().padStart(2, '0');
    const minutes = now.getMinutes().toString().padStart(2, '0');
    return `${day} ${hours}:${minutes}`;
  }  

  async function handleUserMessage(userMsg) {
    const usertimestamp = getLocalTimestamp();

    // Add user message
    const userMsgElem = document.createElement('div');
    userMsgElem.className = 'chat-message user';
    userMsgElem.innerHTML = `<span>${userMsg}</span><div class="message-timestamp-user">Sent - ${usertimestamp}</div>`;
    chatBody.appendChild(userMsgElem);
    chatBody.scrollTop = chatBody.scrollHeight;
  
    typingIndicator.style.display = 'flex';
  
    // Simulate agent response
    const botReply = await window.getLLMResponse(userMsg);
  
    typingIndicator.style.display = 'none';
  
    // Add bot message
    const botMsgContainer = document.createElement('div');
    botMsgContainer.className = 'chat-message bot';
  
    const botMessageContent = document.createElement('div');
    botMessageContent.className = 'formatted-response';
    botMessageContent.innerHTML = formatLLMResponse(botReply);
  
    const timestamp = document.createElement('div');
    timestamp.className = 'message-timestamp-bot';
    timestamp.innerHTML = `Premiere Suites AI Assistant - ${new Date().toLocaleString('en-US', {
      weekday: 'short',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    })}`;
  
    botMsgContainer.appendChild(botMessageContent);
    chatBody.appendChild(botMsgContainer);
    chatBody.appendChild(timestamp);
    chatBody.scrollTop = chatBody.scrollHeight;
  }
  
  chatInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
      const userMsg = chatInput.value.trim();
      if (!userMsg) return;
      chatInput.value = '';
      handleUserMessage(userMsg);
    }
  });

  sendBtn.addEventListener('click', () => {
    const userMsg = chatInput.value.trim();
    if (!userMsg) return;
    chatInput.value = '';
    handleUserMessage(userMsg);
  });

  window.getLLMResponse = async function(userMessage) {
  try {
    // keep a persistent session id
    let sessionId = localStorage.getItem('safqore_sessionId');
    if (!sessionId) {
      sessionId = (typeof crypto !== 'undefined' && crypto.randomUUID) ? crypto.randomUUID() : `sess-${Date.now()}-${Math.floor(Math.random()*1e6)}`;
      localStorage.setItem('safqore_sessionId', sessionId);
    }

    const payload = [
      { sessionId, action: "sendMessage", chatInput: userMessage }
    ];
    const url = 'http://localhost:5678/webhook-test/chat-interface';

    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      credentials: 'omit'
    });

    // n8n returns JSON in the shape: [ { "output": "..." } ]
    const parsed = await res.json();
    if (Array.isArray(parsed) && parsed.length && typeof parsed[0].output === 'string') {
      return parsed[0].output;
    }
    if (parsed && typeof parsed.output === 'string') return parsed.output;

    return "Sorry, I didn't understand that.";
  } catch (err) {
    console.error('Error calling backend API:', err);
    return "An error occurred while fetching a response.";
  }
};

})();
