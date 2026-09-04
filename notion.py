import os
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")
DATA_SOURCE_ID = os.getenv("DATA_SOURCE_ID")

notion = Client(auth=NOTION_TOKEN)
    
def add_video(page_id, youtube_url):
    #get all children of page 
    blocks = notion.blocks.children.list(block_id=page_id)
    
    target_column_id = None

    for block in blocks.get("results", []):
        # find column_list
        if block.get("type") == "column_list":
            #get all columns in column_list
            columns = notion.blocks.children.list(block_id=block["id"])
            
            for column in columns.get("results", []):
                #get content of each column
                col_children = notion.blocks.children.list(block_id=column["id"])
                
                for child in col_children.get("results", []):
                    #check if child is heading 2 and contain "Video"
                    if child.get("type") == "heading_2":
                        texts = child["heading_2"].get("rich_text", [])
                        plain_text = "".join([t.get("plain_text", "") for t in texts])
                        
                        if "Video" in plain_text:
                            target_column_id = column["id"]
                            break
                
                if target_column_id:
                    break
        if target_column_id:
            break

    #Append video to column
    if target_column_id:
        notion.blocks.children.append(
            block_id=target_column_id,
            children=[
                {
                    "object": "block",
                    "type": "video",
                    "video": {
                        "type": "external",
                        "external": {
                            "url": youtube_url
                        }
                    }
                }
            ]
        )
    else:
        print("column not found")
        notion.blocks.children.append(
            block_id=page_id,
            children=[
                {
                    "object": "block",
                    "type": "video",
                    "video": {
                        "type": "external",
                        "external": {
                            "url": youtube_url
                        }
                    }
                }
            ]
        )

def process_page(page):
    properties = page["properties"]
    youtube_url = properties["YouTube"]["url"]
    video_added = properties["Video Added"]["checkbox"]
    
    if youtube_url and not video_added:

        print(f"Adding video: {youtube_url}")

        add_video(
            page["id"],
            youtube_url
        )

        notion.pages.update(
            page_id=page["id"],
            properties={
                "Video Added": {
                    "checkbox": True
                }
            }
        )

        print("Video added!")
    

def main():
    response = notion.data_sources.query(
        data_source_id=DATA_SOURCE_ID
    )
    if response["results"].__len__() == 0:
        print("No results in database")
        return
        
    for page in response["results"]:
        process_page(page)
        


if __name__ == "__main__":
    main()
    