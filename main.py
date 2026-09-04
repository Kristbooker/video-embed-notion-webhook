from fastapi import FastAPI, Request
from notion import notion, process_page

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/webhook/notion")
async def notion_webhook(request: Request):

    payload = await request.json()

    print("Received webhook:")
    print(payload)

    # Verification request
    if "verification_token" in payload:
        print("Verification token:")
        print(payload["verification_token"])

        return {"ok": True}

    # Normal event
    event_type = payload.get("type")

    if event_type == "page.properties_updated":

        page_id = payload["entity"]["id"]

        print(f"Page updated: {page_id}")

        page = notion.pages.retrieve(
            page_id=page_id
        )

        process_page(page)

    return {"ok": True}