from http.client import HTTPException
import os
import json
import hmac
import hashlib

from fastapi import FastAPI, Request
from notion import notion, process_page

app = FastAPI()

NOTION_WEBHOOK_VERIFICATION_TOKEN = os.getenv(
    "NOTION_WEBHOOK_VERIFICATION_TOKEN"
)

@app.get("/")
async def root():
    return {"message": "Sup Notion!"}

@app.post("/webhook/notion")
async def notion_webhook(request: Request):

    # payload = await request.json()
    body = await request.body()
    

    # verify signature
    signature = request.headers.get("X-Notion-Signature")

    print("Received webhook")
    # print(body.decode())

    # check signature exists
    if not signature:
        print("Missing X-Notion-Signature")
        raise HTTPException(
            status_code=401,
            detail="Missing signature"
        )

    # check verification token exists
    if not NOTION_WEBHOOK_VERIFICATION_TOKEN:
        print("Missing NOTION_WEBHOOK_VERIFICATION_TOKEN")
        raise HTTPException(
            status_code=500,
            detail="Webhook verification token is not configured"
        )

    # calculate expected signature
    hmac_obj = hmac.new(
        NOTION_WEBHOOK_VERIFICATION_TOKEN.encode("utf-8"),
        body,
        hashlib.sha256
    )

    expected_signature = "sha256=" + hmac_obj.hexdigest()
    # compare signatures safely
    if not hmac.compare_digest(
        expected_signature,
        signature
    ):
        print("Invalid Notion signature")

        raise HTTPException(
            status_code=401,
            detail="Invalid signature"
        )

    print("Signature verified!")

    # parse json
    payload = json.loads(body)

    # normal event
    event_type = payload.get("type")
    print(f"Event type: {event_type}")


    if event_type == "page.properties_updated":

        page_id = payload["entity"]["id"]

        print(f"Page ID: {page_id}")

        page = notion.pages.retrieve(
            page_id=page_id
        )

        process_page(page)

    return {"ok": True}