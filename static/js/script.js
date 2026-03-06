/**
 * AI Interview Platform - JavaScript
 * Handles form validation, voice input, chat interface, and UI interactions
 * Author: Senior Full-Stack Development Team
 * Version: 1.0
 */

// ==================== GLOBAL VARIABLES ====================

let recognition = null;
let isRecording = false;
let questionCount = 0;
let lastAIQuestion = ''; // Store the last AI question for repeat functionality

// ==================== DOCUMENT READY ====================

document.addEventListener('DOMContentLoaded', function() {
    console.log('AI Interview Platform initialized');
    
    // Initialize various features
    initializeFormValidation();
    initializeFileUpload();
    initializeVoiceRecognition();
    
    // Add smooth scrolling
    enableSmoothScrolling();
});

// ==================== FORM VALIDATION ====================

function initializeFormValidation() {
    // Registration form validation
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            if (!validateRegistrationForm()) {
                e.preventDefault();
            }
        });
        
        // Real-time password confirmation check
        const confirmPassword = document.getElementById('confirm_password');
        if (confirmPassword) {
            confirmPassword.addEventListener('input', function() {
                const password = document.getElementById('password').value;
                const confirm = this.value;
                
                if (confirm && password !== confirm) {
                    this.setCustomValidity('Passwords do not match');
                    this.style.borderColor = '#ef4444';
                } else {
                    this.setCustomValidity('');
                    this.style.borderColor = '#10b981';
                }
            });
        }
    }
    
    // Login form validation
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value;
            
            if (!username || !password) {
                e.preventDefault();
                showAlert('Please fill in all fields', 'error');
            }
        });
    }
    
    // Interview setup form
    const setupForm = document.getElementById('setupForm');
    if (setupForm) {
        setupForm.addEventListener('submit', function(e) {
            const role = document.querySelector('input[name="role"]:checked');
            const difficulty = document.querySelector('input[name="difficulty"]:checked');
            
            if (!role || !difficulty) {
                e.preventDefault();
                showAlert('Please select both role and difficulty', 'error');
            }
        });
    }
}

function validateRegistrationForm() {
    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    
    // Username validation
    if (username.length < 3) {
        showAlert('Username must be at least 3 characters', 'error');
        return false;
    }
    
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showAlert('Please enter a valid email address', 'error');
        return false;
    }
    
    // Password validation
    if (password.length < 6) {
        showAlert('Password must be at least 6 characters', 'error');
        return false;
    }
    
    // Password confirmation
    if (password !== confirmPassword) {
        showAlert('Passwords do not match', 'error');
        return false;
    }
    
    return true;
}

// ==================== FILE UPLOAD ====================

function initializeFileUpload() {
    const fileInput = document.getElementById('resume');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            const fileName = document.getElementById('fileName');
            
            if (file) {
                // Validate file size (16MB max)
                if (file.size > 16 * 1024 * 1024) {
                    showAlert('File size must be less than 16MB', 'error');
                    this.value = '';
                    return;
                }
                
                // Validate file type
                const validTypes = ['.pdf', '.doc', '.docx'];
                const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
                
                if (!validTypes.includes(fileExtension)) {
                    showAlert('Only PDF and DOCX files are allowed', 'error');
                    this.value = '';
                    return;
                }
                
                // Update filename display
                if (fileName) {
                    fileName.textContent = file.name;
                    fileName.style.color = '#10b981';
                }
            }
        });
    }
    
    // Upload form submission
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            const fileInput = document.getElementById('resume');
            if (!fileInput.files || !fileInput.files[0]) {
                e.preventDefault();
                showAlert('Please select a file to upload', 'error');
            }
        });
    }
}

// ==================== VOICE RECOGNITION ====================

function initializeVoiceRecognition() {
    const voiceBtn = document.getElementById('voiceBtn');
    
    if (!voiceBtn) return;
    
    // Check if browser supports speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        recognition.onstart = function() {
            isRecording = true;
            voiceBtn.textContent = '🔴';
            voiceBtn.style.backgroundColor = '#ef4444';
            showAlert('Listening... Speak now!', 'info');
        };
        
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            const userInput = document.getElementById('userInput');
            
            if (userInput) {
                userInput.value = transcript;
                userInput.style.borderColor = '#10b981';
            }
            
            showAlert('Speech captured successfully!', 'success');
        };
        
        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
            let errorMessage = 'Speech recognition error';
            
            switch(event.error) {
                case 'no-speech':
                    errorMessage = 'No speech detected. Please try again.';
                    break;
                case 'audio-capture':
                    errorMessage = 'Microphone not found or permission denied.';
                    break;
                case 'not-allowed':
                    errorMessage = 'Microphone permission denied.';
                    break;
                default:
                    errorMessage = 'Speech recognition failed: ' + event.error;
            }
            
            showAlert(errorMessage, 'error');
        };
        
        recognition.onend = function() {
            isRecording = false;
            voiceBtn.textContent = '🎤';
            voiceBtn.style.backgroundColor = '';
        };
        
        // Voice button click handler
        voiceBtn.addEventListener('click', function() {
            if (isRecording) {
                recognition.stop();
            } else {
                recognition.start();
            }
        });
        
    } else {
        // Voice recognition not supported
        voiceBtn.disabled = true;
        voiceBtn.title = 'Voice input not supported in this browser';
        voiceBtn.style.opacity = '0.5';
        console.warn('Speech recognition not supported in this browser');
    }
}

// ==================== TEXT-TO-SPEECH (AI VOICE) ====================

/**
 * Converts text to speech using Web Speech API
 * @param {string} text - The text to be spoken by the AI
 */
function speakText(text) {
    if (!text || text.trim() === '') {
        console.warn('No text provided for speech synthesis');
        return;
    }
    
    // Check if browser supports speech synthesis
    if (!('speechSynthesis' in window)) {
        console.warn('Speech synthesis not supported in this browser');
        return;
    }
    
    // Create speech synthesis utterance
    const speech = new SpeechSynthesisUtterance();
    speech.text = text;
    speech.lang = "en-US";  // English (US)
    speech.rate = 1;        // Normal speed
    speech.pitch = 1;       // Normal pitch
    speech.volume = 1;      // Full volume
    
    // Cancel any ongoing speech before starting new one
    window.speechSynthesis.cancel();
    
    // Speak the text
    window.speechSynthesis.speak(speech);
    
    // Optional: Log speech events for debugging
    speech.onstart = function() {
        console.log('AI voice started speaking');
    };
    
    speech.onend = function() {
        console.log('AI voice finished speaking');
    };
    
    speech.onerror = function(event) {
        console.error('Speech synthesis error:', event.error);
    };
}

/**
 * Repeats the last AI question
 */
function repeatQuestion() {
    if (!lastAIQuestion || lastAIQuestion.trim() === '') {
        showAlert('No question to repeat', 'warning');
        return;
    }
    
    // Speak the last AI question again
    speakText(lastAIQuestion);
    showAlert('Repeating question...', 'info');
}

/**
 * Stops any ongoing speech
 */
function stopVoice() {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        console.log('AI voice stopped');
    }
}

// ==================== INTERVIEW CHAT INTERFACE ====================

function initializeInterviewChat() {
    const sendBtn = document.getElementById('sendBtn');
    const userInput = document.getElementById('userInput');
    const endInterviewBtn = document.getElementById('endInterviewBtn');
    
    // Load chat history when page loads
    loadChatHistory();
    
    // Send message on button click
    if (sendBtn) {
        sendBtn.addEventListener('click', sendMessage);
    }
    
    // Send message on Enter key (Ctrl+Enter for new line)
    if (userInput) {
        userInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
    
    // End interview button
    if (endInterviewBtn) {
        endInterviewBtn.addEventListener('click', function() {
            document.getElementById('endInterviewModal').classList.add('active');
        });
    }
    
    // Modal buttons
    const cancelEndBtn = document.getElementById('cancelEndBtn');
    const confirmEndBtn = document.getElementById('confirmEndBtn');
    const modal = document.getElementById('endInterviewModal');
    
    if (cancelEndBtn) {
        cancelEndBtn.addEventListener('click', function() {
            modal.classList.remove('active');
        });
    }
    
    if (confirmEndBtn) {
        confirmEndBtn.addEventListener('click', endInterview);
    }
    
    // Close modal on outside click
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    }
}

async function loadChatHistory() {
    try {
        const response = await fetch('/get_chat_history');
        const data = await response.json();
        
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
            chatMessages.innerHTML = '';
            
            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(msg => {
                    // Don't speak historical messages, only new ones
                    displayMessage(msg.sender, msg.message, msg.timestamp, false);
                });
                
                // Scroll to bottom
                scrollToBottom();
            }
        }
    } catch (error) {
        console.error('Error loading chat history:', error);
        showAlert('Failed to load chat history', 'error');
    }
}

async function sendMessage() {
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    
    if (!userInput || !userInput.value.trim()) {
        showAlert('Please enter a message', 'warning');
        return;
    }
    
    const message = userInput.value.trim();
    
    // Disable input while processing
    userInput.disabled = true;
    sendBtn.disabled = true;
    sendBtn.textContent = 'Sending...';
    
    try {
        // Display user message immediately
        displayMessage('Student', message);
        userInput.value = '';
        
        // Show typing indicator
        showTypingIndicator();
        
        // Send to server
        const response = await fetch('/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        });
        
        if (!response.ok) {
            throw new Error('Failed to send message');
        }
        
        const data = await response.json();
        
        // Remove typing indicator
        hideTypingIndicator();
        
        // Display AI response
        displayMessage('AI', data.response);
        
        // Increment question count
        questionCount++;
        
    } catch (error) {
        console.error('Error sending message:', error);
        hideTypingIndicator();
        showAlert('Failed to send message. Please try again.', 'error');
    } finally {
        // Re-enable input
        userInput.disabled = false;
        sendBtn.disabled = false;
        sendBtn.textContent = 'Send Answer';
        userInput.focus();
    }
}

function displayMessage(sender, message, timestamp, speak = true) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = sender === 'AI' ? 'message message-ai' : 'message message-student';
    
    const now = timestamp ? new Date(timestamp) : new Date();
    const timeStr = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="message-sender">${sender === 'AI' ? '🤖 AI Interviewer' : '👤 You'}</div>
            <div class="message-text">${escapeHtml(message)}</div>
            <div class="message-time">${timeStr}</div>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
    
    // *** AI VOICE FEATURE ***
    // If the message is from AI and speak is enabled, automatically speak it aloud
    if (sender === 'AI' && speak) {
        lastAIQuestion = message; // Store for repeat functionality
        speakText(message); // Automatically speak the AI question
    } else if (sender === 'AI' && !speak) {
        // Still store the question even if not speaking (for history loading)
        lastAIQuestion = message;
    }
}

function showTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typingIndicator';
    typingDiv.className = 'message message-ai';
    typingDiv.innerHTML = `
        <div class="message-content">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(typingDiv);
    scrollToBottom();
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function scrollToBottom() {
    const chatWindow = document.getElementById('chatWindow');
    if (chatWindow) {
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
}

async function endInterview() {
    const modal = document.getElementById('endInterviewModal');
    const confirmBtn = document.getElementById('confirmEndBtn');
    
    if (confirmBtn) {
        confirmBtn.disabled = true;
        confirmBtn.textContent = 'Processing...';
    }
    
    try {
        const response = await fetch('/end_interview', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to end interview');
        }
        
        const data = await response.json();
        
        if (data.success) {
            // Redirect to results page
            window.location.href = '/results/' + data.interview_id;
        } else {
            throw new Error('Failed to process interview results');
        }
        
    } catch (error) {
        console.error('Error ending interview:', error);
        showAlert('Failed to end interview. Please try again.', 'error');
        
        if (confirmBtn) {
            confirmBtn.disabled = false;
            confirmBtn.textContent = 'End & Evaluate';
        }
        
        if (modal) {
            modal.classList.remove('active');
        }
    }
}

// ==================== ALERT SYSTEM ====================

function showAlert(message, type = 'info') {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert-floating');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create new alert
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-floating`;
    alert.textContent = message;
    alert.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        z-index: 10000;
        min-width: 300px;
        max-width: 500px;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        animation: slideInRight 0.3s ease;
    `;
    
    document.body.appendChild(alert);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        alert.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => alert.remove(), 300);
    }, 5000);
}

// Add CSS animations for alerts
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideOutRight {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100px);
        }
    }
`;
document.head.appendChild(style);

// ==================== UTILITY FUNCTIONS ====================

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function enableSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// ==================== ROLE/DIFFICULTY CARD ANIMATIONS ====================

document.addEventListener('DOMContentLoaded', function() {
    // Add click animation to role cards
    const roleCards = document.querySelectorAll('.role-card, .difficulty-card');
    roleCards.forEach(card => {
        card.addEventListener('click', function() {
            // Remove active class from siblings
            const siblings = this.parentElement.querySelectorAll('.role-card, .difficulty-card');
            siblings.forEach(sibling => {
                if (sibling !== this) {
                    sibling.classList.remove('active-card');
                }
            });
            
            // Add active class to clicked card
            this.classList.add('active-card');
        });
    });
});

// ==================== PROGRESS CHART HELPER ====================

function createProgressChart(chartData) {
    // This function is called from the progress.html template
    // Chart.js is loaded via CDN in the template
    console.log('Chart data loaded:', chartData);
}

// ==================== AUTO-SAVE DRAFT (Feature Enhancement) ====================

let draftTimer = null;

function enableAutoSave() {
    const userInput = document.getElementById('userInput');
    
    if (userInput) {
        userInput.addEventListener('input', function() {
            // Clear existing timer
            if (draftTimer) {
                clearTimeout(draftTimer);
            }
            
            // Set new timer to save draft after 2 seconds of inactivity
            draftTimer = setTimeout(() => {
                const draft = userInput.value;
                if (draft) {
                    localStorage.setItem('interview_draft', draft);
                    console.log('Draft saved');
                }
            }, 2000);
        });
        
        // Load saved draft on page load
        const savedDraft = localStorage.getItem('interview_draft');
        if (savedDraft) {
            userInput.value = savedDraft;
            console.log('Draft restored');
        }
        
        // Clear draft when message is sent
        const sendBtn = document.getElementById('sendBtn');
        if (sendBtn) {
            sendBtn.addEventListener('click', () => {
                localStorage.removeItem('interview_draft');
            });
        }
    }
}

// Initialize auto-save if on interview page
if (window.location.pathname.includes('/interview_chat')) {
    enableAutoSave();
}

// ==================== KEYBOARD SHORTCUTS ====================

document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to send message
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const sendBtn = document.getElementById('sendBtn');
        if (sendBtn && !sendBtn.disabled) {
            sendMessage();
        }
    }
    
    // Escape to close modal
    if (e.key === 'Escape') {
        const modal = document.getElementById('endInterviewModal');
        if (modal && modal.classList.contains('active')) {
            modal.classList.remove('active');
        }
    }
});

// ==================== PAGE VISIBILITY API ====================

document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        console.log('Page hidden - pausing updates');
    } else {
        console.log('Page visible - resuming updates');
        // Reload chat history if on interview page
        if (window.location.pathname.includes('/interview_chat')) {
            loadChatHistory();
        }
    }
});

// ==================== ERROR HANDLING ====================

window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    // Don't show alerts for minor errors
    // showAlert('An error occurred. Please refresh the page.', 'error');
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
});

// ==================== EXPORT FOR TESTING ====================

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        validateRegistrationForm,
        escapeHtml,
        showAlert
    };
}

console.log('JavaScript initialized successfully! 🚀');
