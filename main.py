from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Optional
import uuid

app = FastAPI(title="Simple Facebook Demo")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory data storage
users: Dict[int, dict] = {}
posts: Dict[int, dict] = {}
comments: Dict[int, dict] = {}
next_user_id = 1
next_post_id = 1
next_comment_id = 1

# Helper functions
def get_or_create_user(name: str) -> int:
    """Get user by name or create a new user"""
    global next_user_id
    # Check if user exists
    for user_id, user in users.items():
        if user["name"] == name:
            return user_id
    
    # Create new user
    user_id = next_user_id
    users[user_id] = {"id": user_id, "name": name}
    next_user_id += 1
    return user_id

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Redirect to posts page"""
    return templates.TemplateResponse("base.html", {"request": request, "redirect": "/posts"})

@app.get("/posts", response_class=HTMLResponse)
async def get_posts(request: Request):
    """Get all posts"""
    posts_list = list(posts.values())
    # Sort by created_at (newest first)
    posts_list.sort(key=lambda x: x["created_at"], reverse=True)

    # Add author name to each post
    for post in posts_list:
        post["author_name"] = users.get(post["author_id"], {}).get("name", "未知")

    template_name = "posts_content.html" if request.headers.get("HX-Request") else "posts.html"
    return templates.TemplateResponse(
        template_name,
        {"request": request, "posts": posts_list}
    )

@app.post("/posts/new", response_class=HTMLResponse)
async def create_post(
    request: Request,
    name: str = Form(...), 
    content: str = Form(...)
):
    """Create a new post"""
    global next_post_id
    
    if not content.strip():
        raise HTTPException(status_code=400, detail="貼文內容不能為空")
    
    # Get or create user
    user_id = get_or_create_user(name)
    
    # Create new post
    post_id = next_post_id
    new_post = {
        "id": post_id,
        "content": content,
        "created_at": datetime.now(),
        "author_id": user_id
    }
    posts[post_id] = new_post
    next_post_id += 1
    
    # Add author name for template rendering
    new_post["author_name"] = users[user_id]["name"]
    
    # Return the post HTML snippet to be inserted with HTMX
    return templates.TemplateResponse(
        "post_item.html", 
        {"request": request, "post": new_post}
    )

@app.get("/posts/{post_id}/comments", response_class=HTMLResponse)
async def get_comments(request: Request, post_id: int):
    """Get comments for a specific post"""
    if post_id not in posts:
        raise HTTPException(status_code=404, detail="找不到貼文")
    
    post_comments = [c for c in comments.values() if c["post_id"] == post_id]
    # Sort by created_at
    post_comments.sort(key=lambda x: x["created_at"])
    
    # Add author name to each comment
    for comment in post_comments:
        comment["author_name"] = users.get(comment["author_id"], {}).get("name", "未知")
    
    return templates.TemplateResponse(
        "comment_list.html", 
        {"request": request, "comments": post_comments, "post_id": post_id}
    )

@app.post("/posts/{post_id}/comments/new", response_class=HTMLResponse)
async def create_comment(
    request: Request,
    post_id: int,
    name: str = Form(...), 
    content: str = Form(...)
):
    """Create a new comment for a post"""
    global next_comment_id
    
    if post_id not in posts:
        raise HTTPException(status_code=404, detail="找不到貼文")
    
    if not content.strip():
        raise HTTPException(status_code=400, detail="留言內容不能為空")
    
    # Get or create user
    user_id = get_or_create_user(name)
    
    # Create new comment
    comment_id = next_comment_id
    new_comment = {
        "id": comment_id,
        "post_id": post_id,
        "content": content,
        "created_at": datetime.now(),
        "author_id": user_id
    }
    comments[comment_id] = new_comment
    next_comment_id += 1
    
    # Add author name for template rendering
    new_comment["author_name"] = users[user_id]["name"]
    
    # Return the comment HTML snippet to be inserted with HTMX
    return templates.TemplateResponse(
        "comment_item.html", 
        {"request": request, "comment": new_comment}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
