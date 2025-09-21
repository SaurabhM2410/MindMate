/**
 * MindMate - Mental Wellbeing Companion App
 * Interactive JavaScript functionality
 */

// Global state management
const AppState = {
    currentTab: 'dashboard',
    conversationId: null,
    breathingSession: {
        isActive: false,
        isPaused: false,
        cycles: 0,
        startTime: null,
        timer: null
    },
    selectedMood: null
};

// Utility functions
const Utils = {
    // Show loading overlay
    showLoading() {
        document.getElementById('loadingOverlay').style.display = 'flex';
    },

    // Hide loading overlay
    hideLoading() {
        document.getElementById('loadingOverlay').style.display = 'none';
    },

    // Show toast notification
    showToast(message, type = 'success') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px;">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
                <span>${message}</span>
            </div>
        `;
        
        container.appendChild(toast);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 3000);
    },

    // Format timestamp
    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleString();
    },

    // Format time duration
    formatDuration(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    },

    // API request helper
    async apiRequest(endpoint, options = {}) {
        try {
            const response = await fetch(`/api${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            Utils.showToast('An error occurred. Please try again.', 'error');
            throw error;
        }
    }
};

// Navigation system
const Navigation = {
    init() {
        // Tab navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const tabName = link.dataset.tab;
                if (tabName) {
                    this.switchTab(tabName);
                }
            });
        });

        // Quick action buttons
        document.querySelectorAll('.quick-action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const tabName = btn.dataset.tab;
                if (tabName) {
                    this.switchTab(tabName);
                }
            });
        });

        // Mobile hamburger menu
        const hamburger = document.querySelector('.hamburger');
        const navMenu = document.querySelector('.nav-menu');
        
        if (hamburger && navMenu) {
            hamburger.addEventListener('click', () => {
                navMenu.classList.toggle('active');
            });
        }
    },

    switchTab(tabName) {
        // Update nav links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });
        document.getElementById(tabName).classList.add('active');

        AppState.currentTab = tabName;

        // Load tab-specific data
        this.loadTabData(tabName);
    },

    async loadTabData(tabName) {
        switch (tabName) {
            case 'dashboard':
                await Dashboard.loadStats();
                break;
            case 'mood':
                await MoodTracker.loadHistory();
                break;
            case 'journal':
                await Journal.loadEntries();
                break;
        }
    }
};

// Dashboard functionality
const Dashboard = {
    async loadStats() {
        try {
            Utils.showLoading();
            const stats = await Utils.apiRequest('/dashboard/stats');
            
            // Update stats display
            document.getElementById('avgMood').textContent = stats.avg_intensity || '-';
            document.getElementById('journalCount').textContent = stats.total_entries || '0';
            document.getElementById('breathingCount').textContent = stats.total_breathing_sessions || '0';
            
            // Update mood chart
            this.updateMoodChart(stats.mood_counts || []);
        } catch (error) {
            console.error('Failed to load dashboard stats:', error);
        } finally {
            Utils.hideLoading();
        }
    },

    updateMoodChart(moodData) {
        const ctx = document.getElementById('moodChart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (window.moodChartInstance) {
            window.moodChartInstance.destroy();
        }

        const labels = moodData.map(item => item.mood);
        const data = moodData.map(item => item.count);
        const colors = [
            '#667eea', '#f093fb', '#4ecdc4', '#51cf66', '#ffd43b', '#ff6b6b'
        ];

        window.moodChartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors.slice(0, data.length),
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
};

// Chat functionality
const Chat = {
    init() {
        const sendBtn = document.getElementById('sendMessage');
        const messageInput = document.getElementById('messageInput');
        const suggestionBtns = document.querySelectorAll('.suggestion-btn');

        sendBtn.addEventListener('click', () => this.sendMessage());
        
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-resize textarea
        messageInput.addEventListener('input', () => {
            messageInput.style.height = 'auto';
            messageInput.style.height = messageInput.scrollHeight + 'px';
        });

        // Suggestion buttons
        suggestionBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                messageInput.value = btn.textContent;
                this.sendMessage();
            });
        });
    },

    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        
        if (!message) return;

        // Clear input and add user message to chat
        messageInput.value = '';
        messageInput.style.height = 'auto';
        this.addMessage(message, 'user');

        try {
            // Send to API
            const response = await Utils.apiRequest('/chat', {
                method: 'POST',
                body: JSON.stringify({
                    message: message,
                    conversation_id: AppState.conversationId
                })
            });

            // Update conversation ID
            AppState.conversationId = response.conversation_id;

            // Add AI response
            this.addMessage(response.reply, 'ai');

            // Handle crisis response
            if (response.is_crisis) {
                Utils.showToast('Emergency resources have been shared. Please reach out for help.', 'error');
            }

        } catch (error) {
            this.addMessage('I apologize, but I\'m having trouble responding right now. Please try again in a moment.', 'ai');
        }
    },

    addMessage(content, sender) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const avatar = sender === 'ai' ? '<i class="fas fa-heart"></i>' : '<i class="fas fa-user"></i>';
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                ${avatar}
            </div>
            <div class="message-content">
                <p>${content}</p>
            </div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
};

// Mood tracking functionality
const MoodTracker = {
    init() {
        const moodBtns = document.querySelectorAll('.mood-btn');
        const saveMoodBtn = document.getElementById('saveMood');
        const cancelMoodBtn = document.getElementById('cancelMood');
        const intensitySlider = document.getElementById('moodIntensity');
        const intensityValue = document.getElementById('intensityValue');

        moodBtns.forEach(btn => {
            btn.addEventListener('click', () => this.selectMood(btn));
        });

        saveMoodBtn.addEventListener('click', () => this.saveMood());
        cancelMoodBtn.addEventListener('click', () => this.cancelMoodSelection());

        intensitySlider.addEventListener('input', (e) => {
            intensityValue.textContent = e.target.value;
        });
    },

    selectMood(button) {
        // Remove previous selection
        document.querySelectorAll('.mood-btn').forEach(btn => {
            btn.classList.remove('selected');
        });

        // Select current mood
        button.classList.add('selected');
        AppState.selectedMood = {
            type: button.dataset.mood,
            emoji: button.dataset.emoji
        };

        // Show mood details
        document.getElementById('moodDetails').style.display = 'block';
    },

    cancelMoodSelection() {
        document.querySelectorAll('.mood-btn').forEach(btn => {
            btn.classList.remove('selected');
        });
        document.getElementById('moodDetails').style.display = 'none';
        AppState.selectedMood = null;
    },

    async saveMood() {
        if (!AppState.selectedMood) return;

        const intensity = document.getElementById('moodIntensity').value;
        const notes = document.getElementById('moodNotes').value;

        try {
            Utils.showLoading();
            
            await Utils.apiRequest('/mood', {
                method: 'POST',
                body: JSON.stringify({
                    mood_type: AppState.selectedMood.type,
                    mood_emoji: AppState.selectedMood.emoji,
                    intensity: parseInt(intensity),
                    notes: notes
                })
            });

            Utils.showToast('Mood logged successfully!');
            this.cancelMoodSelection();
            
            // Clear form
            document.getElementById('moodIntensity').value = 5;
            document.getElementById('intensityValue').textContent = '5';
            document.getElementById('moodNotes').value = '';
            
            // Reload mood history
            await this.loadHistory();

        } catch (error) {
            Utils.showToast('Failed to save mood. Please try again.', 'error');
        } finally {
            Utils.hideLoading();
        }
    },

    async loadHistory() {
        try {
            const response = await Utils.apiRequest('/mood/history?days=7');
            this.displayMoodHistory(response.moods);
        } catch (error) {
            console.error('Failed to load mood history:', error);
        }
    },

    displayMoodHistory(moods) {
        const container = document.getElementById('recentMoods');
        if (!container) return;

        if (moods.length === 0) {
            container.innerHTML = '<p class="text-secondary">No mood entries yet. Log your first mood above!</p>';
            return;
        }

        container.innerHTML = moods.map(mood => `
            <div class="mood-history-item">
                <div class="mood-emoji">${mood.emoji}</div>
                <div class="mood-info">
                    <div class="mood-type">${mood.type}</div>
                    <div class="mood-time">${Utils.formatTimestamp(mood.timestamp)}</div>
                    <div class="mood-intensity">Intensity: ${mood.intensity}/10</div>
                    ${mood.notes ? `<div class="mood-notes-preview">${mood.notes}</div>` : ''}
                </div>
            </div>
        `).join('');
    }
};

// Breathing exercise functionality
const BreathingExercise = {
    init() {
        const startBtn = document.getElementById('startBreathing');
        const pauseBtn = document.getElementById('pauseBreathing');
        const stopBtn = document.getElementById('stopBreathing');

        startBtn.addEventListener('click', () => this.startSession());
        pauseBtn.addEventListener('click', () => this.pauseSession());
        stopBtn.addEventListener('click', () => this.stopSession());
    },

    startSession() {
        if (AppState.breathingSession.isPaused) {
            this.resumeSession();
            return;
        }

        AppState.breathingSession = {
            isActive: true,
            isPaused: false,
            cycles: 0,
            startTime: Date.now(),
            timer: null
        };

        this.updateButtonStates();
        this.startBreathingCycle();
        this.startTimer();
    },

    pauseSession() {
        AppState.breathingSession.isPaused = true;
        if (AppState.breathingSession.timer) {
            clearTimeout(AppState.breathingSession.timer);
        }
        this.updateButtonStates();
        
        const circle = document.getElementById('breathingCircle');
        const text = document.getElementById('breathingText');
        circle.className = 'breathing-circle';
        text.textContent = 'Paused - Click Resume';
    },

    resumeSession() {
        AppState.breathingSession.isPaused = false;
        this.updateButtonStates();
        this.startBreathingCycle();
    },

    stopSession() {
        const session = AppState.breathingSession;
        const duration = Math.floor((Date.now() - session.startTime) / 1000);
        
        // Log the session
        if (session.cycles > 0) {
            this.logSession(duration, session.cycles);
        }

        // Reset state
        AppState.breathingSession = {
            isActive: false,
            isPaused: false,
            cycles: 0,
            startTime: null,
            timer: null
        };

        if (session.timer) {
            clearTimeout(session.timer);
        }

        this.updateButtonStates();
        this.resetDisplay();
    },

    startBreathingCycle() {
        if (!AppState.breathingSession.isActive || AppState.breathingSession.isPaused) {
            return;
        }

        const circle = document.getElementById('breathingCircle');
        const text = document.getElementById('breathingText');

        // Inhale phase (4 seconds)
        circle.className = 'breathing-circle inhale';
        text.textContent = 'Inhale... 4';
        this.countdown(text, 4, 'Inhale', () => {
            if (!AppState.breathingSession.isActive || AppState.breathingSession.isPaused) return;
            
            // Hold phase (7 seconds)
            circle.className = 'breathing-circle hold';
            text.textContent = 'Hold... 7';
            this.countdown(text, 7, 'Hold', () => {
                if (!AppState.breathingSession.isActive || AppState.breathingSession.isPaused) return;
                
                // Exhale phase (8 seconds)
                circle.className = 'breathing-circle exhale';
                text.textContent = 'Exhale... 8';
                this.countdown(text, 8, 'Exhale', () => {
                    if (!AppState.breathingSession.isActive || AppState.breathingSession.isPaused) return;
                    
                    // Complete cycle
                    AppState.breathingSession.cycles++;
                    document.getElementById('completedCycles').textContent = AppState.breathingSession.cycles;
                    
                    // Start next cycle
                    AppState.breathingSession.timer = setTimeout(() => {
                        this.startBreathingCycle();
                    }, 1000);
                });
            });
        });
    },

    countdown(textElement, seconds, phase, callback) {
        let remaining = seconds;
        
        const countdownInterval = setInterval(() => {
            if (!AppState.breathingSession.isActive || AppState.breathingSession.isPaused) {
                clearInterval(countdownInterval);
                return;
            }
            
            remaining--;
            textElement.textContent = `${phase}... ${remaining}`;
            
            if (remaining <= 0) {
                clearInterval(countdownInterval);
                callback();
            }
        }, 1000);
    },

    startTimer() {
        const updateTimer = () => {
            if (!AppState.breathingSession.isActive) return;
            
            const elapsed = Math.floor((Date.now() - AppState.breathingSession.startTime) / 1000);
            document.getElementById('sessionTime').textContent = Utils.formatDuration(elapsed);
            
            if (!AppState.breathingSession.isPaused) {
                setTimeout(updateTimer, 1000);
            }
        };
        
        updateTimer();
    },

    updateButtonStates() {
        const startBtn = document.getElementById('startBreathing');
        const pauseBtn = document.getElementById('pauseBreathing');
        const stopBtn = document.getElementById('stopBreathing');
        
        if (AppState.breathingSession.isActive) {
            startBtn.style.display = 'none';
            pauseBtn.style.display = AppState.breathingSession.isPaused ? 'none' : 'inline-flex';
            stopBtn.style.display = 'inline-flex';
            
            if (AppState.breathingSession.isPaused) {
                startBtn.innerHTML = '<i class="fas fa-play"></i> Resume';
                startBtn.style.display = 'inline-flex';
            }
        } else {
            startBtn.innerHTML = '<i class="fas fa-play"></i> Start Breathing';
            startBtn.style.display = 'inline-flex';
            pauseBtn.style.display = 'none';
            stopBtn.style.display = 'none';
        }
    },

    resetDisplay() {
        const circle = document.getElementById('breathingCircle');
        const text = document.getElementById('breathingText');
        
        circle.className = 'breathing-circle';
        text.textContent = 'Click Start to Begin';
        
        document.getElementById('completedCycles').textContent = '0';
        document.getElementById('sessionTime').textContent = '0:00';
    },

    async logSession(duration, cycles) {
        try {
            await Utils.apiRequest('/breathing', {
                method: 'POST',
                body: JSON.stringify({
                    duration: duration,
                    cycles_completed: cycles,
                    session_type: '4-7-8'
                })
            });

            Utils.showToast(`Breathing session completed! ${cycles} cycles in ${Utils.formatDuration(duration)}`);
        } catch (error) {
            console.error('Failed to log breathing session:', error);
        }
    }
};

// Journal functionality  
const Journal = {
    init() {
        const saveBtn = document.getElementById('saveJournal');
        const clearBtn = document.getElementById('clearJournal');
        const contentTextarea = document.getElementById('journalContent');

        saveBtn.addEventListener('click', () => this.saveEntry());
        clearBtn.addEventListener('click', () => this.clearForm());

        // Auto-save draft (optional enhancement)
        let saveTimeout;
        contentTextarea.addEventListener('input', () => {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                this.saveDraft();
            }, 2000);
        });
    },

    async saveEntry() {
        const title = document.getElementById('journalTitle').value.trim();
        const content = document.getElementById('journalContent').value.trim();
        const mood = document.getElementById('journalMood').value;
        const tags = document.getElementById('journalTags').value.trim();

        if (!content) {
            Utils.showToast('Please write something in your journal entry.', 'error');
            return;
        }

        try {
            Utils.showLoading();
            
            await Utils.apiRequest('/journal', {
                method: 'POST',
                body: JSON.stringify({
                    title: title,
                    content: content,
                    mood_at_time: mood,
                    tags: tags
                })
            });

            Utils.showToast('Journal entry saved successfully!');
            this.clearForm();
            await this.loadEntries();

        } catch (error) {
            Utils.showToast('Failed to save journal entry. Please try again.', 'error');
        } finally {
            Utils.hideLoading();
        }
    },

    clearForm() {
        document.getElementById('journalTitle').value = '';
        document.getElementById('journalContent').value = '';
        document.getElementById('journalMood').value = '';
        document.getElementById('journalTags').value = '';
    },

    async loadEntries() {
        try {
            const response = await Utils.apiRequest('/journal/entries?limit=10');
            this.displayEntries(response.entries);
        } catch (error) {
            console.error('Failed to load journal entries:', error);
        }
    },

    displayEntries(entries) {
        const container = document.getElementById('journalList');
        if (!container) return;

        if (entries.length === 0) {
            container.innerHTML = '<p class="text-secondary">No journal entries yet. Start writing above!</p>';
            return;
        }

        container.innerHTML = entries.map(entry => `
            <div class="journal-entry-card">
                <div class="entry-header">
                    <h4>${entry.title || 'Untitled Entry'}</h4>
                    <span class="entry-date">${Utils.formatTimestamp(entry.timestamp)}</span>
                </div>
                <div class="entry-content">
                    <p>${entry.content.substring(0, 150)}${entry.content.length > 150 ? '...' : ''}</p>
                </div>
                <div class="entry-meta">
                    ${entry.mood ? `<span class="entry-mood">Mood: ${entry.mood}</span>` : ''}
                    ${entry.tags ? `<span class="entry-tags">Tags: ${entry.tags}</span>` : ''}
                </div>
            </div>
        `).join('');
    },

    saveDraft() {
        const content = document.getElementById('journalContent').value;
        if (content.trim()) {
            localStorage.setItem('journalDraft', content);
        }
    },

    loadDraft() {
        const draft = localStorage.getItem('journalDraft');
        if (draft) {
            document.getElementById('journalContent').value = draft;
        }
    }
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 MindMate app initializing...');
    
    // Initialize all modules
    Navigation.init();
    Chat.init();
    MoodTracker.init();
    BreathingExercise.init();
    Journal.init();
    
    // Load initial dashboard data
    Dashboard.loadStats();
    
    // Load journal draft if exists
    Journal.loadDraft();
    
    console.log('✅ MindMate app ready!');
    
    // Hide loading overlay if visible
    Utils.hideLoading();
});