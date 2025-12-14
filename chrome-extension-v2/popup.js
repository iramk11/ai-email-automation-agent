/**
 * Modern popup script with improved UX
 */

console.log('AI Email Assistant: Popup loaded');

// DOM elements
const elements = {
    apiUrl: document.getElementById('apiUrl'),
    confidenceThreshold: document.getElementById('confidenceThreshold'),
    confidenceValue: document.getElementById('confidenceValue'),
    autoInsert: document.getElementById('autoInsert'),
    saveBtn: document.getElementById('saveBtn'),
    testBtn: document.getElementById('testBtn'),
    statusCard: document.getElementById('statusCard'),
    statusIcon: document.getElementById('statusIcon'),
    statusLabel: document.getElementById('statusLabel'),
    statusSubtitle: document.getElementById('statusSubtitle'),
    statusDot: document.getElementById('statusDot'),
    toast: document.getElementById('toast')
};

const DEFAULT_API_URL = 'http://localhost:8001/api';

/**
 * Show toast notification
 */
function showToast(message, type = 'info', duration = 3000) {
    elements.toast.textContent = message;
    elements.toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        elements.toast.classList.remove('show');
    }, duration);
}

/**
 * Update status display
 */
function updateStatus(isOnline, message, subtitle) {
    if (isOnline) {
        elements.statusCard.style.background = 'linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%)';
        elements.statusCard.style.borderColor = '#86efac';
        elements.statusIcon.textContent = '✓';
        elements.statusDot.classList.add('online');
        elements.statusDot.classList.remove('offline');
    } else {
        elements.statusCard.style.background = 'linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%)';
        elements.statusCard.style.borderColor = '#fca5a5';
        elements.statusIcon.textContent = '✕';
        elements.statusDot.classList.add('offline');
        elements.statusDot.classList.remove('online');
    }
    
    elements.statusLabel.textContent = message || (isOnline ? 'Backend online' : 'Backend offline');
    elements.statusSubtitle.textContent = subtitle || 'Connection status';
}

/**
 * Load settings from storage
 */
function loadSettings() {
    chrome.storage.sync.get(
        ['apiUrl', 'autoInsert', 'confidenceThreshold'],
        (items) => {
            elements.apiUrl.value = items.apiUrl || DEFAULT_API_URL;
            elements.autoInsert.checked = items.autoInsert !== false;
            const threshold = items.confidenceThreshold || 0.85;
            elements.confidenceThreshold.value = threshold;
            elements.confidenceValue.textContent = `${Math.round(threshold * 100)}%`;
            
            console.log('Settings loaded:', items);
        }
    );
}

/**
 * Save settings to storage
 */
function saveSettings() {
    const settings = {
        apiUrl: elements.apiUrl.value.trim(),
        autoInsert: elements.autoInsert.checked,
        confidenceThreshold: parseFloat(elements.confidenceThreshold.value)
    };
    
    // Validate API URL
    if (!settings.apiUrl) {
        showToast('Please enter an API URL', 'error');
        return;
    }
    
    chrome.storage.sync.set(settings, () => {
        console.log('Settings saved:', settings);
        showToast('Settings saved successfully', 'success');
    });
}

/**
 * Test connection to backend
 */
async function testConnection() {
    const apiUrl = elements.apiUrl.value.trim() || DEFAULT_API_URL;
    
    if (!apiUrl) {
        showToast('Please enter an API URL first', 'warning');
        return;
    }
    
    elements.testBtn.disabled = true;
    elements.testBtn.innerHTML = `
        <svg class="btn-icon" viewBox="0 0 24 24" fill="none" style="animation: spin 1s linear infinite;">
            <path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z" fill="currentColor"/>
        </svg>
        Testing...
    `;
    
    updateStatus(false, 'Testing connection...', 'Please wait');
    
    try {
        const response = await fetch(`${apiUrl}/health`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Health check response:', data);
        
        if (data.status === 'healthy') {
            updateStatus(true, 'Backend online and healthy', 'All services running');
            showToast('Connection successful!', 'success');
        } else if (data.status === 'degraded') {
            updateStatus(true, 'Backend online (degraded)', 'Some services unavailable');
            showToast('Backend online but degraded', 'warning');
        } else {
            updateStatus(false, 'Backend unhealthy', 'Services not responding');
            showToast('Backend is unhealthy', 'error');
        }
    } catch (error) {
        console.error('Connection test failed:', error);
        updateStatus(false, 'Backend offline', 'Cannot reach server');
        showToast(`Connection failed: ${error.message}`, 'error');
    } finally {
        elements.testBtn.disabled = false;
        elements.testBtn.innerHTML = `
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none">
                <path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z" fill="currentColor"/>
            </svg>
            Test Connection
        `;
    }
}

/**
 * Check backend health on popup load
 */
async function checkHealth() {
    const apiUrl = elements.apiUrl.value.trim() || DEFAULT_API_URL;
    
    if (!apiUrl) {
        updateStatus(false, 'API URL not configured', 'Please set your API URL');
        return;
    }
    
    try {
        const response = await fetch(`${apiUrl}/health`, {
            method: 'GET'
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.status === 'healthy') {
                updateStatus(true, 'Backend online', 'All systems operational');
            } else {
                updateStatus(true, 'Backend online (degraded)', 'Some services unavailable');
            }
        } else {
            updateStatus(false, 'Backend offline', 'Cannot reach server');
        }
    } catch (error) {
        console.error('Health check failed:', error);
        updateStatus(false, 'Backend offline', 'Connection failed');
    }
}

// Event listeners
elements.saveBtn.addEventListener('click', saveSettings);
elements.testBtn.addEventListener('click', testConnection);

// Confidence slider update
elements.confidenceThreshold.addEventListener('input', (e) => {
    const value = Math.round(parseFloat(e.target.value) * 100);
    elements.confidenceValue.textContent = `${value}%`;
});

// Initialize
loadSettings();
setTimeout(() => {
    checkHealth();
}, 500);

console.log('Popup initialized');

