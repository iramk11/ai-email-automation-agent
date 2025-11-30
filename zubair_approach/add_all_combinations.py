#!/usr/bin/env python3
"""
Add all remaining combination cells (5-21) to the notebook.
"""

import json
import nbformat
from nbformat.v4 import new_code_cell

# Read existing notebook
with open('generate_email_dataset.ipynb', 'r') as f:
    nb = nbformat.read(f, as_version=4)

# Define all remaining combinations (5-21)
combinations = [
    {
        "num": 5,
        "topic": "Professor/Academic",
        "intents": ["send_materials", "request_feedback"],
        "artifacts": ["report", "draft"],
        "prompt": '''Generate 5 different email pairs (incoming email + reply) with these specifications:

TOPIC: Professor/Academic
INTENTS: send_materials, request_feedback (professor requests materials AND feedback)
ARTIFACTS: report, draft (Zubair sends both a report and draft)

INCOMING EMAIL GUIDELINES:
- Professor requesting both materials (report) and feedback on a draft
- Could be research progress report + draft paper, project report + proposal draft, etc.
- Professional academic tone
- 400-500 characters
- Include sender name and email (university domain)

REPLY GUIDELINES:
- Zubair acknowledges both requests
- Mentions sending report and draft document
- Offers to discuss further
- 400-500 characters
- Must end with: "Best Regards,\\nZubair"

OUTPUT FORMAT (JSON):
{
  "email_1": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_2": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_3": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_4": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_5": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."}
}'''
    },
    {
        "num": 6,
        "topic": "Recruiter/Job Search",
        "intents": ["send_materials"],
        "artifacts": ["swe_resume"],
        "prompt": '''Generate 5 different email pairs (incoming email + reply) with these specifications:

TOPIC: Recruiter/Job Search
INTENT: send_materials (recruiter requests resume/materials)
ARTIFACT: swe_resume (Zubair shares Software Engineering resume)

INCOMING EMAIL GUIDELINES:
- Recruiter from tech company reaching out about software engineering position
- Requests resume or application materials
- Professional recruiter tone
- 400-500 characters
- Include sender name, company, and email (company domain)

REPLY GUIDELINES:
- Zubair responds professionally
- Shares SWE resume link: https://drive.google.com/file/d/1NsbClvTx1MgSHhjvdcdpdTppI5MXxtYQ/view?usp=sharing
- Expresses interest in the opportunity
- 400-500 characters
- Must end with: "Best Regards,\\nZubair"

OUTPUT FORMAT (JSON):
{
  "email_1": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_2": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_3": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_4": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_5": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."}
}'''
    },
    {
        "num": 7,
        "topic": "Recruiter/Job Search",
        "intents": ["send_materials"],
        "artifacts": ["ds_resume"],
        "prompt": '''Generate 5 different email pairs (incoming email + reply) with these specifications:

TOPIC: Recruiter/Job Search
INTENT: send_materials (recruiter requests resume/materials)
ARTIFACT: ds_resume (Zubair shares Data Science resume)

INCOMING EMAIL GUIDELINES:
- Recruiter from company reaching out about data science/ML position
- Requests resume or application materials
- Professional recruiter tone
- 400-500 characters
- Include sender name, company, and email (company domain)

REPLY GUIDELINES:
- Zubair responds professionally
- Shares DS resume link: https://drive.google.com/file/d/16lp87m0BbAx4uTPcdHGCIDHEdSQtywy0/view?usp=sharing
- Expresses interest in the data science opportunity
- 400-500 characters
- Must end with: "Best Regards,\\nZubair"

OUTPUT FORMAT (JSON):
{
  "email_1": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_2": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_3": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_4": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_5": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."}
}'''
    },
    {
        "num": 8,
        "topic": "Recruiter/Job Search",
        "intents": ["request_info"],
        "artifacts": ["linkedin_profile"],
        "prompt": '''Generate 5 different email pairs (incoming email + reply) with these specifications:

TOPIC: Recruiter/Job Search
INTENT: request_info (recruiter wants more information about Zubair)
ARTIFACT: linkedin_profile (Zubair shares LinkedIn profile)

INCOMING EMAIL GUIDELINES:
- Recruiter interested in learning more about Zubair's background
- Asks for LinkedIn profile or professional information
- Professional recruiter tone
- 400-500 characters
- Include sender name, company, and email (company domain)

REPLY GUIDELINES:
- Zubair responds professionally
- Shares LinkedIn profile: https://www.linkedin.com/in/zubair-atha/
- Mentions willingness to discuss further
- 400-500 characters
- Must end with: "Best Regards,\\nZubair"

OUTPUT FORMAT (JSON):
{
  "email_1": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_2": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_3": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_4": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_5": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."}
}'''
    },
    {
        "num": 9,
        "topic": "Recruiter/Job Search",
        "intents": ["schedule"],
        "artifacts": ["zoom_link"],
        "prompt": '''Generate 5 different email pairs (incoming email + reply) with these specifications:

TOPIC: Recruiter/Job Search
INTENT: schedule (recruiter wants to schedule interview/call)
ARTIFACT: zoom_link (Zubair provides Zoom link)

INCOMING EMAIL GUIDELINES:
- Recruiter wants to schedule an interview or phone call
- Mentions next steps in hiring process
- Professional recruiter tone
- 400-500 characters
- Include sender name, company, and email (company domain)

REPLY GUIDELINES:
- Zubair confirms availability
- Shares Zoom link: https://us05web.zoom.us/j/5756631049?pwd=2whWm7gb5MHL5GIspFbviES0GQPuyE.1
- Mentions Meeting ID: 575 663 1049 and Passcode: 4Jp5UP
- 400-500 characters
- Must end with: "Best Regards,\\nZubair"

OUTPUT FORMAT (JSON):
{
  "email_1": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_2": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_3": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_4": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_5": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."}
}'''
    },
    {
        "num": 10,
        "topic": "Recruiter/Job Search",
        "intents": ["send_materials"],
        "artifacts": ["swe_resume", "linkedin_profile"],
        "prompt": '''Generate 5 different email pairs (incoming email + reply) with these specifications:

TOPIC: Recruiter/Job Search
INTENT: send_materials (recruiter requests materials)
ARTIFACTS: swe_resume, linkedin_profile (Zubair shares both SWE resume and LinkedIn)

INCOMING EMAIL GUIDELINES:
- Recruiter requesting resume and professional profile
- Software engineering or tech position
- Professional recruiter tone
- 400-500 characters
- Include sender name, company, and email (company domain)

REPLY GUIDELINES:
- Zubair responds professionally
- Shares SWE resume: https://drive.google.com/file/d/1NsbClvTx1MgSHhjvdcdpdTppI5MXxtYQ/view?usp=sharing
- Shares LinkedIn: https://www.linkedin.com/in/zubair-atha/
- Expresses interest
- 400-500 characters
- Must end with: "Best Regards,\\nZubair"

OUTPUT FORMAT (JSON):
{
  "email_1": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_2": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_3": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_4": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_5": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."}
}'''
    },
    {
        "num": 11,
        "topic": "Recruiter/Job Search",
        "intents": ["send_materials"],
        "artifacts": ["portfolio", "github"],
        "prompt": '''Generate 5 different email pairs (incoming email + reply) with these specifications:

TOPIC: Recruiter/Job Search
INTENT: send_materials (recruiter requests portfolio/work samples)
ARTIFACTS: portfolio, github (Zubair shares both portfolio and GitHub)

INCOMING EMAIL GUIDELINES:
- Recruiter interested in seeing portfolio and code samples
- Software engineering or developer position
- Professional recruiter tone
- 400-500 characters
- Include sender name, company, and email (company domain)

REPLY GUIDELINES:
- Zubair responds professionally
- Shares Portfolio: https://zubairatha.vercel.app/
- Shares GitHub: https://github.com/zubairatha
- Mentions relevant projects
- 400-500 characters
- Must end with: "Best Regards,\\nZubair"

OUTPUT FORMAT (JSON):
{
  "email_1": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_2": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_3": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_4": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_5": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."}
}'''
    },
    {
        "num": 12,
        "topic": "Group/Event Coordination",
        "intents": ["schedule"],
        "artifacts": ["calendly"],
        "prompt": '''Generate 5 different email pairs (incoming email + reply) with these specifications:

TOPIC: Group/Event Coordination
INTENT: schedule (group/team wants to schedule meeting/event)
ARTIFACT: calendly (Zubair shares Calendly link)

INCOMING EMAIL GUIDELINES:
- Team member or event coordinator reaching out to schedule group meeting
- Could be project meeting, team sync, event planning, etc.
- Friendly professional tone
- 400-500 characters
- Include sender name and email (university/company domain)

REPLY GUIDELINES:
- Zubair responds positively
- Shares Calendly link: https://calendly.com/za2366-columbia/30min
- Mentions availability
- 400-500 characters
- Must end with: "Best Regards,\\nZubair"

OUTPUT FORMAT (JSON):
{
  "email_1": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_2": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_3": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_4": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_5": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."}
}'''
    },
    {
        "num": 13,
        "topic": "Group/Event Coordination",
        "intents": ["request_feedback"],
        "artifacts": [],
        "prompt": '''Generate 5 different email pairs (incoming email + reply) with these specifications:

TOPIC: Group/Event Coordination
INTENT: request_feedback (team member requests feedback)
ARTIFACTS: None (Zubair provides feedback but doesn't send documents)

INCOMING EMAIL GUIDELINES:
- Team member asking for feedback on project, presentation, or work
- Could be slides, proposal, event plan, etc.
- Friendly collaborative tone
- 400-500 characters
- Include sender name and email (university/company domain)

REPLY GUIDELINES:
- Zubair provides constructive feedback
- Offers to discuss further if needed
- No documents shared, just feedback in email
- 400-500 characters
- Must end with: "Best Regards,\\nZubair"

OUTPUT FORMAT (JSON):
{
  "email_1": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_2": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_3": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_4": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_5": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."}
}'''
    },
    {
        "num": 14,
        "topic": "Group/Event Coordination",
        "intents": ["reschedule"],
        "artifacts": ["zoom_link"],
        "prompt": '''Generate 5 different email pairs (incoming email + reply) with these specifications:

TOPIC: Group/Event Coordination
INTENT: reschedule (team wants to reschedule meeting)
ARTIFACT: zoom_link (Zubair provides Zoom link for rescheduled meeting)

INCOMING EMAIL GUIDELINES:
- Team member requesting to reschedule group meeting
- Mentions reason or new proposed time
- Friendly professional tone
- 400-500 characters
- Include sender name and email (university/company domain)

REPLY GUIDELINES:
- Zubair confirms reschedule
- Shares Zoom link: https://us05web.zoom.us/j/5756631049?pwd=2whWm7gb5MHL5GIspFbviES0GQPuyE.1
- Mentions Meeting ID: 575 663 1049 and Passcode: 4Jp5UP
- 400-500 characters
- Must end with: "Best Regards,\\nZubair"

OUTPUT FORMAT (JSON):
{
  "email_1": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_2": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_3": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_4": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_5": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."}
}'''
    },
    {
        "num": 15,
        "topic": "Group/Event Coordination",
        "intents": ["confirm", "request_info"],
        "artifacts": ["zoom_link"],
        "prompt": '''Generate 5 different email pairs (incoming email + reply) with these specifications:

TOPIC: Group/Event Coordination
INTENTS: confirm, request_info (team confirms meeting AND requests information)
ARTIFACT: zoom_link (Zubair confirms and provides Zoom link)

INCOMING EMAIL GUIDELINES:
- Team member confirming meeting details AND asking for additional info
- Could be confirming time and asking for agenda, materials, etc.
- Friendly professional tone
- 400-500 characters
- Include sender name and email (university/company domain)

REPLY GUIDELINES:
- Zubair confirms meeting
- Provides requested information
- Shares Zoom link: https://us05web.zoom.us/j/5756631049?pwd=2whWm7gb5MHL5GIspFbviES0GQPuyE.1
- Mentions Meeting ID: 575 663 1049 and Passcode: 4Jp5UP
- 400-500 characters
- Must end with: "Best Regards,\\nZubair"

OUTPUT FORMAT (JSON):
{
  "email_1": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_2": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_3": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_4": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_5": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."}
}'''
    },
    {
        "num": 16,
        "topic": "Feedback & Reviews",
        "intents": ["request_feedback"],
        "artifacts": ["report"],
        "prompt": '''Generate 5 different email pairs (incoming email + reply) with these specifications:

TOPIC: Feedback & Reviews
INTENT: request_feedback (someone requests feedback on a report)
ARTIFACT: report (Zubair sends a report)

INCOMING EMAIL GUIDELINES:
- Someone asking for feedback on a report or document
- Could be colleague, professor, or team member
- Professional tone
- 400-500 characters
- Include sender name and email

REPLY GUIDELINES:
- Zubair acknowledges request
- Mentions sending report document
- Offers to discuss further
- 400-500 characters
- Must end with: "Best Regards,\\nZubair"

OUTPUT FORMAT (JSON):
{
  "email_1": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_2": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_3": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_4": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_5": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."}
}'''
    },
    {
        "num": 17,
        "topic": "Feedback & Reviews",
        "intents": ["share_feedback"],
        "artifacts": ["draft"],
        "prompt": '''Generate 5 different email pairs (incoming email + reply) with these specifications:

TOPIC: Feedback & Reviews
INTENT: share_feedback (someone shares feedback, Zubair responds with draft)
ARTIFACT: draft (Zubair sends a draft document)

INCOMING EMAIL GUIDELINES:
- Someone providing feedback on Zubair's work
- Could be professor, colleague, or reviewer
- Constructive feedback tone
- 400-500 characters
- Include sender name and email

REPLY GUIDELINES:
- Zubair thanks for feedback
- Mentions sending revised draft incorporating feedback
- Appreciates the input
- 400-500 characters
- Must end with: "Best Regards,\\nZubair"

OUTPUT FORMAT (JSON):
{
  "email_1": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_2": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_3": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_4": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_5": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."}
}'''
    },
    {
        "num": 18,
        "topic": "Feedback & Reviews",
        "intents": ["request_info"],
        "artifacts": ["github"],
        "prompt": '''Generate 5 different email pairs (incoming email + reply) with these specifications:

TOPIC: Feedback & Reviews
INTENT: request_info (someone requests information about a project)
ARTIFACT: github (Zubair shares GitHub repository)

INCOMING EMAIL GUIDELINES:
- Someone asking about a project or code repository
- Could be colleague, professor, or collaborator
- Professional tone
- 400-500 characters
- Include sender name and email

REPLY GUIDELINES:
- Zubair responds helpfully
- Shares GitHub link: https://github.com/zubairatha
- Mentions relevant project or repository
- 400-500 characters
- Must end with: "Best Regards,\\nZubair"

OUTPUT FORMAT (JSON):
{
  "email_1": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_2": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_3": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_4": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_5": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."}
}'''
    },
    {
        "num": 19,
        "topic": "Scheduling",
        "intents": ["schedule"],
        "artifacts": ["calendly"],
        "prompt": '''Generate 5 different email pairs (incoming email + reply) with these specifications:

TOPIC: Scheduling
INTENT: schedule (someone wants to schedule a meeting)
ARTIFACT: calendly (Zubair shares Calendly link)

INCOMING EMAIL GUIDELINES:
- Generic scheduling request (not specific to professor/recruiter/group)
- Could be networking, general meeting, consultation, etc.
- Professional tone
- 400-500 characters
- Include sender name and email

REPLY GUIDELINES:
- Zubair responds positively
- Shares Calendly link: https://calendly.com/za2366-columbia/30min
- Mentions availability
- 400-500 characters
- Must end with: "Best Regards,\\nZubair"

OUTPUT FORMAT (JSON):
{
  "email_1": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_2": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_3": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_4": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_5": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."}
}'''
    },
    {
        "num": 20,
        "topic": "Scheduling",
        "intents": ["reschedule"],
        "artifacts": ["zoom_link", "phone_number"],
        "prompt": '''Generate 5 different email pairs (incoming email + reply) with these specifications:

TOPIC: Scheduling
INTENT: reschedule (someone wants to reschedule a meeting)
ARTIFACTS: zoom_link, phone_number (Zubair provides both Zoom link and phone number)

INCOMING EMAIL GUIDELINES:
- Generic reschedule request
- Mentions conflict or need to change time
- Professional tone
- 400-500 characters
- Include sender name and email

REPLY GUIDELINES:
- Zubair confirms reschedule
- Shares Zoom link: https://us05web.zoom.us/j/5756631049?pwd=2whWm7gb5MHL5GIspFbviES0GQPuyE.1
- Mentions Meeting ID: 575 663 1049 and Passcode: 4Jp5UP
- Provides phone number: +16463925601 (as backup option)
- 400-500 characters
- Must end with: "Best Regards,\\nZubair"

OUTPUT FORMAT (JSON):
{
  "email_1": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_2": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_3": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_4": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_5": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."}
}'''
    },
    {
        "num": 21,
        "topic": "Scheduling",
        "intents": ["confirm"],
        "artifacts": ["phone_number"],
        "prompt": '''Generate 5 different email pairs (incoming email + reply) with these specifications:

TOPIC: Scheduling
INTENT: confirm (someone confirms a meeting and requests contact)
ARTIFACT: phone_number (Zubair shares phone number)

INCOMING EMAIL GUIDELINES:
- Someone confirming a scheduled meeting
- May request phone number for call or backup contact
- Professional tone
- 400-500 characters
- Include sender name and email

REPLY GUIDELINES:
- Zubair confirms meeting
- Shares phone number: +16463925601
- Mentions availability for the call
- 400-500 characters
- Must end with: "Best Regards,\\nZubair"

OUTPUT FORMAT (JSON):
{
  "email_1": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_2": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_3": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_4": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."},
  "email_5": {"subject": "...", "sender_email": "...", "prospect_email": "...", "reply": "..."}
}'''
    },
]

# Add all combinations to notebook
for comb in combinations:
    code = f'''# Combination {comb["num"]}: {comb["topic"]} | {", ".join(comb["intents"])} | {", ".join(comb["artifacts"]) if comb["artifacts"] else "None"}

COMBINATION_{comb["num"]}_PROMPT = """
{comb["prompt"]}
"""

process_combination(
    COMBINATION_{comb["num"]}_PROMPT,
    combination_num={comb["num"]},
    topic="{comb["topic"]}",
    intents={comb["intents"]},
    artifacts={comb["artifacts"]}
)
'''
    nb.cells.append(new_code_cell(code))
    print(f"✅ Added Combination {comb['num']}")

# Save notebook
with open('generate_email_dataset.ipynb', 'w') as f:
    nbformat.write(nb, f)

print(f"\n✅ Notebook updated with {len(combinations)} combinations (5-21)")
print(f"Total cells: {len(nb.cells)}")

