/**
 * Popup script for Graph RAG Email Assistant
 * Handles settings and status display
 */

console.log('Popup script loaded');

// DOM elements
const apiUrlInput = document.getElementById('apiUrl');
const confidenceThresholdInput = document.getElementById('confidenceThreshold');
const autoInsertCheckbox = document.getElementById('autoInsert');
const saveBtn = document.getElementById('saveBtn');
const testBtn = document.getElementById('testBtn');
const statusDiv = document.getElementById('status');
const statusText = document.getElementById('statusText');
const messageDiv = document.getElementById('message');

/**
 * Load settings from storage
 */
function loadSettings() {
    chrome.storage.sync.get(
        ['apiUrl', 'autoInsert', 'confidenceThreshold'],
        (items) => {
            apiUrlInput.value = items.apiUrl || 'http://localhost:8000/api';
            autoInsertCheckbox.checked = items.autoInsert !== false;
            confidenceThresholdInput.value = items.confidenceThreshold || 0.85;
            
            console.log('Settings loaded:', items);
        }
    );
}

/**
 * Save settings to storage
 */
function saveSettings() {
    const settings = {
        apiUrl: apiUrlInput.value,
        autoInsert: autoInsertCheckbox.checked,
        confidenceThreshold: parseFloat(confidenceThresholdInput.value)
    };
    
    chrome.storage.sync.set(settings, () => {
        console.log('Settings saved:', settings);
        showMessage('Settings saved successfully!', 'success');
    });
}

/**
 * Test connection to backend
 */
async function testConnection() {
    const apiUrl = apiUrlInput.value;
    
    showMessage('Testing connection...', 'success');
    testBtn.disabled = true;
    testBtn.textContent = 'Testing...';
    
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
            updateStatus(true, 'Backend online and healthy');
            showMessage('Connection successful! All services running.', 'success');
        } else if (data.status === 'degraded') {
            updateStatus(true, 'Backend online (degraded)');
            showMessage('Backend online but some services unavailable.', 'success');
        } else {
            updateStatus(false, 'Backend unhealthy');
            showMessage('Backend is running but unhealthy.', 'error');
        }
    } catch (error) {
        console.error('Connection test failed:', error);
        updateStatus(false, 'Backend offline');
        showMessage(`Connection failed: ${error.message}`, 'error');
    } finally {
        testBtn.disabled = false;
        testBtn.textContent = 'Test Connection';
    }
}

/**
 * Update status display
 */
function updateStatus(isOnline, message) {
    if (isOnline) {
        statusDiv.className = 'status online';
        statusText.textContent = message || 'Backend online';
    } else {
        statusDiv.className = 'status offline';
        statusText.textContent = message || 'Backend offline';
    }
}

/**
 * Show message to user
 */
function showMessage(text, type = 'success') {
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
    messageDiv.style.display = 'block';
    
    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 3000);
}

/**
 * Check backend health on popup load
 */
async function checkHealth() {
    const apiUrl = apiUrlInput.value;
    
    try {
        const response = await fetch(`${apiUrl}/health`, {
            method: 'GET'
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.status === 'healthy') {
                updateStatus(true, 'Backend online');
            } else {
                updateStatus(true, 'Backend online (degraded)');
            }
        } else {
            updateStatus(false, 'Backend offline');
        }
    } catch (error) {
        console.error('Health check failed:', error);
        updateStatus(false, 'Backend offline');
    }
}

// Event listeners
saveBtn.addEventListener('click', saveSettings);
testBtn.addEventListener('click', testConnection);

// Initialize
loadSettings();
setTimeout(checkHealth, 500); // Check health after settings load

console.log('Popup initialized');

