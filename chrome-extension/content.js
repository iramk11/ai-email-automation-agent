/**
 * Content script for Gmail integration
 * Extracts email content and inserts AI-generated replies
 */

console.log('Graph RAG Email Assistant: Content script loaded');

// Configuration
const API_BASE_URL = 'http://localhost:8000/api';
const BUTTON_CHECK_INTERVAL = 2000; // Check for reply buttons every 2 seconds

/**
 * Extract email content from the current Gmail view
 */
function extractEmailContent() {
    console.log('Attempting to extract email content...');
    
    // Try multiple selectors for email subject
    const subjectElement = document.querySelector('h2.hP') || 
                          document.querySelector('[data-subject]') ||
                          document.querySelector('.ha h2');
    
    // Try multiple selectors for sender email
    const senderElement = document.querySelector('span.gD') ||
                         document.querySelector('[email]') ||
                         document.querySelector('.go');
    
    // Try multiple selectors for email body
    const bodyElement = document.querySelector('div.a3s.aiL') ||
                       document.querySelector('.ii.gt') ||
                       document.querySelector('[data-message-id] .a3s');
    
    const subject = subjectElement?.innerText?.trim() || 'No Subject';
    const sender = senderElement?.getAttribute('email') || 
                  senderElement?.innerText?.trim() || 
                  'unknown@example.com';
    const body = bodyElement?.innerText?.trim() || '';
    
    console.log('Extracted email data:', { subject, sender, bodyLength: body.length });
    
    if (!body) {
        console.warn('Could not extract email body');
        return null;
    }
    
    return { subject, sender, body };
}

/**
 * Find the reply compose box in Gmail
 */
function findReplyBox() {
    // Try multiple selectors for the compose/reply box
    const selectors = [
        'div[aria-label="Message Body"]',
        'div[contenteditable="true"][aria-label*="Message"]',
        'div.editable[contenteditable="true"]',
        'div[g_editable="true"]',
        'div.Am.Al.editable'
    ];
    
    for (const selector of selectors) {
        const element = document.querySelector(selector);
        if (element) {
            console.log('Found reply box with selector:', selector);
            return element;
        }
    }
    
    console.warn('Could not find reply box');
    return null;
}

/**
 * Insert generated draft into the reply box
 */
function insertDraft(draftText, replyBox) {
    if (!replyBox) {
        console.error('No reply box provided');
        return false;
    }
    
    console.log('Inserting draft into reply box...');
    
    try {
        // Set the text content
        replyBox.innerText = draftText;
        
        // Trigger input events to ensure Gmail recognizes the change
        replyBox.dispatchEvent(new Event('input', { bubbles: true }));
        replyBox.dispatchEvent(new Event('change', { bubbles: true }));
        
        // Focus the reply box
        replyBox.focus();
        
        console.log('Draft inserted successfully');
        return true;
    } catch (error) {
        console.error('Failed to insert draft:', error);
        return false;
    }
}

/**
 * Call the backend API to generate a reply
 */
async function generateReply(emailData) {
    console.log('Calling API to generate reply...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/generate-reply`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(emailData)
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status} ${response.statusText}`);
        }
        
        const result = await response.json();
        console.log('API response:', result);
        
        // Log detailed context for debugging
        console.log('🎯 RETRIEVAL DETAILS:');
        console.log('  Intent:', result.intent);
        console.log('  Confidence:', result.confidence_score);
        console.log('  Auto-send:', result.auto_send);
        
        if (result.context_used) {
            console.log('\n📚 FAQ Hits:', result.context_used.faq_hits?.length || 0);
            result.context_used.faq_hits?.forEach((faq, i) => {
                console.log(`    [${i+1}] Score: ${faq.score.toFixed(3)} - ${faq.question}`);
            });
            
            console.log('\n🕸️  Graph Nodes:', result.context_used.graph_nodes?.length || 0);
            result.context_used.graph_nodes?.forEach((node, i) => {
                console.log(`    [${i+1}] Score: ${node.score.toFixed(3)} - ${node.node_name} (${node.node_type})`);
            });
            
            console.log('\n🔗 Expanded Graph:');
            Object.entries(result.context_used.expanded_graph || {}).forEach(([node, neighbors]) => {
                console.log(`    ${node} → [${neighbors.join(', ')}]`);
            });
        }
        
        return result;
    } catch (error) {
        console.error('Failed to generate reply:', error);
        throw error;
    }
}

/**
 * Create and show a loading indicator
 */
function showLoadingIndicator(button) {
    button.disabled = true;
    button.textContent = '⏳ Generating...';
    button.style.opacity = '0.7';
}

/**
 * Hide loading indicator and restore button
 */
function hideLoadingIndicator(button) {
    button.disabled = false;
    button.textContent = '🤖 Generate Reply';
    button.style.opacity = '1';
}

/**
 * Show a notification to the user
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'error' ? '#f44336' : type === 'success' ? '#4CAF50' : '#2196F3'};
        color: white;
        border-radius: 4px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        z-index: 10000;
        font-family: Arial, sans-serif;
        font-size: 14px;
        max-width: 350px;
        white-space: pre-line;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 8000);
}

/**
 * Show detailed context panel
 */
function showContextPanel(response) {
    // Remove existing panel if any
    const existing = document.getElementById('rag-context-panel');
    if (existing) existing.remove();
    
    const panel = document.createElement('div');
    panel.id = 'rag-context-panel';
    panel.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 400px;
        max-height: 500px;
        overflow-y: auto;
        background: white;
        border: 2px solid #667eea;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10001;
        font-family: Arial, sans-serif;
        font-size: 13px;
    `;
    
    const contextInfo = response.context_used;
    
    let html = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <h3 style="margin: 0; color: #667eea;">🔍 Retrieval Context</h3>
            <button onclick="this.parentElement.parentElement.remove()" style="
                border: none;
                background: #f5f5f5;
                padding: 5px 10px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
            ">✕</button>
        </div>
        
        <div style="background: #f0f0f0; padding: 8px; border-radius: 4px; margin-bottom: 10px;">
            <strong>Intent:</strong> ${response.intent}<br>
            <strong>Confidence:</strong> ${(response.confidence_score * 100).toFixed(1)}%<br>
            <strong>Auto-send:</strong> ${response.auto_send ? '✅ Yes' : '❌ No'}
        </div>
    `;
    
    // FAQ Hits
    if (contextInfo?.faq_hits?.length > 0) {
        html += '<div style="margin-bottom: 10px;"><strong>📚 FAQ Matches:</strong></div>';
        contextInfo.faq_hits.forEach((faq, i) => {
            html += `
                <div style="background: #e8f5e9; padding: 8px; border-radius: 4px; margin-bottom: 5px; font-size: 12px;">
                    <div style="color: #2e7d32; font-weight: bold;">
                        [${(faq.score * 100).toFixed(1)}%] ${faq.question}
                    </div>
                    <div style="color: #666; margin-top: 4px;">
                        ${faq.answer.substring(0, 100)}${faq.answer.length > 100 ? '...' : ''}
                    </div>
                </div>
            `;
        });
    }
    
    // Graph Nodes
    if (contextInfo?.graph_nodes?.length > 0) {
        html += '<div style="margin: 10px 0;"><strong>🕸️  Graph Nodes:</strong></div>';
        contextInfo.graph_nodes.forEach((node, i) => {
            html += `
                <div style="background: #e3f2fd; padding: 8px; border-radius: 4px; margin-bottom: 5px; font-size: 12px;">
                    <div style="color: #1565c0; font-weight: bold;">
                        [${(node.score * 100).toFixed(1)}%] ${node.node_name} <span style="color: #666;">(${node.node_type})</span>
                    </div>
                    <div style="color: #666; margin-top: 4px;">
                        Connected: ${node.neighbors.slice(0, 3).join(', ')}${node.neighbors.length > 3 ? '...' : ''}
                    </div>
                </div>
            `;
        });
    }
    
    // Expanded Graph
    if (contextInfo?.expanded_graph && Object.keys(contextInfo.expanded_graph).length > 0) {
        html += '<div style="margin: 10px 0;"><strong>🔗 Related Concepts:</strong></div>';
        Object.entries(contextInfo.expanded_graph).forEach(([node, neighbors]) => {
            html += `
                <div style="background: #fff3e0; padding: 6px; border-radius: 4px; margin-bottom: 3px; font-size: 11px; color: #666;">
                    ${node} → ${neighbors.slice(0, 4).join(', ')}${neighbors.length > 4 ? '...' : ''}
                </div>
            `;
        });
    }
    
    panel.innerHTML = html;
    document.body.appendChild(panel);
    
    // Auto-hide after 30 seconds
    setTimeout(() => {
        panel.remove();
    }, 30000);
}

/**
 * Create the "Generate Reply" button
 */
function createGenerateButton() {
    const button = document.createElement('button');
    button.id = 'rag-generate-reply-btn';
    button.textContent = '🤖 Generate Reply';
    button.style.cssText = `
        margin: 10px 5px;
        padding: 8px 16px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    `;
    
    // Hover effect
    button.addEventListener('mouseenter', () => {
        button.style.transform = 'translateY(-1px)';
        button.style.boxShadow = '0 4px 8px rgba(0,0,0,0.15)';
    });
    
    button.addEventListener('mouseleave', () => {
        button.style.transform = 'translateY(0)';
        button.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
    });
    
    button.addEventListener('click', async () => {
        console.log('Generate Reply button clicked');
        
        // Extract email content
        const emailData = extractEmailContent();
        if (!emailData) {
            showNotification('Could not extract email content. Please try again.', 'error');
            return;
        }
        
        // Find reply box
        const replyBox = findReplyBox();
        if (!replyBox) {
            showNotification('Please open the reply box first.', 'error');
            return;
        }
        
        // Show loading
        showLoadingIndicator(button);
        
        try {
            // Generate reply
            const response = await generateReply(emailData);
            
            // Insert draft
            const success = insertDraft(response.draft_reply, replyBox);
            
            if (success) {
                // Show detailed notification with context
                const contextInfo = response.context_used;
                const faqCount = contextInfo?.faq_hits?.length || 0;
                const graphCount = contextInfo?.graph_nodes?.length || 0;
                
                showNotification(
                    `✅ Reply generated!\n` +
                    `Intent: ${response.intent}\n` +
                    `Confidence: ${(response.confidence_score * 100).toFixed(0)}%\n` +
                    `Context: ${faqCount} FAQs, ${graphCount} graph nodes`,
                    'success'
                );
                
                // Show detailed context panel
                showContextPanel(response);
                
                // Log detailed breakdown
                console.log('📊 GENERATION SUMMARY:');
                console.log(`  Intent detected: ${response.intent}`);
                console.log(`  Confidence score: ${response.confidence_score.toFixed(3)}`);
                console.log(`  Used ${faqCount} FAQ entries`);
                console.log(`  Used ${graphCount} graph nodes`);
                console.log(`  Draft length: ${response.draft_reply.length} chars`);
            } else {
                showNotification('Failed to insert draft. Please try again.', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification(
                'Failed to generate reply. Make sure the backend is running.',
                'error'
            );
        } finally {
            hideLoadingIndicator(button);
        }
    });
    
    return button;
}

/**
 * Insert the generate button near the reply box
 */
function insertGenerateButton() {
    // Check if button already exists
    if (document.getElementById('rag-generate-reply-btn')) {
        return;
    }
    
    // Find the reply button container
    const replyButtonContainers = [
        document.querySelector('div[role="button"][aria-label*="Reply"]')?.parentElement,
        document.querySelector('.btC')?.parentElement,
        document.querySelector('div.gU')
    ];
    
    for (const container of replyButtonContainers) {
        if (container) {
            console.log('Found container for button insertion');
            const button = createGenerateButton();
            container.appendChild(button);
            console.log('Generate Reply button inserted');
            return;
        }
    }
    
    // Alternative: Insert near any compose toolbar
    const toolbar = document.querySelector('div[role="toolbar"]') ||
                   document.querySelector('.btC');
    
    if (toolbar) {
        console.log('Inserting button in toolbar');
        const button = createGenerateButton();
        toolbar.appendChild(button);
        console.log('Generate Reply button inserted in toolbar');
    }
}

/**
 * Monitor for reply boxes and insert button when found
 */
function monitorForReplyBoxes() {
    insertGenerateButton();
}

/**
 * Initialize the content script
 */
function initialize() {
    console.log('Initializing Graph RAG Email Assistant...');
    
    // Insert button periodically
    setInterval(monitorForReplyBoxes, BUTTON_CHECK_INTERVAL);
    
    // Also try on page load
    setTimeout(monitorForReplyBoxes, 1000);
    
    // Listen for navigation changes (Gmail is a SPA)
    let lastUrl = location.href;
    new MutationObserver(() => {
        const currentUrl = location.href;
        if (currentUrl !== lastUrl) {
            lastUrl = currentUrl;
            console.log('Gmail navigation detected');
            setTimeout(monitorForReplyBoxes, 1000);
        }
    }).observe(document.body, { subtree: true, childList: true });
    
    console.log('Graph RAG Email Assistant initialized');
}

// Start when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
} else {
    initialize();
}

