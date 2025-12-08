# Golden Dataset Benchmark Summary

## Overview
This golden dataset contains **20 carefully crafted emails** designed to benchmark the AI email automation agent. The dataset covers all topics, intents, artifacts, and edge cases while maintaining variations from the original `generated_email_pairs.json`.

## Coverage Statistics

### Topics Covered (5/5)
- ✅ Professor/Academic (7 emails)
- ✅ Recruiter/Job Search (7 emails)
- ✅ Group/Event Coordination (3 emails)
- ✅ Feedback & Reviews (3 emails)
- ✅ Scheduling (3 emails)

### Intents Covered (8/8)
- ✅ schedule (6 emails)
- ✅ request_feedback (4 emails)
- ✅ send_materials (5 emails)
- ✅ accept_or_decline (2 emails)
- ✅ reschedule (2 emails)
- ✅ request_info (3 emails)
- ✅ confirm (2 emails)
- ✅ share_feedback (1 email)

### Artifacts Covered (10/10)
- ✅ calendly (6 emails)
- ✅ zoom_link (5 emails)
- ✅ ds_resume (4 emails)
- ✅ swe_resume (3 emails)
- ✅ linkedin_profile (3 emails)
- ✅ portfolio (2 emails)
- ✅ github (2 emails)
- ✅ draft (3 emails)
- ✅ report (2 emails)
- ✅ phone_number (3 emails)

## Edge Cases Covered

### 1. Multiple Intents in Single Email
- **benchmark_001**: schedule + request_feedback
- **benchmark_002**: send_materials + schedule
- **benchmark_010**: schedule + request_feedback
- **benchmark_014**: send_materials + request_feedback
- **benchmark_015**: confirm + request_info
- **benchmark_019**: schedule + request_feedback

### 2. Multiple Artifacts in Single Email
- **benchmark_002**: ds_resume + linkedin_profile + calendly
- **benchmark_008**: portfolio + github
- **benchmark_012**: zoom_link + phone_number
- **benchmark_017**: ds_resume + swe_resume

### 3. Urgent Requests
- **benchmark_001**: "urgently" + "within 48 hours"
- **benchmark_012**: "URGENT" in subject + family emergency

### 4. Vague/Ambiguous Requests
- **benchmark_016**: Very short, unclear request ("Need to discuss something")

### 5. Decline Scenarios
- **benchmark_009**: Declining workshop invitation due to constraints

### 6. Complex Multi-Step Requests
- **benchmark_014**: Requesting both materials to be sent AND feedback to be provided
- **benchmark_015**: Confirming meeting AND requesting agenda items

### 7. Different Communication Styles
- **benchmark_003**: Casual ("Hey Zubair")
- **benchmark_004**: Professional but brief
- **benchmark_011**: Formal feedback sharing
- **benchmark_016**: Very informal

### 8. Context Variations
- Similar scenarios to `generated_email_pairs.json` but with:
  - Different sender names/companies
  - Different timeframes
  - Different specific details
  - Different urgency levels
  - Different formality levels

## Key Differences from `generated_email_pairs.json`

1. **Varied Scenarios**: Similar contexts but with different details (e.g., "thesis defense" vs "thesis guidance", "ML Engineer" vs "Data Scientist")
2. **Different Urgency Levels**: Mix of urgent and non-urgent requests
3. **Different Formality**: Range from very formal to casual
4. **Different Complexity**: Mix of simple single-intent and complex multi-intent emails
5. **Edge Case Focus**: More emphasis on challenging scenarios (multiple intents/artifacts, vague requests, declines)

## Usage

This dataset can be used to:
1. **Benchmark Intent Classification**: Test accuracy of intent detection
2. **Benchmark Artifact Identification**: Test accuracy of artifact selection
3. **Benchmark Reply Generation**: Test quality of generated replies
4. **Test Edge Cases**: Evaluate system performance on complex scenarios
5. **Measure System Robustness**: Test handling of vague, urgent, or multi-part requests

## Format

Each entry follows the format from `generated_email_pairs.json`:
```json
{
  "id": "benchmark_XXX",
  "labels": {
    "topic": "...",
    "intents": ["..."],
    "artifacts": ["..."]
  },
  "subject": "...",
  "sender_email": "...",
  "prospect_email": "...",
  "reply": "..."
}
```

## Notes

- All replies end with "Best Regards,\nZubair" as per the standard format
- All links and contact information match the FAQ data
- Email lengths are kept reasonable (400-500 characters as per guidelines)
- Replies are contextually appropriate and professional

