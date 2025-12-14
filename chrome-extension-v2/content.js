/**
 * Content script for Gmail & Outlook integration
 * Extracts email content and inserts AI-generated replies
 */

console.log('AI Email Assistant: Content script loaded');

// Configuration
const DEFAULT_API_URL = 'http://localhost:8001/api';
const BUTTON_CHECK_INTERVAL = 2000;

// Detect email provider
function detectProvider() {
    const hostname = window.location.hostname;
    if (hostname.includes('mail.google.com')) {
        return 'gmail';
    } else if (hostname.includes('outlook.live.com') || 
               hostname.includes('outlook.office.com') || 
               hostname.includes('outlook.office365.com')) {
        return 'outlook';
    }
    return 'unknown';
}

const provider = detectProvider();
console.log(`Detected provider: ${provider}`);

/**
 * Get API URL from storage
 */
async function getApiUrl() {
    return new Promise((resolve) => {
        chrome.storage.sync.get(['apiUrl'], (items) => {
            resolve(items.apiUrl || DEFAULT_API_URL);
        });
    });
}

/**
 * Extract email content - Gmail
 */
function extractEmailContentGmail() {
    console.log('Extracting email content from Gmail...');
    
    const subjectElement = document.querySelector('h2.hP') || 
                          document.querySelector('[data-subject]') ||
                          document.querySelector('.ha h2');
    
    const senderElement = document.querySelector('span.gD') ||
                         document.querySelector('[email]') ||
                         document.querySelector('.go');
    
    const bodyElement = document.querySelector('div.a3s.aiL') ||
                       document.querySelector('.ii.gt') ||
                       document.querySelector('[data-message-id] .a3s');
    
    const subject = subjectElement?.innerText?.trim() || 'No Subject';
    const sender = senderElement?.getAttribute('email') || 
                  senderElement?.innerText?.trim() || 
                  'unknown@example.com';
    const body = bodyElement?.innerText?.trim() || '';
    
    console.log('Extracted Gmail data:', { subject, sender, bodyLength: body.length });
    
    if (!body) {
        console.warn('Could not extract email body from Gmail');
        return null;
    }
    
    return { subject, sender, body };
}

/**
 * Extract email content - Outlook
 */
function extractEmailContentOutlook() {
    console.log('🔍 Extracting email content from Outlook...');
    console.log('Current URL:', window.location.href);
    
    // Debug: Log all potential elements
    const allElements = document.querySelectorAll('*');
    console.log('Total elements on page:', allElements.length);
    
    // Try multiple strategies for subject
    const subjectSelectors = [
        '[aria-label*="Subject" i]',
        '[aria-label*="subject" i]',
        'div[role="heading"]',
        'h1',
        'h2',
        '[data-automation-id*="subject" i]',
        '.ms-fontColor-themePrimary',
        'div[title*="Subject" i]'
    ];
    
    let subject = 'No Subject';
    let subjectElement = null;
    for (const selector of subjectSelectors) {
        const elements = document.querySelectorAll(selector);
        for (const el of elements) {
            const text = el.innerText?.trim() || el.textContent?.trim() || '';
            // Subject should be visible and not empty, and not be part of compose box
            if (text && text.length > 0 && text.length < 200 && 
                !el.closest('[role="dialog"]') && 
                !el.closest('[aria-label*="compose" i]')) {
                subjectElement = el;
                subject = text;
                console.log('✅ Found subject with selector:', selector, 'Text:', subject.substring(0, 50));
                break;
            }
        }
        if (subjectElement) break;
    }
    
    // Try multiple strategies for sender
    const senderSelectors = [
        '[aria-label*="From" i]',
        '[aria-label*="from" i]',
        '[title*="@" i]',
        'div[role="button"][aria-label*="From" i]',
        '.ms-Persona-primaryText',
        '[data-automation-id*="sender" i]',
        '[data-automation-id*="from" i]',
        'span[title*="@" i]'
    ];
    
    let sender = 'unknown@example.com';
    let senderElement = null;
    for (const selector of senderSelectors) {
        const elements = document.querySelectorAll(selector);
        for (const el of elements) {
            const text = el.innerText?.trim() || el.textContent?.trim() || el.getAttribute('title') || '';
            const emailMatch = text.match(/[\w\.-]+@[\w\.-]+\.\w+/);
            // Make sure it's not in compose box
            if (emailMatch && !el.closest('[role="dialog"]') && !el.closest('[aria-label*="compose" i]')) {
                senderElement = el;
                sender = emailMatch[0];
                console.log('✅ Found sender with selector:', selector, 'Email:', sender);
                break;
            }
        }
        if (senderElement) break;
    }
    
    // For Outlook, the body is in the reading pane (not compose box)
    // We need to find the actual email message content
    let body = '';
    
    // Strategy 1: Look for Outlook's specific email body div with inline styles
    // Outlook uses divs with style="font-family: Aptos..." for email content
    const outlookEmailBodySelectors = [
        'div[style*="font-family: Aptos"]',
        'div[style*="font-family:Aptos"]',
        'div[style*="font-family: Aptos_EmbeddedFont"]',
        'div[style*="Calibri"]',
        'div[style*="font-size:12pt"]',
        'div[style*="direction:ltr"]',
        'div[style*="line-height:1.5"]'
    ];
    
    for (const selector of outlookEmailBodySelectors) {
        const elements = document.querySelectorAll(selector);
        for (const el of elements) {
            // Skip if it's in compose box (elementToProof) or dialog
            if (el.closest('.elementToProof') || 
                el.classList.contains('elementToProof') ||
                el.closest('[role="dialog"]') ||
                el.closest('[aria-label*="compose" i]')) {
                continue;
            }
            
            const text = el.innerText?.trim() || el.textContent?.trim() || '';
            // Look for substantial email content (not UI elements)
            if (text.length > 50 && 
                text.split(/\s+/).length > 5 && // At least 5 words
                !text.includes('Reply') && 
                !text.includes('Forward') &&
                !text.includes('Delete') &&
                !text.includes('Send')) {
                body = text;
                console.log('✅ Found Outlook email body with style selector:', selector, 'Length:', body.length);
                break;
            }
        }
        if (body) break;
    }
    
    // Strategy 2: Look for reading pane container
    const readingPaneSelectors = [
        '[data-automation-id="readingPaneContainer"]',
        '[role="main"]',
        '.ms-ReadingPaneContainer',
        '[aria-label*="Reading" i]',
        'div[role="region"][aria-label*="Reading" i]'
    ];
    
    let readingPane = null;
    for (const selector of readingPaneSelectors) {
        readingPane = document.querySelector(selector);
        if (readingPane) {
            console.log('✅ Found reading pane with selector:', selector);
            break;
        }
    }
    
    // Strategy 3: If reading pane found, look for message body inside it
    if (readingPane && !body) {
        const messageBodySelectors = [
            '[role="article"]',
            '.ms-MessageBody',
            '[data-automation-id="messageBody"]',
            'div[aria-label*="Message" i]',
            '.ms-fontColor-neutralPrimary',
            'div[dir="ltr"]',
            'div[dir="rtl"]'
        ];
        
        for (const selector of messageBodySelectors) {
            const messageContent = readingPane.querySelector(selector);
            if (messageContent) {
                const text = messageContent.innerText?.trim() || messageContent.textContent?.trim() || '';
                // Make sure it's substantial content (not just a few words)
                if (text.length > 50 && !text.includes('Reply') && !text.includes('Forward')) {
                    body = text;
                    console.log('✅ Found message body in reading pane with selector:', selector, 'Length:', body.length);
                    break;
                }
            }
        }
    }
    
    // Strategy 4: If no reading pane, try to find message content directly
    if (!body) {
        const directBodySelectors = [
            '[role="article"]',
            '.ms-MessageBody',
            '[data-automation-id="messageBody"]',
            'div[aria-label*="Message body" i]',
            'div[aria-label*="message" i]'
        ];
        
        for (const selector of directBodySelectors) {
            const elements = document.querySelectorAll(selector);
            for (const el of elements) {
                // Make sure it's not in compose box
                if (el.closest('[role="dialog"]') || el.closest('[aria-label*="compose" i]')) {
                    continue;
                }
                const text = el.innerText?.trim() || el.textContent?.trim() || '';
                if (text.length > 50) {
                    body = text;
                    console.log('✅ Found message body directly with selector:', selector, 'Length:', body.length);
                    break;
                }
            }
            if (body) break;
        }
    }
    
    // Strategy 5: Fallback - look for large text blocks that aren't UI elements
    if (!body || body.length < 10) {
        const allDivs = document.querySelectorAll('div');
        for (const div of allDivs) {
            // Skip if it's in compose box, toolbar, or other UI
            if (div.closest('[role="dialog"]') || 
                div.closest('[role="toolbar"]') ||
                div.closest('[aria-label*="compose" i]') ||
                div.closest('button') ||
                div.closest('[role="button"]')) {
                continue;
            }
            
            const text = div.innerText?.trim() || div.textContent?.trim() || '';
            // Look for substantial text blocks
            if (text.length > 100 && 
                text.split(/\s+/).length > 10 && // At least 10 words
                !text.includes('Reply') && 
                !text.includes('Forward') &&
                !text.includes('Delete')) {
                body = text;
                console.log('✅ Found message body via fallback, Length:', body.length);
                break;
            }
        }
    }
    
    console.log('📧 Extracted Outlook data:', { 
        subject: subject.substring(0, 50), 
        sender, 
        bodyLength: body.length,
        hasSubject: !!subjectElement,
        hasSender: !!senderElement,
        hasBody: body.length > 10
    });
    
    if (!body || body.length < 10) {
        console.warn('❌ Could not extract email body from Outlook');
        console.warn('Debug info:', {
            url: window.location.href,
            readingPaneFound: !!readingPane,
            allDivsCount: document.querySelectorAll('div').length
        });
        return null;
    }
    
    return { subject, sender, body };
}

/**
 * Extract email content based on provider
 */
function extractEmailContent() {
    if (provider === 'gmail') {
        return extractEmailContentGmail();
    } else if (provider === 'outlook') {
        return extractEmailContentOutlook();
    }
    return null;
}

/**
 * Find reply box - Gmail
 */
function findReplyBoxGmail() {
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
            console.log('Found Gmail reply box:', selector);
            return element;
        }
    }
    return null;
}

/**
 * Find reply box - Outlook
 */
function findReplyBoxOutlook() {
    console.log('🔍 Looking for Outlook reply box...');
    
    // Strategy 1: Look for elementToProof class (Outlook's specific reply box class)
    const elementToProof = document.querySelector('.elementToProof[contenteditable="true"]') ||
                          document.querySelector('.elementToProof');
    
    if (elementToProof) {
        // Check if it's actually editable
        const isEditable = elementToProof.isContentEditable || 
                          elementToProof.contentEditable === 'true' ||
                          elementToProof.getAttribute('contenteditable') === 'true';
        
        if (isEditable) {
            console.log('✅ Found Outlook reply box via elementToProof class');
            return elementToProof;
        } else {
            // Try to make it editable if it's not
            elementToProof.setAttribute('contenteditable', 'true');
            console.log('✅ Found elementToProof, made it editable');
            return elementToProof;
        }
    }
    
    // Strategy 2: Look for compose dialog/modal first
    const composeDialog = document.querySelector('[role="dialog"]') ||
                         document.querySelector('[aria-label*="compose" i]') ||
                         document.querySelector('[aria-label*="reply" i]') ||
                         document.querySelector('[aria-label*="Reply" i]');
    
    if (composeDialog) {
        console.log('✅ Found compose dialog');
        
        // Look for elementToProof inside dialog first
        const proofInDialog = composeDialog.querySelector('.elementToProof[contenteditable="true"]') ||
                             composeDialog.querySelector('.elementToProof');
        
        if (proofInDialog) {
            const isEditable = proofInDialog.isContentEditable || 
                              proofInDialog.contentEditable === 'true';
            if (isEditable) {
                console.log('✅ Found elementToProof in compose dialog');
                return proofInDialog;
            } else {
                proofInDialog.setAttribute('contenteditable', 'true');
                console.log('✅ Found elementToProof in dialog, made it editable');
                return proofInDialog;
            }
        }
        
        // Look for contenteditable elements inside the dialog
        const contentEditables = composeDialog.querySelectorAll('[contenteditable="true"]');
        console.log('Found contenteditable elements in dialog:', contentEditables.length);
        
        for (const el of contentEditables) {
            // Check if it's the message body (not a subject or other field)
            const ariaLabel = el.getAttribute('aria-label') || '';
            const role = el.getAttribute('role') || '';
            
            if (ariaLabel.toLowerCase().includes('message') ||
                ariaLabel.toLowerCase().includes('body') ||
                role === 'textbox') {
                console.log('✅ Found Outlook reply box in dialog:', ariaLabel);
                return el;
            }
        }
        
        // If no specific match, use the largest contenteditable
        if (contentEditables.length > 0) {
            let largest = contentEditables[0];
            for (const el of contentEditables) {
                if (el.innerText.length > largest.innerText.length) {
                    largest = el;
                }
            }
            console.log('✅ Using largest contenteditable as reply box');
            return largest;
        }
    }
    
    // Strategy 3: Direct selectors for reply box
    const selectors = [
        'div[aria-label*="Message body" i][contenteditable="true"]',
        'div[aria-label*="message body" i][contenteditable="true"]',
        'div[role="textbox"][aria-label*="Message" i]',
        'div[contenteditable="true"][aria-label*="Message" i]',
        '[data-automation-id="messageBody"][contenteditable="true"]',
        '.ms-Editor-content[contenteditable="true"]',
        'div[contenteditable="true"].ms-Editor-content',
        'div[contenteditable="true"][role="textbox"]',
        'div[contenteditable="true"]'
    ];
    
    for (const selector of selectors) {
        const elements = document.querySelectorAll(selector);
        for (const element of elements) {
            // Make sure it's actually editable and in a compose context
            if (element.isContentEditable && 
                (element.closest('[role="dialog"]') || 
                 element.getAttribute('aria-label')?.toLowerCase().includes('message'))) {
                console.log('✅ Found Outlook reply box:', selector);
                return element;
            }
        }
    }
    
    // Strategy 4: Find all contenteditable and filter
    const allContentEditables = document.querySelectorAll('[contenteditable="true"]');
    console.log('Found total contenteditable elements:', allContentEditables.length);
    
    for (const el of allContentEditables) {
        // Skip if it's clearly not a message body
        const ariaLabel = (el.getAttribute('aria-label') || '').toLowerCase();
        const parentAriaLabel = (el.closest('[aria-label]')?.getAttribute('aria-label') || '').toLowerCase();
        
        if (ariaLabel.includes('subject') || 
            ariaLabel.includes('to') || 
            ariaLabel.includes('cc') ||
            ariaLabel.includes('bcc')) {
            continue;
        }
        
        // Prefer elements in dialogs or with message-related labels
        if (el.closest('[role="dialog"]') || 
            ariaLabel.includes('message') || 
            parentAriaLabel.includes('message') ||
            parentAriaLabel.includes('reply') ||
            parentAriaLabel.includes('compose')) {
            console.log('✅ Found Outlook reply box via filtering:', ariaLabel || 'no label');
            return el;
        }
    }
    
    console.warn('❌ Could not find Outlook reply box');
    return null;
}

/**
 * Find reply box based on provider
 */
function findReplyBox() {
    if (provider === 'gmail') {
        return findReplyBoxGmail();
    } else if (provider === 'outlook') {
        return findReplyBoxOutlook();
    }
    return null;
}

/**
 * Insert draft into reply box
 */
function insertDraft(draftText, replyBox) {
    if (!replyBox) {
        console.error('❌ No reply box provided');
        return false;
    }
    
    console.log('📝 Inserting draft into reply box...');
    console.log('Reply box element:', replyBox);
    console.log('Is contenteditable:', replyBox.isContentEditable);
    console.log('Provider:', provider);
    
    try {
        // Focus first to ensure Outlook recognizes the element
        replyBox.focus();
        
        // Wait a bit for focus to take effect (especially for Outlook)
        setTimeout(() => {
            const paragraphs = draftText.split(/\n\n+/).filter(p => p.trim().length > 0);
            
            let htmlContent;
            if (paragraphs.length > 1) {
                htmlContent = paragraphs
                    .map(paragraph => {
                        return `<p>${paragraph.trim().replace(/\n/g, '<br>')}</p>`;
                    })
                    .join('');
            } else {
                htmlContent = draftText.replace(/\n/g, '<br>');
            }
            
            // Clear existing content first
            if (provider === 'outlook') {
                // For Outlook, especially elementToProof, we need to be careful
                try {
                    // Check if it's elementToProof
                    if (replyBox.classList.contains('elementToProof')) {
                        // For elementToProof, replace the inner content
                        // Outlook expects the content in a specific format
                        replyBox.innerHTML = htmlContent;
                        // Ensure it stays editable
                        replyBox.setAttribute('contenteditable', 'true');
                    } else {
                        // Method 1: Direct innerHTML for other Outlook elements
                        replyBox.innerHTML = htmlContent;
                    }
                } catch (e) {
                    console.warn('innerHTML failed, trying textContent:', e);
                    // Method 2: textContent as fallback
                    replyBox.textContent = draftText;
                    // Ensure editable
                    replyBox.setAttribute('contenteditable', 'true');
                }
            } else {
                // Gmail
                replyBox.innerHTML = htmlContent;
            }
            
            // Move cursor to end
            const range = document.createRange();
            const selection = window.getSelection();
            
            if (replyBox.childNodes.length > 0) {
                range.selectNodeContents(replyBox);
                range.collapse(false);
            } else {
                range.setStart(replyBox, 0);
                range.setEnd(replyBox, 0);
            }
            
            selection.removeAllRanges();
            selection.addRange(range);
            
            // Trigger multiple events for better compatibility
            const events = [
                new Event('input', { bubbles: true, cancelable: true }),
                new Event('change', { bubbles: true, cancelable: true }),
                new KeyboardEvent('keydown', { bubbles: true, cancelable: true, key: 'Enter' }),
                new KeyboardEvent('keyup', { bubbles: true, cancelable: true, key: 'Enter' }),
                new KeyboardEvent('keypress', { bubbles: true, cancelable: true, key: 'Enter' })
            ];
            
            events.forEach(event => {
                try {
                    replyBox.dispatchEvent(event);
                } catch (e) {
                    // Some events might fail, that's okay
                }
            });
            
            // Focus again to ensure cursor is visible
            replyBox.focus();
            
            console.log('✅ Draft inserted successfully');
        }, 100);
        
        return true;
    } catch (error) {
        console.error('❌ Failed to insert draft:', error);
        console.error('Error details:', {
            message: error.message,
            stack: error.stack,
            replyBox: replyBox
        });
        return false;
    }
}

/**
 * Call the backend API to generate a reply
 */
async function generateReply(emailData) {
    console.log('Calling API to generate reply...');
    
    const apiUrl = await getApiUrl();
    
    try {
        const response = await fetch(`${apiUrl}/generate-reply`, {
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
        
        // Log detailed context
        console.log('🎯 RETRIEVAL DETAILS:');
        console.log('  Intent:', result.intent);
        console.log('  Artifacts:', result.artifacts || []);
        console.log('  Confidence:', result.confidence_score);
        console.log('  Auto-send:', result.auto_send);
        
        if (result.context_used) {
            console.log('\n📚 FAQ Hits:', result.context_used.faq_hits?.length || 0);
            result.context_used.faq_hits?.forEach((faq, i) => {
                console.log(`    [${i+1}] Score: ${faq.score.toFixed(3)} - ${faq.question}`);
            });
            
            console.log('\n📧 Graph Replies:', result.context_used.graph_replies?.length || 0);
            console.log('  Matching emails found:', result.context_used.graph_emails_found || 0);
        }
        
        return result;
    } catch (error) {
        console.error('Failed to generate reply:', error);
        throw error;
    }
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `ai-email-notification ai-email-notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

/**
 * Show context panel
 */
function showContextPanel(response) {
    const existing = document.getElementById('ai-email-context-panel');
    if (existing) existing.remove();
    
    const panel = document.createElement('div');
    panel.id = 'ai-email-context-panel';
    panel.className = 'ai-email-context-panel';
    
    const contextInfo = response.context_used;
    const artifacts = response.artifacts || [];
    
    let html = `
        <div class="context-header">
            <h3>🔍 Retrieval Context</h3>
            <button class="context-close" aria-label="Close">✕</button>
        </div>
        <div class="context-summary">
            <div class="context-item">
                <strong>Intent:</strong> ${response.intent}
            </div>
            <div class="context-item">
                <strong>Artifacts:</strong> ${artifacts.join(', ') || 'None'}
            </div>
            <div class="context-item">
                <strong>Confidence:</strong> ${(response.confidence_score * 100).toFixed(1)}%
            </div>
            <div class="context-item">
                <strong>Auto-send:</strong> ${response.auto_send ? '✅ Yes' : '❌ No'}
            </div>
        </div>
    `;
    
    if (contextInfo?.faq_hits?.length > 0) {
        html += '<div class="context-section"><strong>📚 FAQ Matches:</strong></div>';
        contextInfo.faq_hits.forEach((faq, i) => {
            html += `
                <div class="context-faq">
                    <div class="context-faq-score">[${(faq.score * 100).toFixed(1)}%] ${faq.question}</div>
                    <div class="context-faq-answer">${faq.answer.substring(0, 100)}${faq.answer.length > 100 ? '...' : ''}</div>
                </div>
            `;
        });
    }
    
    if (contextInfo?.graph_replies?.length > 0) {
        html += '<div class="context-section"><strong>📧 Similar Email Replies:</strong></div>';
        html += `<div class="context-subtitle">Found ${contextInfo.graph_emails_found || 0} matching emails</div>`;
        contextInfo.graph_replies.forEach((reply, i) => {
            html += `
                <div class="context-reply">
                    <div class="context-reply-title">Example Reply ${i + 1}:</div>
                    <div class="context-reply-content">${reply.substring(0, 150)}${reply.length > 150 ? '...' : ''}</div>
                </div>
            `;
        });
    }
    
    panel.innerHTML = html;
    document.body.appendChild(panel);
    
    // Close button
    panel.querySelector('.context-close').addEventListener('click', () => {
        panel.remove();
    });
    
    // Auto-hide after 30 seconds
    setTimeout(() => {
        if (panel.parentNode) {
            panel.remove();
        }
    }, 30000);
}

/**
 * Create generate button
 */
function createGenerateButton() {
    const button = document.createElement('button');
    button.id = 'ai-email-generate-btn';
    button.className = 'ai-email-generate-btn';
    button.innerHTML = `
        <svg class="btn-icon" viewBox="0 0 24 24" fill="none">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="currentColor"/>
        </svg>
        <span>Generate Reply</span>
    `;
    
    button.addEventListener('click', async () => {
        console.log('Generate Reply button clicked');
        
        const emailData = extractEmailContent();
        if (!emailData) {
            const errorMsg = provider === 'outlook' 
                ? 'Could not extract email content. Make sure you\'re viewing an email (not compose window). Try refreshing the page.'
                : 'Could not extract email content. Please try again.';
            showNotification(errorMsg, 'error');
            console.error('❌ Email extraction failed. Run debugAIEmailAssistant() for details.');
            return;
        }
        
        const replyBox = findReplyBox();
        if (!replyBox) {
            const errorMsg = provider === 'outlook'
                ? 'Please click Reply first to open the compose window.'
                : 'Please open the reply box first.';
            showNotification(errorMsg, 'error');
            console.error('❌ Reply box not found. Run debugAIEmailAssistant() for details.');
            return;
        }
        
        button.disabled = true;
        button.innerHTML = `
            <svg class="btn-icon spinning" viewBox="0 0 24 24" fill="none">
                <path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z" fill="currentColor"/>
            </svg>
            <span>Generating...</span>
        `;
        
        try {
            const response = await generateReply(emailData);
            
            // Double-check reply box is still available
            const currentReplyBox = findReplyBox();
            if (!currentReplyBox) {
                showNotification('Reply box not found. Please open the reply window again.', 'error');
                return;
            }
            
            const success = insertDraft(response.draft_reply, currentReplyBox);
            
            if (success) {
                const contextInfo = response.context_used;
                const faqCount = contextInfo?.faq_hits?.length || 0;
                const graphReplyCount = contextInfo?.graph_replies?.length || 0;
                const artifacts = response.artifacts || [];
                
                showNotification(
                    `✅ Reply generated! Intent: ${response.intent} | Confidence: ${(response.confidence_score * 100).toFixed(0)}%`,
                    'success'
                );
                
                showContextPanel(response);
            } else {
                showNotification('Failed to insert draft. Please try again.', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('Failed to generate reply. Make sure the backend is running.', 'error');
        } finally {
            button.disabled = false;
            button.innerHTML = `
                <svg class="btn-icon" viewBox="0 0 24 24" fill="none">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="currentColor"/>
                </svg>
                <span>Generate Reply</span>
            `;
        }
    });
    
    return button;
}

/**
 * Insert generate button
 */
function insertGenerateButton() {
    if (document.getElementById('ai-email-generate-btn')) {
        return;
    }
    
    let container = null;
    
    if (provider === 'gmail') {
        const replyButtonContainers = [
            document.querySelector('div[role="button"][aria-label*="Reply"]')?.parentElement,
            document.querySelector('.btC')?.parentElement,
            document.querySelector('div.gU')
        ];
        
        for (const c of replyButtonContainers) {
            if (c) {
                container = c;
                break;
            }
        }
    } else if (provider === 'outlook') {
        console.log('🔍 Looking for Outlook button container...');
        
        // Strategy 1: Look for compose dialog toolbar
        const composeDialog = document.querySelector('[role="dialog"]');
        if (composeDialog) {
            const toolbar = composeDialog.querySelector('[role="toolbar"]') ||
                           composeDialog.querySelector('[data-automation-id="commandBar"]') ||
                           composeDialog.querySelector('.ms-CommandBar');
            if (toolbar) {
                container = toolbar;
                console.log('✅ Found toolbar in compose dialog');
            }
        }
        
        // Strategy 2: Look for reply button and its container
        if (!container) {
            const replyBtnSelectors = [
                'button[aria-label*="Reply" i]',
                '[aria-label*="Reply" i][role="button"]',
                '[title*="Reply" i]',
                '[data-automation-id*="reply" i]',
                'button[title*="Reply" i]'
            ];
            
            for (const selector of replyBtnSelectors) {
                const replyBtn = document.querySelector(selector);
                if (replyBtn) {
                    // Try to find toolbar or button group
                    container = replyBtn.closest('[role="toolbar"]') ||
                              replyBtn.closest('[data-automation-id="commandBar"]') ||
                              replyBtn.closest('.ms-CommandBar') ||
                              replyBtn.parentElement;
                    if (container) {
                        console.log('✅ Found container via reply button:', selector);
                        break;
                    }
                }
            }
        }
        
        // Strategy 3: Look for any toolbar
        if (!container) {
            const toolbars = document.querySelectorAll('[role="toolbar"]');
            for (const toolbar of toolbars) {
                // Prefer toolbars that contain reply-related buttons
                if (toolbar.textContent.includes('Reply') || 
                    toolbar.querySelector('[aria-label*="Reply" i]')) {
                    container = toolbar;
                    console.log('✅ Found toolbar with reply button');
                    break;
                }
            }
        }
        
        // Strategy 4: Insert directly into compose dialog header/footer
        if (!container && composeDialog) {
            const header = composeDialog.querySelector('[role="banner"]') ||
                          composeDialog.querySelector('header') ||
                          composeDialog.firstElementChild;
            if (header) {
                container = header;
                console.log('✅ Using compose dialog header');
            }
        }
        
        // Strategy 5: Last resort - create our own container
        if (!container && composeDialog) {
            // Create a toolbar div and insert it
            const newToolbar = document.createElement('div');
            newToolbar.style.cssText = 'display: flex; gap: 8px; padding: 8px;';
            composeDialog.insertBefore(newToolbar, composeDialog.firstChild);
            container = newToolbar;
            console.log('✅ Created new toolbar container');
        }
    }
    
    if (container) {
        const button = createGenerateButton();
        container.appendChild(button);
        console.log('Generate Reply button inserted');
    }
}

/**
 * Monitor for reply boxes
 */
function monitorForReplyBoxes() {
    insertGenerateButton();
}

/**
 * Debug helper - expose to window for console access
 */
function debugOutlook() {
    console.log('🔍 DEBUG: Outlook Email Assistant');
    console.log('Provider:', provider);
    console.log('URL:', window.location.href);
    
    // Test email extraction
    console.log('\n📧 Testing email extraction...');
    const emailData = extractEmailContent();
    console.log('Extracted data:', emailData);
    
    // Test reply box finding
    console.log('\n📝 Testing reply box finding...');
    const replyBox = findReplyBox();
    console.log('Reply box:', replyBox);
    if (replyBox) {
        console.log('Reply box details:', {
            isContentEditable: replyBox.isContentEditable,
            ariaLabel: replyBox.getAttribute('aria-label'),
            role: replyBox.getAttribute('role'),
            inDialog: !!replyBox.closest('[role="dialog"]')
        });
    }
    
    // Test button insertion
    console.log('\n🔘 Testing button insertion...');
    const button = document.getElementById('ai-email-generate-btn');
    console.log('Button exists:', !!button);
    
    return {
        provider,
        emailData,
        replyBox,
        buttonExists: !!button
    };
}

// Expose debug function to window
window.debugAIEmailAssistant = debugOutlook;

/**
 * Initialize
 */
function initialize() {
    console.log(`🚀 Initializing AI Email Assistant for ${provider}...`);
    console.log(`📍 URL: ${window.location.href}`);
    
    if (provider === 'unknown') {
        console.warn('⚠️ Unknown email provider, extension may not work correctly');
        return;
    }
    
    // Log helpful debug command
    console.log('💡 Tip: Run debugAIEmailAssistant() in console to debug issues');
    
    setInterval(monitorForReplyBoxes, BUTTON_CHECK_INTERVAL);
    setTimeout(monitorForReplyBoxes, 1000);
    
    // Listen for navigation changes
    let lastUrl = location.href;
    new MutationObserver(() => {
        const currentUrl = location.href;
        if (currentUrl !== lastUrl) {
            lastUrl = currentUrl;
            console.log('🔄 Navigation detected, reinitializing...');
            setTimeout(monitorForReplyBoxes, 1000);
        }
    }).observe(document.body, { subtree: true, childList: true });
    
    console.log('✅ AI Email Assistant initialized');
}

// Start when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
} else {
    initialize();
}

