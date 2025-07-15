import base64, email, time, pathlib
from email.message import EmailMessage
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from rag import is_relevant, answer
from rag import chat


#magic
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send",
]

def get_creds():
    token_file = pathlib.Path("token.json")
    creds = None

    if token_file.exists():
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port = 0)   #opens browser = once
        token_file.write_text(creds.to_json())
    return creds

service = build("gmail", "v1", credentials = get_creds(), cache_discovery = False)



def list_unread():
    resp = service.users().messages().list(userId = "me", q = "is:unread").execute()
    return resp.get("messages", [])


def get_msg(msg_id):
    return service.users().messages().get(userId = "me", id = msg_id, format = "full").execute()


def mark_read(msg_id):
    service.users().messages().modify(userId = "me", id = msg_id, body = {"removeLabelIds": ["UNREAD"]}).execute()


def extract_plain(payload):
    for part in payload.get("parts", []):
        if part.get("mimeType") == "text/plain":
            data = part["body"]["data"]
            return base64.urlsafe_b64decode(data).decode(errors="ignore")
    return payload.get("snippet", "")


def save_draft_reply(thread_id, to_addr, subject, body_text):
    msg = EmailMessage()
    msg["To"] = to_addr
    msg["Subject"] = "Re: " + subject
    msg.set_content(body_text)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().drafts().create(userId = "me", body = {"message": {"raw": raw, "threadId": thread_id}}).execute()


def process_last_email():
    """
    Fetches the last unread email, generates a draft reply, and stops.
    """
    print("Checking for unread emails...")
    unread_metas = list_unread()

    if not unread_metas:
        print("No unread emails found. Exiting.")
        return

    # Fetch all unread messages to find the most recent one
    print(f"Found {len(unread_metas)} unread email(s). Identifying the latest...")
    all_msgs = [get_msg(meta['id']) for meta in unread_metas]

    # Sort messages by internalDate (timestamp) to find the newest
    latest_msg = sorted(all_msgs, key = lambda m: int(m['internalDate']), reverse = True)[0]

    hdrs = {h["name"]: h["value"] for h in latest_msg["payload"]["headers"]}
    frm = hdrs.get("From", "")
    subj = hdrs.get("Subject", "(no subject)")
    body = extract_plain(latest_msg["payload"])

    print(f"processing most recent email from: {frm} | Subject: {subj}")

    question = f"{subj}\n\n{body}"

    #whether to use pdf or plain llm chat
    if is_relevant(question):
        reply = answer(question)
    else:
        print("...pdf not relevant. using plain llm chat.")
        reply = chat(question)

    save_draft_reply(latest_msg["threadId"], frm, subj, reply)
    # Mark the specific message we processed as read
    mark_read(latest_msg["id"])
    print(f"\ndraft saved '{frm}' & Script finished.")



if __name__ == "__main__":
    process_last_email()