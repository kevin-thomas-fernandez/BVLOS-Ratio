// Global state
let queriesCount = 0;
let isProcessing = false;

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const queriesCountEl = document.getElementById('queriesCount');
const totalRulesEl = document.getElementById('totalRules');
const categoriesListEl = document.getElementById('categoriesList');

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    loadCategories();
    loadTotalRules();
    setupEventListeners();
    autoResizeTextarea();
});

// Setup event listeners
function setupEventListeners() {
    // Send button click
    sendBtn.addEventListener('click', sendMessage);
    
    // Enter key to send (Shift+Enter for new line)
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Example query buttons
    document.querySelectorAll('.example-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            userInput.value = btn.dataset.query;
            sendMessage();
        });
    });
}

// Auto-resize textarea
function autoResizeTextarea() {
    userInput.addEventListener('input', () => {
        userInput.style.height = 'auto';
        userInput.style.height = userInput.scrollHeight + 'px';
    });
}

// Send message
async function sendMessage(summaryPreference = null) {
    const query = userInput.value.trim();
    
    if (!query || isProcessing) return;
    
    isProcessing = true;
    sendBtn.disabled = true;
    
    // Clear input
    userInput.value = '';
    userInput.style.height = 'auto';
    
    // Remove welcome message if exists
    const welcomeMsg = document.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    // Add user message (only if not a summary preference selection)
    if (summaryPreference === null) {
        addMessage(query, 'user');
    }
    
    // Add typing indicator
    const typingId = addTypingIndicator();
    
    try {
        // Send request to backend
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                query: query,
                summary_preference: summaryPreference
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to get response');
        }
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator(typingId);
        
        // Check if we need to ask for summary preference
        if (data.ask_summary_preference) {
            addSummaryPreferencePrompt(data.query, data.relevant_rules);
        } else {
            // Add bot response
            addMessage(data.response, 'bot', data.relevant_rules, data.follow_ups);
            
            // Update query count
            queriesCount++;
            queriesCountEl.textContent = queriesCount;
        }
        
    } catch (error) {
        console.error('Error:', error);
        removeTypingIndicator(typingId);
        addMessage('Sorry, I encountered an error processing your request. Please try again.', 'bot');
    } finally {
        isProcessing = false;
        sendBtn.disabled = false;
        userInput.focus();
    }
}

// Add summary preference prompt
function addSummaryPreferencePrompt(query, relevantRules) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    messageDiv.id = 'summary-preference-' + Date.now();
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = '🤖';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    messageContent.innerHTML = `
        <p><strong>How would you like your answer?</strong></p>
        <p style="margin-top: 0.5rem; color: var(--text-secondary); font-size: 0.875rem;">
            Choose your preferred summary length:
        </p>
    `;
    
    const buttonsContainer = document.createElement('div');
    buttonsContainer.className = 'summary-preference-buttons';
    buttonsContainer.style.marginTop = '1rem';
    
    const shortBtn = document.createElement('button');
    shortBtn.className = 'summary-preference-btn';
    shortBtn.textContent = '📝 Short Summary';
    shortBtn.addEventListener('click', () => {
        userInput.value = query;
        sendMessage('short');
        messageDiv.remove();
    });
    
    const detailedBtn = document.createElement('button');
    detailedBtn.className = 'summary-preference-btn';
    detailedBtn.textContent = '📚 Detailed Explanation';
    detailedBtn.addEventListener('click', () => {
        userInput.value = query;
        sendMessage('detailed');
        messageDiv.remove();
    });
    
    buttonsContainer.appendChild(shortBtn);
    buttonsContainer.appendChild(detailedBtn);
    messageContent.appendChild(buttonsContainer);
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Add message to chat
function addMessage(content, type, relevantRules = null, followUps = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = type === 'user' ? '👤' : '🤖';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    // Format content with markdown-like support
    const formattedContent = formatMessage(content);
    messageContent.innerHTML = formattedContent;
    
    // Add relevant rules if available
    if (relevantRules && relevantRules.length > 0) {
        const rulesSection = document.createElement('div');
        rulesSection.className = 'relevant-rules';
        rulesSection.innerHTML = '<h4>📋 Referenced Regulations:</h4>';
        
        relevantRules.forEach(rule => {
            const ruleItem = document.createElement('div');
            ruleItem.className = 'rule-item';
            ruleItem.innerHTML = `
                <strong>Rule ${rule.rule_number}</strong> - ${rule.title}
                <span class="rule-category">${rule.category}</span>
            `;
            rulesSection.appendChild(ruleItem);
        });
        
        messageContent.appendChild(rulesSection);
    }
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);
    
    chatMessages.appendChild(messageDiv);
    
    // Add follow-up buttons after bot messages
    if (type === 'bot' && followUps && followUps.length > 0) {
        addFollowUpButtons(followUps);
    }
    
    scrollToBottom();
}

// Add follow-up question buttons
function addFollowUpButtons(followUps) {
    const followUpDiv = document.createElement('div');
    followUpDiv.className = 'follow-up-options';
    
    const header = document.createElement('h5');
    header.textContent = '💡 Suggested follow-ups:';
    followUpDiv.appendChild(header);
    
    const buttonsContainer = document.createElement('div');
    buttonsContainer.className = 'follow-up-buttons';
    
    followUps.forEach(followUp => {
        const btn = document.createElement('button');
        btn.className = 'follow-up-btn';
        btn.textContent = followUp;
        btn.addEventListener('click', () => {
            userInput.value = followUp;
            sendMessage();
        });
        buttonsContainer.appendChild(btn);
    });
    
    followUpDiv.appendChild(buttonsContainer);
    chatMessages.appendChild(followUpDiv);
    scrollToBottom();
}

// Format message with basic markdown support
function formatMessage(text) {
    // Bold
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Code blocks
    text = text.replace(/```(.*?)```/gs, '<pre><code>$1</code></pre>');
    
    // Inline code
    text = text.replace(/`(.*?)`/g, '<code>$1</code>');
    
    // Line breaks
    text = text.replace(/\n/g, '<br>');
    
    // Lists
    text = text.replace(/^- (.*?)$/gm, '<li>$1</li>');
    text = text.replace(/(<li>.*?<\/li>)/s, '<ul>$1</ul>');
    
    return text;
}

// Add typing indicator
function addTypingIndicator() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    messageDiv.id = 'typing-indicator-' + Date.now();
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = '🤖';
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message-content';
    typingDiv.innerHTML = `
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(typingDiv);
    chatMessages.appendChild(messageDiv);
    
    scrollToBottom();
    return messageDiv.id;
}

// Remove typing indicator
function removeTypingIndicator(id) {
    const indicator = document.getElementById(id);
    if (indicator) {
        indicator.remove();
    }
}

// Scroll to bottom of chat with smooth scrolling
function scrollToBottom() {
    chatMessages.scrollTo({
        top: chatMessages.scrollHeight,
        behavior: 'smooth'
    });
}

// Load categories
async function loadCategories() {
    try {
        const response = await fetch('/api/categories');
        const data = await response.json();
        
        if (data.categories) {
            categoriesListEl.innerHTML = '';
            data.categories.forEach(category => {
                const categoryDiv = document.createElement('div');
                categoryDiv.className = 'category-item';
                categoryDiv.innerHTML = `
                    <span>📁 ${formatCategoryName(category)}</span>
                `;
                categoryDiv.addEventListener('click', () => {
                    userInput.value = `What are the regulations for ${category}?`;
                    sendMessage();
                });
                categoriesListEl.appendChild(categoryDiv);
            });
        }
    } catch (error) {
        console.error('Error loading categories:', error);
        categoriesListEl.innerHTML = '<div class="loading">Failed to load categories</div>';
    }
}

// Load total rules count
async function loadTotalRules() {
    try {
        const response = await fetch('/api/rules');
        const data = await response.json();
        
        if (data.total !== undefined) {
            totalRulesEl.textContent = data.total;
        }
    } catch (error) {
        console.error('Error loading rules count:', error);
    }
}

// Format category name
function formatCategoryName(category) {
    return category
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

// Handle errors gracefully
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
});

// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K to focus input
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        userInput.focus();
    }
});

// Add some helpful animations
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
`;
document.head.appendChild(style);
