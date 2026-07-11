import json
import os

import streamlit as st

from workflow import process_request

LOG_FILE = "request_log.json"
REQUEST_TYPES = [
    "Complaint",
    "General Enquiry",
    "Service Request",
    "Escalation / Urgent"
]
URGENCY_LEVELS = ["Low", "Medium", "High", "Critical"]

st.set_page_config(
    page_title="AI Request Processing Workflow",
    page_icon="🤖",
    layout="wide"
)

st.markdown(
    """
    <style>
    .reportview-container .main .block-container {
        padding-top: 1.5rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }
    .stButton>button {
        color: white;
        background-color: #0a4c78;
        border: none;
        border-radius: 8px;
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 8px;
    }
    .streamlit-expanderHeader {
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Helper functions
# ----------------------------

def load_logs():
    if not os.path.exists(LOG_FILE):
        return []

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def metrics(logs):
    total = len(logs)
    type_counts = {
        request_type: len(
            [item for item in logs if item.get("request_type") == request_type]
        )
        for request_type in REQUEST_TYPES
    }
    urgency_counts = {
        urgency: len(
            [item for item in logs if item.get("urgency") == urgency]
        )
        for urgency in URGENCY_LEVELS
    }
    return total, type_counts, urgency_counts


def parse_uploaded_request(content):
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    if len(lines) >= 2:
        return lines[0], "\n".join(lines[1:])
    if len(lines) == 1:
        return "Uploaded Request", lines[0]
    return "Uploaded Request", content.strip()


logs = load_logs()

total, type_counts, urgency_counts = metrics(logs)

st.title("🤖 AI Incoming Request Processing Workflow")

st.caption(
    "AI-powered classification, routing, escalation, and response workflow for incoming requests."
)

st.divider()

columns = st.columns([1, 1, 1, 1, 1])
columns[0].metric("Total Requests", total)
for idx, request_type in enumerate(REQUEST_TYPES, start=1):
    columns[idx].metric(request_type, type_counts.get(request_type, 0))

st.divider()

st.subheader("Urgency distribution")
st.bar_chart(urgency_counts)

with st.expander("Workflow overview"):
    st.write(
        """
        1. Enter a customer request manually or upload a text file.
        2. AI determines the request type and urgency.
        3. The system generates a branch-specific remediation plan.
        4. The request is logged and the draft response is shown.
        """
    )

st.divider()

# -------------------------------------------------
# Request tabs
# -------------------------------------------------

tab1, tab2 = st.tabs(["📝 Manual Request", "📂 Upload Request"])
result = None

with tab1:
    left, right = st.columns([1.3, 0.9])

    with left:
        st.subheader("Manual request entry")
        with st.form("request_form"):
            customer = st.text_input("Customer Name", placeholder="e.g. Sumit Kumar")
            email = st.text_input("Customer Email", placeholder="example@company.com")
            subject = st.text_input("Request Subject", placeholder="Account access issue")
            description = st.text_area(
                "Request Description",
                height=240,
                placeholder="Describe the customer's issue, question or request in detail..."
            )
            submit = st.form_submit_button("🚀 Process Request")

    with right:
        st.subheader("Branch examples")
        st.info(
            """
- Complaint: urgent account, billing or service issues
- General Enquiry: product, policy or information requests
- Service Request: change, assistance or provisioning
- Escalation / Urgent: critical, supervisor review needed
"""
        )

        st.subheader("Expected outcome")
        st.success(
            """
Complaint -> Acknowledge, escalate, follow-up
General Enquiry -> Answer, route, close
Service Request -> Confirm, assign, schedule
Escalation / Urgent -> Alert supervisor, human review, pause auto-resolution
"""
        )

with tab2:
    st.subheader("Upload request from TXT file")
    uploaded_file = st.file_uploader("Choose a TXT file", type=["txt"])
    file_subject = ""
    file_description = ""

    if uploaded_file is not None:
        content = uploaded_file.read().decode("utf-8", errors="replace")
        file_subject, file_description = parse_uploaded_request(content)
        st.write("**Parsed request subject:**", file_subject)
        st.text_area("File content preview", value=content, height=240, disabled=True)
        if st.button("🚀 Process uploaded request"):
            if not file_description.strip():
                st.error("Uploaded file does not contain request text.")
            else:
                with st.spinner("AI is processing uploaded request..."):
                    result = process_request(
                        "Uploaded request",
                        "",
                        file_subject,
                        file_description,
                    )

# -------------------------------------------------
# Process result
# -------------------------------------------------

if 'submit' in locals() and submit:
    if not subject.strip() or not description.strip():
        st.error("Subject and Description are required.")
    else:
        with st.spinner("AI is processing request..."):
            result = process_request(
                customer.strip(),
                email.strip(),
                subject.strip(),
                description.strip(),
            )

if result is not None:
    st.divider()
    st.header("Processing result")
    left, right = st.columns([1, 1])

    with left:
        st.subheader("Classification")
        st.metric("Request Type", result["request_type"])
        st.metric("Urgency", result["urgency"])
        st.write(f"**Assigned Team:** {result['assigned_team']}")
        st.write(f"**Follow-up:** {result['follow_up']}")

    with right:
        st.subheader("Executed actions")
        for action in result["actions"]:
            st.checkbox(action, value=True, disabled=True)

    st.divider()
    st.subheader("Draft customer response")
    st.info(result["response"])

# -------------------------------------------------
# History
# -------------------------------------------------

st.divider()
st.header("Recent processed requests")
logs = load_logs()

if not logs:
    st.info("No requests processed yet.")
else:
    recent_logs = list(reversed(logs[-10:]))
    for item in recent_logs:
        with st.expander(f"{item.get('request_type', '')} | {item.get('urgency', '')} | {item.get('processed_at', '')}"):
            st.write(f"**Customer:** {item.get('customer_name', 'N/A')}")
            st.write(f"**Subject:** {item.get('subject', 'N/A')}")
            st.write(f"**Assigned Team:** {item.get('assigned_team', 'N/A')}")
            st.write(f"**Follow-up:** {item.get('follow_up', 'N/A')}")
            st.write("**Response:**")
            st.write(item.get("response", ""))

    st.divider()
    st.subheader("Recent activity")
    table_data = [
        {
            "Processed At": item.get("processed_at", ""),
            "Type": item.get("request_type", ""),
            "Urgency": item.get("urgency", ""),
            "Team": item.get("assigned_team", ""),
            "Follow-up": item.get("follow_up", ""),
            "Subject": item.get("subject", "")[:45],
        }
        for item in recent_logs
    ]
    st.table(table_data)
