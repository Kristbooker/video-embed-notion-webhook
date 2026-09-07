import json

from fastapi import FastAPI, Request
from notion import notion, process_page

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Sup Notion!"}

@app.post("/webhook/notion")
async def notion_webhook(request: Request):

    # payload = await request.json()
    body = await request.body()
    print("Received webhook:")
    print(body.decode())
    signature = request.headers.get("X-Notion-Signature")

    # verify signature



    payload = json.loads(body)

    # # Normal event
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