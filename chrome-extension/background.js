/**
 * Background service worker for Graph RAG Email Assistant
 * Handles extension lifecycle and message passing
 */

console.log('Graph RAG Email Assistant: Background service worker loaded');

// Configuration
const DEFAULT_API_URL = 'http://localhost:8000/api';

/**
 * Handle extension installation
 */
chrome.runtime.onInstalled.addListener((details) => {
    console.log('Extension installed:', details.reason);
    
    // Set default settings
    chrome.storage.sync.set({
        apiUrl: DEFAULT_API_URL,
        autoInsert: true,
        confidenceThreshold: 0.85
    }, () => {
        console.log('Default settings saved');
    });
    
    if (details.reason === 'install') {
        // Show welcome message
        console.log('Welcome to Graph RAG Email Assistant!');
    } else if (details.reason === 'update') {
        console.log('Extension updated to version', chrome.runtime.getManifest().version);
    }
});

/**
 * Handle messages from content script or popup
 */
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('Received message:', request.type);
    
    if (request.type === 'GET_SETTINGS') {
        // Get settings from storage
        chrome.storage.sync.get(['apiUrl', 'autoInsert', 'confidenceThreshold'], (items) => {
            sendResponse({
                apiUrl: items.apiUrl || DEFAULT_API_URL,
                autoInsert: items.autoInsert !== false,
                confidenceThreshold: items.confidenceThreshold || 0.85
            });
        });
        return true; // Keep channel open for async response
    }
    
    if (request.type === 'SAVE_SETTINGS') {
        // Save settings to storage
        chrome.storage.sync.set(request.settings, () => {
            console.log('Settings saved:', request.settings);
            sendResponse({ success: true });
        });
        return true;
    }
    
    if (request.type === 'GENERATE_REPLY') {
        // Forward to API (this is handled by content script, but kept for extensibility)
        handleGenerateReply(request.emailData)
            .then(response => sendResponse({ success: true, data: response }))
            .catch(error => sendResponse({ success: false, error: error.message }));
        return true;
    }
});

/**
 * Handle reply generation (if needed from background)
 */
async function handleGenerateReply(emailData) {
    const settings = await new Promise((resolve) => {
        chrome.storage.sync.get(['apiUrl'], (items) => {
            resolve(items);
        });
    });
    
    const apiUrl = settings.apiUrl || DEFAULT_API_URL;
    
    try {
        const response = await fetch(`${apiUrl}/generate-reply`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(emailData)
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Failed to generate reply:', error);
        throw error;
    }
}

/**
 * Handle extension icon click
 */
chrome.action.onClicked.addListener((tab) => {
    console.log('Extension icon clicked on tab:', tab.id);
    
    // Check if we're on Gmail
    if (tab.url && tab.url.includes('mail.google.com')) {
        console.log('On Gmail, popup will open automatically');
    } else {
        console.log('Not on Gmail');
    }
});

/**
 * Monitor tab changes
 */
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url && tab.url.includes('mail.google.com')) {
        console.log('Gmail tab loaded:', tabId);
    }
});

console.log('Background service worker initialized');

