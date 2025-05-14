from fastapi import FastAPI, Query, Path, Body, Form, File, UploadFile, Response, status
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="FastAPI HTTP Methods Implementation")

# --- Data models ---
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

# In-memory “database”
items: dict[int, Item] = {}

# --- GET with path & query parameters ---
@app.get("/items/{item_id}", summary="Get an item by ID")
async def read_item(
    item_id: int = Path(..., description="The ID of the item to retrieve"),
    q: str | None = Query(None, max_length=50, description="Optional search query")
):
    item = items.get(item_id)
    return {"item_id": item_id, "item": item, "q": q}

# --- POST with JSON body ---
@app.post("/items/", status_code=status.HTTP_201_CREATED, summary="Create a new item")
async def create_item(item: Item = Body(...)):
    new_id = max(items.keys(), default=0) + 1
    items[new_id] = item
    return {"item_id": new_id, **item.dict()}

# --- PUT to replace an item ---
@app.put("/items/{item_id}", summary="Replace an existing item")
async def replace_item(item_id: int, item: Item = Body(...)):
    items[item_id] = item
    return {"item_id": item_id, **item.dict()}

# --- PATCH to partially update an item ---
class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    tax: float | None = None

@app.patch("/items/{item_id}", summary="Update fields of an existing item")
async def update_item(item_id: int, item: ItemUpdate):
    stored = items.get(item_id)
    if not stored:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    updated = stored.copy(update=item.dict(exclude_unset=True))
    items[item_id] = updated
    return {"item_id": item_id, **updated.dict()}

# --- DELETE an item ---
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an item")
async def delete_item(item_id: int):
    if item_id in items:
        del items[item_id]
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return Response(status_code=status.HTTP_404_NOT_FOUND)

# --- HEAD and OPTIONS ---
@app.head("/items/{item_id}", summary="HEAD for an item")
async def head_item(item_id: int, response: Response):
    if item_id in items:
        response.headers["X-Item-Exists"] = "true"
        return Response(status_code=status.HTTP_200_OK)
    return Response(status_code=status.HTTP_404_NOT_FOUND)

@app.options("/items/", summary="OPTIONS for items")
async def options_items(response: Response):
    response.headers["Allow"] = "GET,POST,PUT,PATCH,DELETE,HEAD,OPTIONS"
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# --- Form data ---
@app.post("/login/", summary="Submit a login form")
async def login(username: str = Form(...), password: str = Form(...)):
    # Dummy check
    if username == "admin" and password == "secret":
        return {"status": "success"}
    return Response(status_code=status.HTTP_401_UNAUTHORIZED, content="Invalid credentials")

# --- File upload ---
@app.post("/uploadfile/", summary="Upload a file")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    return {"filename": file.filename, "size": len(contents)}

# --- Run with HTTPS ---
if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=1111,
        log_level="info"
    )
