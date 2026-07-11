import json
import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in .env")

client = OpenAI(api_key=OPENAI_API_KEY)


def classify_request(subject, description):
    prompt = f"""
You are an AI Operations Assistant.

Classify the following customer request. Choose the best match for request type and urgency.

Request Types:
- Complaint
- General Enquiry
- Service Request
- Escalation / Urgent

Urgency:
- Low
- Medium
- High
- Critical

Provide ONLY valid JSON with these two keys:
{{
  "request_type":"...",
  "urgency":"..."
}}

Subject:
{subject}

Description:
{description}
"""

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)


def generate_response(request_type, urgency, subject, description):
    prompt = f"""
You are an AI Operations Assistant.

A customer request has been classified. Generate a branch-specific remediation plan and a draft customer response.

Request Type: {request_type}
Urgency: {urgency}
Subject: {subject}
Description: {description}

Return ONLY JSON with these keys:
- assigned_team
- follow_up
- actions
- response

Example:
{{
  "assigned_team": "Senior Support",
  "follow_up": "2 Hours",
  "actions": [
    "Acknowledgement Generated",
    "Escalated to Senior Support",
    "Follow-up Reminder Created"
  ],
  "response": "Dear Customer..."
}}

If the request is Escalation / Urgent or urgency is Critical, include a supervisor alert or human-review step in actions.
"""

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)
