/**
 * SimpleChatbot - Chat Interface JavaScript
 * Handles message sending, model switching, and UI interactions.
 */

(function () {
    'use strict';

    // ---------------------------------------------------------------------------
    // DOM Elements
    // ---------------------------------------------------------------------------

    const chatArea = document.getElementById('chat-area');
    const messageInput = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');
    const clearBtn = document.getElementById('clear-btn');
    const modelSelect = document.getElementById('model-select');
    const welcomeMessage = document.getElementById('welcome-message');

    // ---------------------------------------------------------------------------
    // State
    // ---------------------------------------------------------------------------

    let isLoading = false;

    // ---------------------------------------------------------------------------
    // API Functions
    // ---------------------------------------------------------------------------

    /**
     * Send a chat message to the API and get a response.
     * @param {string} message - The user's message text.
     * @returns {Promise<Object>} The API response data.
     */
    async function sendMessage(message) {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to get response from server.');
        }

        return data;
    }

    /**
     * Switch the active model.
     * @param {string} modelKey - The model key to switch to.
     * @returns {Promise<Object>} The API response data.
     */
    async function switchModel(modelKey) {
        const response = await fetch('/api/model', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model_key: modelKey }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to switch model.');
        }

        return data;
    }

    /**
     * Clear the conversation history.
     * @returns {Promise<Object>} The API response data.
     */
    async function clearHistory() {
        const response = await fetch('/api/history', {
            method: 'DELETE',
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to clear history.');
        }

        return data;
    }

    // ---------------------------------------------------------------------------
    // UI Functions
    // ---------------------------------------------------------------------------

    /**
     * Add a message bubble to the chat area.
     * @param {string} content - The message content (supports basic markdown).
     * @param {string} role - 'user' or 'assistant'.
     */
    function addMessage(content, role) {
        // Hide welcome message on first interaction
        if (welcomeMessage) {
            welcomeMessage.style.display = 'none';
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${role}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = role === 'user' ? 'U' : 'AI';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        if (role === 'assistant') {
            contentDiv.innerHTML = formatMarkdown(content);
        } else {
            contentDiv.textContent = content;
        }

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(contentDiv);
        chatArea.appendChild(messageDiv);

        scrollToBottom();
    }

    /**
     * Show the loading indicator in the chat area.
     */
    function showLoading() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'loading-indicator';
        loadingDiv.id = 'loading-indicator';

        loadingDiv.innerHTML = `
            <div class="message-avatar" style="background: var(--color-orange); color: var(--color-primary);">AI</div>
            <div>
                <div class="loading-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
                <div class="loading-text">Thinking...</div>
            </div>
        `;

        chatArea.appendChild(loadingDiv);
        scrollToBottom();
    }

    /**
     * Remove the loading indicator from the chat area.
     */
    function hideLoading() {
        const loading = document.getElementById('loading-indicator');
        if (loading) {
            loading.remove();
        }
    }

    /**
     * Show an error toast notification.
     * @param {string} message - The error message to display.
     */
    function showToast(message) {
        // Remove existing toast if any
        const existing = document.querySelector('.toast');
        if (existing) {
            existing.remove();
        }

        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        document.body.appendChild(toast);

        // Trigger animation
        requestAnimationFrame(() => {
            toast.classList.add('show');
        });

        // Auto-remove after 5 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }

    /**
     * Scroll the chat area to the bottom.
     */
    function scrollToBottom() {
        requestAnimationFrame(() => {
            chatArea.scrollTop = chatArea.scrollHeight;
        });
    }

    /**
     * Set the loading state of the UI.
     * @param {boolean} loading - Whether the UI should be in loading state.
     */
    function setLoading(loading) {
        isLoading = loading;
        sendBtn.disabled = loading;
        messageInput.disabled = loading;

        if (loading) {
            sendBtn.textContent = '...';
        } else {
            sendBtn.textContent = 'Send';
            messageInput.focus();
        }
    }

    /**
     * Format basic markdown to HTML for display.
     * @param {string} text - The raw text with markdown.
     * @returns {string} HTML string.
     */
    function formatMarkdown(text) {
        let html = text;

        // Escape HTML entities first
        html = html.replace(/&/g, '&amp;')
                   .replace(/</g, '&lt;')
                   .replace(/>/g, '&gt;');

        // Code blocks (triple backticks)
        html = html.replace(/```(\w*)\n?([\s\S]*?)```/g, function (match, lang, code) {
            return `<pre><code>${code.trim()}</code></pre>`;
        });

        // Inline code
        html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

        // Bold
        html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

        // Italic
        html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

        // Headers
        html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
        html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
        html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');

        // Unordered lists
        html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
        html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');

        // Ordered lists
        html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');

        // Blockquotes
        html = html.replace(/^&gt; (.+)$/gm, '<blockquote>$1</blockquote>');

        // Links
        html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');

        // Paragraphs (double newline)
        html = html.replace(/\n\n/g, '</p><p>');

        // Single newlines to <br>
        html = html.replace(/\n/g, '<br>');

        // Wrap in paragraph if not already wrapped
        if (!html.startsWith('<')) {
            html = `<p>${html}</p>`;
        }

        return html;
    }

    /**
     * Auto-resize the textarea based on content.
     */
    function autoResize() {
        messageInput.style.height = 'auto';
        const newHeight = Math.min(messageInput.scrollHeight, 150);
        messageInput.style.height = newHeight + 'px';
    }

    // ---------------------------------------------------------------------------
    // Event Handlers
    // ---------------------------------------------------------------------------

    /**
     * Handle sending a message.
     */
    async function handleSend() {
        const message = messageInput.value.trim();

        if (!message || isLoading) {
            return;
        }

        // Add user message to UI
        addMessage(message, 'user');
        messageInput.value = '';
        messageInput.style.height = 'auto';

        // Show loading and disable input
        setLoading(true);
        showLoading();

        try {
            const data = await sendMessage(message);
            hideLoading();
            addMessage(data.response, 'assistant');
        } catch (error) {
            hideLoading();
            showToast(error.message);
        } finally {
            setLoading(false);
        }
    }

    /**
     * Handle model switch.
     */
    async function handleModelSwitch() {
        const modelKey = modelSelect.value;

        try {
            const data = await switchModel(modelKey);
            showToast(`Switched to ${data.model.name}`);
        } catch (error) {
            showToast(error.message);
            // Revert select to previous value
            modelSelect.value = modelSelect.dataset.previousValue || modelSelect.value;
        }
    }

    /**
     * Handle clearing conversation history.
     */
    async function handleClear() {
        try {
            await clearHistory();

            // Clear UI messages
            const messages = chatArea.querySelectorAll('.message, .loading-indicator');
            messages.forEach(msg => msg.remove());

            // Show welcome message again
            if (welcomeMessage) {
                welcomeMessage.style.display = 'flex';
            }
        } catch (error) {
            showToast(error.message);
        }
    }

    // ---------------------------------------------------------------------------
    // Event Listeners
    // ---------------------------------------------------------------------------

    // Send button click
    sendBtn.addEventListener('click', handleSend);

    // Enter key to send (Shift+Enter for newline)
    messageInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    });

    // Auto-resize textarea
    messageInput.addEventListener('input', autoResize);

    // Model selector change
    modelSelect.addEventListener('focus', function () {
        this.dataset.previousValue = this.value;
    });
    modelSelect.addEventListener('change', handleModelSwitch);

    // Clear button
    clearBtn.addEventListener('click', handleClear);

    // Focus input on load
    messageInput.focus();

})();
