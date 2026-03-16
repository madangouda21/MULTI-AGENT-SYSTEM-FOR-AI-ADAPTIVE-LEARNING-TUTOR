/**
 * AI Adaptive Learning Tutor - Frontend Application
 * Connects to FastAPI backend for AI-powered learning
 */

// API Base URL
const API_BASE = 'http://localhost:8000';

// State
let chatHistory = [];
let currentQuiz = null;
let factIndex = 0;
let factInterval = null;

// Educational Fun Facts
const educationalFacts = [
    "🧠 The human brain can process images in just 13 milliseconds!",
    "📚 Reading for 6 minutes can reduce stress by up to 68%.",
    "💡 Thomas Edison made 1,000 unsuccessful attempts before inventing the light bulb.",
    "🎵 Learning music can improve math skills by up to 20%.",
    "🌍 There are more possible iterations of a chess game than atoms in the observable universe.",
    "🐙 An octopus has three hearts and blue blood!",
    "🚀 A day on Venus is longer than a year on Venus.",
    "🧬 Humans share 60% of their DNA with bananas.",
    "📖 The word 'algorithm' comes from the Persian mathematician Al-Khwarizmi.",
    "💻 The first computer programmer was Ada Lovelace in the 1840s.",
    "🎨 The color orange was named after the fruit, not the other way around.",
    "🌊 There's enough water in Lake Superior to cover all of North and South America in one foot of water.",
    "⚡ Lightning strikes Earth about 8 million times per day.",
    "🦋 A group of butterflies is called a 'kaleidoscope'.",
    "🌙 The Moon is slowly drifting away from Earth at 3.8 cm per year.",
    "🧪 Water can boil and freeze at the same time (triple point).",
    "🎓 Finland has no standardized tests until age 16, yet has top education.",
    "🌳 Trees can communicate and share nutrients through underground fungal networks.",
    "🔢 The number 0 was invented in India around the 5th century.",
    "🌈 A rainbow is actually a full circle, but we only see half from the ground."
];

// Topics by subject
const topicsBySubject = {
    'Mathematics': ['Quadratic Equations', 'Linear Algebra', 'Calculus', 'Statistics'],
    'Physics': ["Newton's Laws", 'Thermodynamics', 'Electromagnetism', 'Quantum Mechanics'],
    'Computer Science': ['Python Basics', 'Data Structures', 'Algorithms', 'Machine Learning'],
    'Biology': ['Photosynthesis', 'Cell Biology', 'Genetics', 'Evolution'],
    'Chemistry': ['Periodic Table', 'Chemical Bonds', 'Reactions', 'Organic Chemistry']
};

// Curated CS Resources
const csResources = {
    'Data Structures': [
        { name: 'GeeksforGeeks', url: 'https://www.geeksforgeeks.org/data-structures/' },
        { name: 'Visualgo', url: 'https://visualgo.net/' },
        { name: 'CP-Algorithms', url: 'https://cp-algorithms.com/' }
    ],
    'Algorithms': [
        { name: 'CP-Algorithms', url: 'https://cp-algorithms.com/' },
        { name: 'GeeksforGeeks', url: 'https://www.geeksforgeeks.org/fundamentals-of-algorithms/' }
    ],
    'Python Basics': [
        { name: 'W3Schools Python', url: 'https://www.w3schools.com/python/' },
        { name: 'GeeksforGeeks Python', url: 'https://www.geeksforgeeks.org/python-programming-language/' }
    ],
    'Machine Learning': [
        { name: 'scikit-learn Docs', url: 'https://scikit-learn.org/stable/' },
        { name: 'GeeksforGeeks ML', url: 'https://www.geeksforgeeks.org/machine-learning/' }
    ]
};

// ========================================
// Initialization
// ========================================

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initThemeToggle();
    initSubjectTopics();
    initDurationSlider();
    checkApiStatus();
});

// ========================================
// Navigation
// ========================================

function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.dataset.page;
            navigateTo(page);
            
            // Close sidebar on mobile after navigation
            if (window.innerWidth <= 992) {
                closeSidebar();
            }
        });
    });
}

function navigateTo(page) {
    // Update nav
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.page === page);
    });
    
    // Update pages
    document.querySelectorAll('.page').forEach(p => {
        p.classList.toggle('active', p.id === `page-${page}`);
    });
}

// Mobile sidebar toggle
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    const menuBtn = document.querySelector('.mobile-menu-btn i');
    
    sidebar.classList.toggle('active');
    overlay.classList.toggle('active');
    
    // Toggle icon
    if (sidebar.classList.contains('active')) {
        menuBtn.classList.remove('fa-bars');
        menuBtn.classList.add('fa-times');
    } else {
        menuBtn.classList.remove('fa-times');
        menuBtn.classList.add('fa-bars');
    }
}

function closeSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    const menuBtn = document.querySelector('.mobile-menu-btn i');
    
    sidebar.classList.remove('active');
    overlay.classList.remove('active');
    menuBtn.classList.remove('fa-times');
    menuBtn.classList.add('fa-bars');
}

// ========================================
// Theme Toggle
// ========================================

function initThemeToggle() {
    const themeBtn = document.getElementById('theme-btn');
    const savedTheme = localStorage.getItem('theme') || 'light';
    
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        document.body.classList.remove('light-mode');
    }
    
    themeBtn.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        document.body.classList.toggle('light-mode');
        
        const isDark = document.body.classList.contains('dark-mode');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });
}

// ========================================
// Subject & Topics
// ========================================

function initSubjectTopics() {
    const subjectSelect = document.getElementById('subject-select');
    const topicSelect = document.getElementById('topic-select');
    
    if (subjectSelect && topicSelect) {
        subjectSelect.addEventListener('change', () => {
            const subject = subjectSelect.value;
            const topics = topicsBySubject[subject] || [];
            
            topicSelect.innerHTML = topics.map(t => 
                `<option value="${t}">${t}</option>`
            ).join('');
        });
    }
}

// ========================================
// Chat / AI Tutor
// ========================================

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    const subject = document.getElementById('subject-select')?.value || 'General';
    const topic = document.getElementById('topic-select')?.value || 'General';
    const helpMode = document.querySelector('input[name="help-mode"]:checked')?.value || 'ai';
    const masMode = document.getElementById('mas-mode-toggle')?.checked || false;
    
    // Add user message
    addChatMessage('user', message);
    input.value = '';
    
    // Check if we should use resource-first mode
    if (subject === 'Computer Science' && helpMode === 'resources') {
        const resources = getCSResources(topic, message);
        addChatMessage('assistant', resources);
        return;
    }
    
    // Call API
    showLoading();
    
    try {
        // Choose endpoint based on MAS mode
        const endpoint = masMode ? `${API_BASE}/mas/learn` : `${API_BASE}/tutor/ask`;
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question: message,
                subject: subject,
                session_id: 'web_session'
            })
        });
        
        if (!response.ok) throw new Error('API request failed');
        
        const data = await response.json();
        
        // Display results based on mode
        if (masMode) {
            // Multi-Agent Mode - show comprehensive output
            addChatMessage('assistant', data.answer || data.content || 'Processing...');
            
            // Show quiz if available
            if (data.assessment && data.assessment.questions && data.assessment.questions.length > 0) {
                setTimeout(() => {
                    displayMASQuiz(data.assessment.questions);
                }, 1000);
            }
        } else {
            // Standard mode
            addChatMessage('assistant', data.answer || 'I received your question but encountered an issue.');
        }
        
        // Add visual recommendation for visual CS topics
        if (subject === 'Computer Science' && isVisualTopic(topic, message)) {
            setTimeout(() => {
                addChatMessage('assistant', 
                    '💡 <strong>Tip:</strong> This topic is highly visual! Check out ' +
                    '<a href="https://visualgo.net" target="_blank">Visualgo</a> for interactive visualizations, ' +
                    'or try the Video Generator for an animated explainer.'
                );
            }, 500);
        }
        
    } catch (error) {
        console.error('Error:', error);
        addChatMessage('assistant', 
            'Sorry, I couldn\'t connect to the AI service. Please make sure the backend is running on port 8000.'
        );
    }
    
    hideLoading();
}

function displayMASQuiz(questions) {
    const messagesContainer = document.getElementById('chat-messages');
    const quizDiv = document.createElement('div');
    quizDiv.className = 'message assistant';
    
    let quizHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
            <h4>📝 Practice Quiz</h4>
    `;
    
    questions.forEach((q, idx) => {
        quizHTML += `
            <div class="quiz-question" style="margin: 15px 0; padding: 15px; border-left: 3px solid var(--primary-color); background: var(--surface-color);">
                <p><strong>Q${idx + 1}:</strong> ${q.question}</p>
                <ul style="list-style: none; padding-left: 0;">
        `;
        
        q.options.forEach((opt, optIdx) => {
            quizHTML += `<li style="padding: 5px 0;">• ${opt}</li>`;
        });
        
        quizHTML += `
                </ul>
                <details style="margin-top: 10px;">
                    <summary style="cursor: pointer; color: var(--primary-color);">Show Answer</summary>
                    <p><strong>Answer:</strong> ${q.options[q.correct_answer]}</p>
                    <p><em>${q.explanation}</em></p>
                </details>
            </div>
        `;
    });
    
    quizHTML += `</div>`;
    quizDiv.innerHTML = quizHTML;
    messagesContainer.appendChild(quizDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function addChatMessage(role, content) {
    const messagesContainer = document.getElementById('chat-messages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    // Render markdown for assistant messages
    const renderedContent = role === 'assistant' && typeof marked !== 'undefined' 
        ? marked.parse(content) 
        : content;
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas ${role === 'user' ? 'fa-user' : 'fa-robot'}"></i>
        </div>
        <div class="message-content">
            ${renderedContent}
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    chatHistory.push({ role, content });
}

function clearChat() {
    const messagesContainer = document.getElementById('chat-messages');
    messagesContainer.innerHTML = `
        <div class="message assistant">
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <p>Hello! I'm your AI tutor. Ask me anything about the selected topic.</p>
            </div>
        </div>
    `;
    chatHistory = [];
}

function getCSResources(topic, query) {
    const resources = csResources[topic] || csResources['Data Structures'];
    
    let html = '<strong>📚 Curated Resources (saving API credits):</strong><br><br>';
    html += `For <strong>${topic}</strong>, check out these high-quality resources:<br><ul>`;
    
    resources.forEach(r => {
        html += `<li><a href="${r.url}" target="_blank">${r.name}</a></li>`;
    });
    
    html += '</ul><br>Search these sites for: <code>' + query + '</code><br>';
    html += '<br><em>Switch to "AI Tutor" mode for personalized explanations.</em>';
    
    return html;
}

function isVisualTopic(topic, question) {
    const visualKeywords = [
        'array', 'linked list', 'stack', 'queue', 'tree', 'binary tree',
        'bst', 'graph', 'heap', 'priority queue', 'trie', 'hash table',
        'sorting', 'searching', 'recursion', 'dynamic programming'
    ];
    const text = `${topic} ${question}`.toLowerCase();
    return visualKeywords.some(k => text.includes(k));
}

// ========================================
// Quiz
// ========================================

async function generateQuiz() {
    const topic = document.getElementById('quiz-topic').value;
    const difficulty = document.getElementById('quiz-difficulty').value;
    const numQuestions = parseInt(document.getElementById('quiz-count').value);
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE}/quiz/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                topic: topic,
                difficulty: difficulty,
                num_questions: numQuestions
            })
        });
        
        if (!response.ok) throw new Error('Quiz generation failed');
        
        const data = await response.json();
        currentQuiz = data.questions;
        renderQuiz(data.questions);
        
    } catch (error) {
        console.error('Error:', error);
        showToast('Failed to generate quiz. Is the backend running?', 'error');
    }
    
    hideLoading();
}

function renderQuiz(questions) {
    const container = document.getElementById('quiz-content');
    
    if (!questions || questions.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-exclamation-circle"></i>
                <p>No questions generated. Try a different topic.</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    
    questions.forEach((q, idx) => {
        html += `
            <div class="quiz-question" id="question-${idx}">
                <h4>Question ${idx + 1}: ${q.question}</h4>
                <div class="quiz-options">
        `;
        
        q.options.forEach((opt, optIdx) => {
            html += `
                <div class="quiz-option" data-question="${idx}" data-option="${optIdx}" onclick="selectOption(${idx}, ${optIdx})">
                    ${opt}
                </div>
            `;
        });
        
        html += `
                </div>
                <div class="quiz-explanation" id="explanation-${idx}" style="display: none; margin-top: 1rem; padding: 1rem; background: rgba(16, 185, 129, 0.1); border-radius: 10px;">
                    <strong>Explanation:</strong> ${q.explanation}
                </div>
            </div>
        `;
    });
    
    html += `
        <button class="btn btn-primary btn-block" onclick="submitQuiz()" style="margin-top: 1.5rem;">
            <i class="fas fa-check"></i> Submit Quiz
        </button>
    `;
    
    container.innerHTML = html;
}

let selectedAnswers = {};

function selectOption(questionIdx, optionIdx) {
    // Deselect all options for this question
    document.querySelectorAll(`[data-question="${questionIdx}"]`).forEach(opt => {
        opt.classList.remove('selected');
    });
    
    // Select clicked option
    document.querySelector(`[data-question="${questionIdx}"][data-option="${optionIdx}"]`).classList.add('selected');
    selectedAnswers[questionIdx] = optionIdx;
}

function submitQuiz() {
    if (!currentQuiz) return;
    
    let correct = 0;
    
    currentQuiz.forEach((q, idx) => {
        const selected = selectedAnswers[idx];
        const options = document.querySelectorAll(`[data-question="${idx}"]`);
        
        options.forEach((opt, optIdx) => {
            if (optIdx === q.correct_answer) {
                opt.classList.add('correct');
            } else if (optIdx === selected && selected !== q.correct_answer) {
                opt.classList.add('incorrect');
            }
        });
        
        if (selected === q.correct_answer) {
            correct++;
        }
        
        // Show explanation
        document.getElementById(`explanation-${idx}`).style.display = 'block';
    });
    
    const score = Math.round((correct / currentQuiz.length) * 100);
    showToast(`Score: ${score}% (${correct}/${currentQuiz.length} correct)`, score >= 70 ? 'success' : 'warning');
}

// ========================================
// Video Generator
// ========================================

function initDurationSlider() {
    const slider = document.getElementById('video-duration');
    const value = document.getElementById('duration-value');
    
    if (slider && value) {
        slider.addEventListener('input', () => {
            value.textContent = slider.value + ' min';
        });
    }
}

async function generateVideo() {
    const topic = document.getElementById('video-topic').value;
    const subject = document.getElementById('video-subject').value;
    const duration = document.getElementById('video-duration').value;
    const difficulty = document.getElementById('video-difficulty')?.value || 'beginner';
    const voice = document.getElementById('video-voice')?.value || 'nova';
    const proMode = document.getElementById('pro-mode-toggle')?.checked ?? true;
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE}/video/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                topic: topic,
                subject: subject,
                difficulty_level: difficulty,
                duration_minutes: parseInt(duration),
                professional_mode: proMode,
                voice: voice
            })
        });
        
        if (!response.ok) throw new Error('Video generation failed');
        
        const data = await response.json();
        
        // Display video with player and download
        const preview = document.getElementById('video-preview');
        let scenesHtml = '';
        
        if (data.scenes && data.scenes.length > 0) {
            scenesHtml = data.scenes.map((scene, idx) => `
                <div style="background: rgba(102, 126, 234, 0.1); border-radius: 12px; padding: 1rem; margin-bottom: 0.5rem;">
                    <h4 style="color: var(--accent-color); margin-bottom: 0.3rem; font-size: 1rem;">
                        Scene ${scene.scene_number || idx + 1}: ${scene.title || 'Untitled'}
                    </h4>
                    <p style="color: var(--text-primary); margin-bottom: 0.3rem; font-size: 0.9rem;">
                        ${scene.narration_text || 'No narration'}
                    </p>
                </div>
            `).join('');
        }
        
        preview.innerHTML = `
            <div style="text-align: center;">
                <i class="fas fa-check-circle" style="font-size: 3rem; color: var(--success); margin-bottom: 1rem;"></i>
                <h3 style="color: var(--text-primary); margin-bottom: 1rem;">🎬 Video Generated Successfully!</h3>
                <p style="color: #bd93f9; font-size: 0.9rem; margin-bottom: 1rem;">
                    ${proMode ? '✨ Professional Mode: Manim + OpenAI ' + voice.charAt(0).toUpperCase() + voice.slice(1) + ' Voice' : 'Standard Mode'}
                </p>
                
                ${data.video_path || data.download_url ? `
                    <div style="background: #000; border-radius: 12px; overflow: hidden; margin: 1.5rem 0; width: 100%; max-width: 900px;">
                        <video controls style="width: 100%; height: auto; display: block;" preload="metadata">
                            <source src="${API_BASE}${data.download_url || `/video/${data.id}/download`}" type="video/mp4">
                            Your browser does not support video playback.
                        </video>
                    </div>
                    
                    <div style="margin: 1rem 0; display: flex; gap: 1rem; flex-wrap: wrap; justify-content: center;">
                        <a href="${API_BASE}${data.download_url || `/video/${data.id}/download`}" class="btn btn-primary" download>
                        <i class="fas fa-download"></i> Download Video (MP4)
                    </a>
                        <button class="btn btn-outline" onclick="navigator.clipboard.writeText('${API_BASE}${data.download_url || `/video/${data.id}/download`}').then(() => showToast('Video URL copied!', 'success'))">
                            <i class="fas fa-link"></i> Copy Video URL
                        </button>
                    </div>
                ` : '<p style="color: var(--text-secondary); margin-top: 1rem;">Video is being generated... Please wait a moment and refresh.</p>'}
                
                <div style="text-align: left; margin-top: 1.5rem; max-width: 800px; margin-left: auto; margin-right: auto;">
                    <h4 style="color: var(--text-primary); margin-bottom: 0.75rem; font-size: 1.1rem;">📝 Script Summary:</h4>
                    <p style="color: var(--text-secondary); margin-bottom: 0.75rem;">
                        <strong>Topic:</strong> ${topic} | 
                        <strong>Scenes:</strong> ${data.scenes?.length || 0} | 
                        <strong>Voice:</strong> ${voice.charAt(0).toUpperCase() + voice.slice(1)}
                    </p>
                    ${scenesHtml || '<p>Script generated successfully!</p>'}
                </div>
            </div>
        `;
        
        showToast('Video rendered and ready to download!', 'success');
        
    } catch (error) {
        console.error('Error:', error);
        showToast('Video generation failed. This may take a while - please wait...', 'error');
    }
    
    hideLoading();
}

// Complete 3Blue1Brown Package Generator
async function generate3B1BPackage() {
    const topic = document.getElementById('video-topic').value;
    const voice = document.getElementById('video-voice')?.value || 'nova';
    
    if (!topic.trim()) {
        showToast('Please enter a topic', 'error');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE}/video/3b1b-complete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                topic: topic,
                voice: voice
            })
        });
        
        if (!response.ok) throw new Error('3B1B package generation failed');
        
        const data = await response.json();
        const sections = data.sections;
        
        // Display all 4 sections
        const preview = document.getElementById('video-preview');
        preview.innerHTML = `
            <div style="max-height: 80vh; overflow-y: auto;">
                <div style="text-align: center; margin-bottom: 2rem;">
                    <i class="fas fa-check-circle" style="font-size: 2.5rem; color: var(--success); margin-bottom: 1rem;"></i>
                    <h3 style="color: var(--text-primary); margin-bottom: 0.5rem;">🎬 Complete 3Blue1Brown Package</h3>
                    <p style="color: #bd93f9;">Topic: ${data.topic} | Voice: ${data.voice}</p>
                    
                    <audio controls style="margin: 1rem auto; display: block;" src="${API_BASE}${data.download_url}">
                        Your browser does not support audio.
                    </audio>
                    <a href="${API_BASE}${data.download_url}" class="btn btn-primary btn-sm" download>
                        <i class="fas fa-download"></i> Download Narration
                    </a>
                </div>
                
                <!-- Section 1: Voiceover Script -->
                <div style="background: rgba(189, 147, 249, 0.1); border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; border-left: 4px solid #bd93f9;">
                    <h4 style="color: #bd93f9; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.5rem;">
                        <i class="fas fa-microphone"></i> SECTION 1: VOICEOVER SCRIPT
                    </h4>
                    <pre style="white-space: pre-wrap; word-wrap: break-word; font-size: 0.9rem; color: var(--text-primary); background: var(--input-bg); padding: 1rem; border-radius: 8px; max-height: 200px; overflow-y: auto;">${sections.voiceover_script || 'No script generated'}</pre>
                </div>
                
                <!-- Section 2: Animation Storyboard -->
                <div style="background: rgba(80, 250, 123, 0.1); border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; border-left: 4px solid #50fa7b;">
                    <h4 style="color: #50fa7b; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.5rem;">
                        <i class="fas fa-film"></i> SECTION 2: ANIMATION STORYBOARD
                    </h4>
                    <pre style="white-space: pre-wrap; word-wrap: break-word; font-size: 0.9rem; color: var(--text-primary); background: var(--input-bg); padding: 1rem; border-radius: 8px; max-height: 200px; overflow-y: auto;">${sections.animation_storyboard || 'No storyboard generated'}</pre>
                </div>
                
                <!-- Section 3: Manim Code -->
                <div style="background: rgba(255, 121, 198, 0.1); border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; border-left: 4px solid #ff79c6;">
                    <h4 style="color: #ff79c6; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.5rem;">
                        <i class="fas fa-code"></i> SECTION 3: MANIM CODE
                        <button onclick="copyToClipboard(this.parentElement.nextElementSibling.textContent)" class="btn btn-sm" style="margin-left: auto; padding: 0.25rem 0.5rem; font-size: 0.75rem;">
                            <i class="fas fa-copy"></i> Copy
                        </button>
                    </h4>
                    <pre style="white-space: pre-wrap; word-wrap: break-word; font-size: 0.85rem; font-family: 'Fira Code', monospace; color: var(--text-primary); background: #1e1e2e; padding: 1rem; border-radius: 8px; max-height: 300px; overflow-y: auto;">${escapeHtml(sections.manim_code) || 'No code generated'}</pre>
                </div>
                
                <!-- Section 4: Voice Generation Prompt -->
                <div style="background: rgba(139, 233, 253, 0.1); border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; border-left: 4px solid #8be9fd;">
                    <h4 style="color: #8be9fd; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.5rem;">
                        <i class="fas fa-comment-dots"></i> SECTION 4: VOICE GENERATION PROMPT
                    </h4>
                    <pre style="white-space: pre-wrap; word-wrap: break-word; font-size: 0.9rem; color: var(--text-primary); background: var(--input-bg); padding: 1rem; border-radius: 8px; max-height: 200px; overflow-y: auto;">${sections.voice_prompt || 'No voice prompt generated'}</pre>
                </div>
            </div>
        `;
        
        showToast('Complete 3B1B package generated with all 4 sections!', 'success');
        
    } catch (error) {
        console.error('Error:', error);
        showToast('Failed to generate 3B1B package. Please try again.', 'error');
    }
    
    hideLoading();
}

// Helper functions
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Code copied to clipboard!', 'success');
    }).catch(() => {
        showToast('Failed to copy', 'error');
    });
}

// ========================================
// Settings
// ========================================

async function checkApiStatus() {
    const statusApi = document.getElementById('status-api');
    const statusRag = document.getElementById('status-rag');
    
    try {
        const response = await fetch(`${API_BASE}/health`);
        
        if (response.ok) {
            if (statusApi) {
                statusApi.classList.add('success');
                statusApi.querySelector('.status-badge').textContent = 'Connected';
            }
            if (statusRag) {
                statusRag.classList.add('success');
                statusRag.querySelector('.status-badge').textContent = 'Ready';
            }
        } else {
            throw new Error('API not healthy');
        }
    } catch (error) {
        if (statusApi) {
            statusApi.classList.add('error');
            statusApi.querySelector('.status-badge').textContent = 'Disconnected';
        }
        if (statusRag) {
            statusRag.classList.add('error');
            statusRag.querySelector('.status-badge').textContent = 'Unavailable';
        }
    }
}

async function initializeSampleContent() {
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE}/content/initialize-samples`, {
            method: 'POST'
        });
        
        if (!response.ok) throw new Error('Initialization failed');
        
        const data = await response.json();
        showToast(`Added ${data.chunks} sample content chunks!`, 'success');
        
    } catch (error) {
        console.error('Error:', error);
        showToast('Failed to initialize content. Is the backend running?', 'error');
    }
    
    hideLoading();
}

// ========================================
// Utilities
// ========================================

function showLoading() {
    const overlay = document.getElementById('loading-overlay');
    overlay.classList.add('active');
    
    // Start rotating facts every 5 seconds (slower)
    updateLoadingFact();
    factInterval = setInterval(updateLoadingFact, 5000);
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    overlay.classList.remove('active');
    
    // Stop rotating facts
    if (factInterval) {
        clearInterval(factInterval);
        factInterval = null;
    }
}

function updateLoadingFact() {
    const factElement = document.getElementById('loading-fact');
    if (factElement) {
        factElement.style.opacity = '0';
        setTimeout(() => {
            factElement.textContent = educationalFacts[factIndex];
            factElement.style.opacity = '1';
            factIndex = (factIndex + 1) % educationalFacts.length;
        }, 500); // Slower fade transition
    }
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}
