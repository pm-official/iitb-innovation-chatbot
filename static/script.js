// IIC Innovation Advisor — Chat Logic

const chatContainer = document.getElementById('chatContainer');
const messagesDiv = document.getElementById('messages');
const welcomeScreen = document.getElementById('welcomeScreen');
const queryInput = document.getElementById('queryInput');
const sendBtn = document.getElementById('sendBtn');

let chatHistory = [];
let isLoading = false;

// Auto-resize textarea
function autoResize(el) {
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}

// Handle Enter key (Shift+Enter for new line)
function handleKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
}

// Send a starter question
function sendStarter(btn) {
    queryInput.value = btn.textContent;
    sendMessage();
}

// Simple markdown to HTML (handles common patterns)
function renderMarkdown(text) {
    let html = text
        // Escape HTML
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        // Headers
        .replace(/^### (.+)$/gm, '<h3>$1</h3>')
        .replace(/^## (.+)$/gm, '<h2>$1</h2>')
        .replace(/^# (.+)$/gm, '<h1>$1</h1>')
        // Bold and italic
        .replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        // Inline code
        .replace(/`(.+?)`/g, '<code>$1</code>')
        // Links
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
        // Horizontal rule
        .replace(/^---$/gm, '<hr>')
        // Blockquote
        .replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>');

    // Process bullet lists
    html = html.replace(/^(\s*[-*] .+\n?)+/gm, function(match) {
        const items = match.trim().split('\n')
            .map(line => line.replace(/^\s*[-*] /, '').trim())
            .filter(Boolean)
            .map(item => `<li>${item}</li>`)
            .join('');
        return `<ul>${items}</ul>`;
    });

    // Process numbered lists
    html = html.replace(/^(\s*\d+\. .+\n?)+/gm, function(match) {
        const items = match.trim().split('\n')
            .map(line => line.replace(/^\s*\d+\. /, '').trim())
            .filter(Boolean)
            .map(item => `<li>${item}</li>`)
            .join('');
        return `<ol>${items}</ol>`;
    });

    // Paragraphs (double newlines)
    html = html
        .split(/\n\n+/)
        .map(block => {
            block = block.trim();
            if (!block) return '';
            // Don't wrap if already an HTML block element
            if (/^<(h[1-3]|ul|ol|blockquote|hr|div)/.test(block)) return block;
            return `<p>${block.replace(/\n/g, '<br>')}</p>`;
        })
        .join('');

    return html;
}

// Add a message to the UI
function addMessage(role, content, sources) {
    welcomeScreen.style.display = 'none';

    const msg = document.createElement('div');
    msg.className = `message ${role}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? 'You' : 'IIC';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';

    if (role === 'bot') {
        bubble.innerHTML = renderMarkdown(content);
    } else {
        bubble.textContent = content;
    }

    contentDiv.appendChild(bubble);

    // Add sources for bot messages
    if (role === 'bot' && sources && sources.length > 0) {
        const sourcesDiv = document.createElement('div');
        sourcesDiv.className = 'sources';

        const toggle = document.createElement('button');
        toggle.className = 'sources-toggle';
        toggle.innerHTML = `📎 ${sources.length} sources <span>▸</span>`;
        toggle.onclick = () => {
            list.classList.toggle('open');
            toggle.querySelector('span').textContent = list.classList.contains('open') ? '▾' : '▸';
        };

        const list = document.createElement('div');
        list.className = 'sources-list';

        sources.forEach(src => {
            const item = document.createElement('div');
            item.className = 'source-item';

            const cat = document.createElement('span');
            cat.className = 'category';
            cat.textContent = src.category;

            item.appendChild(cat);

            if (src.url) {
                const link = document.createElement('a');
                link.href = src.url;
                link.target = '_blank';
                link.rel = 'noopener';
                link.textContent = src.file;
                item.appendChild(link);
            } else {
                const name = document.createElement('span');
                name.textContent = src.file;
                item.appendChild(name);
            }

            list.appendChild(item);
        });

        sourcesDiv.appendChild(toggle);
        sourcesDiv.appendChild(list);
        contentDiv.appendChild(sourcesDiv);
    }

    msg.appendChild(avatar);
    msg.appendChild(contentDiv);
    messagesDiv.appendChild(msg);

    scrollToBottom();
    return msg;
}

// Add typing indicator
function addTypingIndicator() {
    const msg = document.createElement('div');
    msg.className = 'message bot';
    msg.id = 'typingIndicator';

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = 'IIC';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';

    contentDiv.appendChild(bubble);
    msg.appendChild(avatar);
    msg.appendChild(contentDiv);
    messagesDiv.appendChild(msg);
    scrollToBottom();
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) indicator.remove();
}

function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Main send function
async function sendMessage() {
    const query = queryInput.value.trim();
    if (!query || isLoading) return;

    isLoading = true;
    sendBtn.disabled = true;
    queryInput.value = '';
    queryInput.style.height = 'auto';

    // Add user message
    addMessage('user', query);
    chatHistory.push({ role: 'user', content: query });

    // Show typing indicator
    addTypingIndicator();

    try {
        const resp = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: query,
                history: chatHistory.slice(-8),
            }),
        });

        if (!resp.ok) {
            throw new Error(`Server error: ${resp.status}`);
        }

        const data = await resp.json();

        removeTypingIndicator();
        addMessage('bot', data.answer, data.sources);
        chatHistory.push({ role: 'assistant', content: data.answer });

    } catch (err) {
        removeTypingIndicator();
        addMessage('bot', `Sorry, something went wrong. Please try again.\n\nError: ${err.message}`);
        console.error('Chat error:', err);
    }

    isLoading = false;
    sendBtn.disabled = false;
    queryInput.focus();
}

// Focus input on load
queryInput.focus();
