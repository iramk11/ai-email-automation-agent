"""
Simple rule-based intent classifier as fallback.
Use this if LLM-based classification is unreliable.
"""
from typing import List
import re


def classify_intent_simple(email_text: str) -> List[str]:
    """
    Simple rule-based intent classification.
    More reliable than LLM for structured intent detection.
    """
    text_lower = email_text.lower()
    intents = []
    
    # send_materials patterns
    if any(word in text_lower for word in [
        'share your resume', 'send resume', 'share resume',
        'send your cv', 'share cv', 'attach resume',
        'send portfolio', 'share portfolio',
        'send linkedin', 'share linkedin',
        'send github', 'share github',
        'share your materials', 'send materials'
    ]):
        intents.append('send_materials')
    
    # request_info patterns
    if any(word in text_lower for word in [
        'provide the', 'provide your', 'share the',
        'time to connect', 'time for', 'availability',
        'let me know', 'kindly share', 'please provide'
    ]):
        if 'send_materials' not in intents:  # Only if not already sending materials
            intents.append('request_info')
        elif any(w in text_lower for w in ['time', 'availability', 'schedule', 'meet', 'call']):
            intents.append('request_info')
    
    # schedule patterns
    if any(word in text_lower for word in [
        'schedule', 'set up', 'arrange', 'book',
        'meeting', 'call', 'interview',
        'zoom', 'google meet', 'teams meeting'
    ]):
        if 'schedule' not in [i for i in intents]:
            intents.append('schedule')
    
    # confirm patterns
    if any(word in text_lower for word in [
        'confirm', 'confirmation', 'confirming'
    ]):
        intents.append('confirm')
    
    # reschedule patterns
    if any(word in text_lower for word in [
        'reschedule', 'rescheduling', 'change the time',
        'different time', 'postpone'
    ]):
        intents.append('reschedule')
    
    # request_feedback patterns
    if any(word in text_lower for word in [
        'feedback', 'review', 'thoughts on', 'your input',
        'what do you think'
    ]):
        intents.append('request_feedback')
    
    # share_feedback patterns
    if any(word in text_lower for word in [
        'here is my feedback', 'my thoughts', 'my review',
        'suggestions', 'comments on'
    ]):
        intents.append('share_feedback')
    
    # accept_or_decline patterns
    if any(word in text_lower for word in [
        'accept', 'decline', 'offer', 'invitation',
        'rsvp', 'will you', 'can you join'
    ]):
        intents.append('accept_or_decline')
    
    # follow_up patterns
    if any(word in text_lower for word in [
        'follow up', 'following up', 'checking in',
        'any update', 'status update'
    ]):
        intents.append('follow_up')
    
    # Default to general_inquiry if nothing matched
    if not intents:
        intents.append('general_inquiry')
    
    return intents


# Test the classifier
if __name__ == "__main__":
    test_emails = [
        "Please share your resume and provide the right time to connect with you for an online meeting.",
        "Can we reschedule our meeting to Thursday?",
        "I'd love to get your feedback on the project draft.",
        "Confirming our interview tomorrow at 2pm."
    ]
    
    print("Testing Simple Intent Classifier:\n")
    for email in test_emails:
        intents = classify_intent_simple(email)
        print(f"Email: {email[:60]}...")
        print(f"Intents: {intents}\n")

