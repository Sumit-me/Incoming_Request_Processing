from ai import classify_request, generate_response
from logger import save_log


def process_request(customer_name, email, subject, description):

    # Step 1 - Classify Request
    classification = classify_request(subject, description)

    request_type = classification["request_type"]
    urgency = classification["urgency"]

    # Step 2 - Generate Branch Specific Response
    remediation = generate_response(
        request_type=request_type,
        urgency=urgency,
        subject=subject,
        description=description
    )

    result = {
        "customer_name": customer_name,
        "email": email,
        "subject": subject,
        "description": description,
        "request_type": request_type,
        "urgency": urgency,
        "actions": remediation["actions"],
        "assigned_team": remediation["assigned_team"],
        "follow_up": remediation["follow_up"],
        "response": remediation["response"]
    }

    # Step 3 - Save Log
    save_log(result)

    return result