/**
 * Background service worker for AI Email Assistant
 * Handles extension lifecycle and message passing
 */

console.log('AI Email Assistant: Background service worker loaded');

const DEFAULT_API_URL = 'http://localhost:8001/api';

/**
 * Handle extension installation
 */
chrome.runtime.onInstalled.addListener((details) => {
    console.log('Extension installed:', details.reason);
    
    chrome.storage.sync.set({
        apiUrl: DEFAULT_API_URL,
        autoInsert: true,
        confidenceThreshold: 0.85
    }, () => {
        console.log('Default settings saved');
    });
    
    if (details.reason === 'install') {
        console.log('Welcome to AI Email Assistant!');
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
        chrome.storage.sync.get(['apiUrl', 'autoInsert', 'confidenceThreshold'], (items) => {
            sendResponse({
                apiUrl: items.apiUrl || DEFAULT_API_URL,
                autoInsert: items.autoInsert !== false,
                confidenceThreshold: items.confidenceThreshold || 0.85
            });
        });
        return true;
    }
    
    if (request.type === 'SAVE_SETTINGS') {
        chrome.storage.sync.set(request.settings, () => {
            console.log('Settings saved:', request.settings);
            sendResponse({ success: true });
        });
        return true;
    }
    
    if (request.type === 'GENERATE_REPLY') {
        handleGenerateReply(request.emailData)
            .then(response => sendResponse({ success: true, data: response }))
            .catch(error => sendResponse({ success: false, error: error.message }));
        return true;
    }
});

/**
 * Handle reply generation
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
    
    const url = tab.url || '';
    if (url.includes('mail.google.com')) {
        console.log('On Gmail');
    } else if (url.includes('outlook.live.com') || url.includes('outlook.office.com')) {
        console.log('On Outlook');
    } else {
        console.log('Not on supported email client');
    }
});

/**
 * Monitor tab changes
 */
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url) {
        const url = tab.url;
        if (url.includes('mail.google.com')) {
            console.log('Gmail tab loaded:', tabId);
        } else if (url.includes('outlook.live.com') || url.includes('outlook.office.com')) {
            console.log('Outlook tab loaded:', tabId);
        }
    }
});

console.log('Background service worker initialized');

