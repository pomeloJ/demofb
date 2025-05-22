from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Optional
from starlette.middleware.sessions import SessionMiddleware
import uuid

app = FastAPI(title="Simple Facebook Demo")

# Enable sessions for simple authentication
app.add_middleware(SessionMiddleware, secret_key="demo-secret-key")

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
def find_user_by_name(name: str) -> Optional[dict]:
    """Return a user dict by name if exists"""
    for user in users.values():
        if user["name"] == name:
            return user
    return None


def create_user(name: str, password: str) -> int:
    """Create a new user and return its ID"""
    global next_user_id
    user_id = next_user_id
    users[user_id] = {"id": user_id, "name": name, "password": password}
    next_user_id += 1
    return user_id


def get_current_user(request: Request) -> Optional[dict]:
    """Get currently logged-in user from the session"""
    user_id = request.session.get("user_id")
    if user_id is None:
        return None
    return users.get(user_id)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Redirect to posts page"""
    user = get_current_user(request)
    return templates.TemplateResponse(
        "base.html",
        {"request": request, "redirect": "/posts", "user": user}
    )


@app.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    """Display registration form"""
    return templates.TemplateResponse(
        "register.html",
        {"request": request}
    )


@app.post("/register", response_class=HTMLResponse)
async def register_post(request: Request, name: str = Form(...), password: str = Form(...)):
    """Handle user registration"""
    if find_user_by_name(name):
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "使用者名稱已存在"}
        )

    user_id = create_user(name, password)
    request.session["user_id"] = user_id
    return RedirectResponse(url="/posts", status_code=303)


@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    """Display login form"""
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )


@app.post("/login", response_class=HTMLResponse)
async def login_post(request: Request, name: str = Form(...), password: str = Form(...)):
    """Handle user login"""
    user = find_user_by_name(name)
    if not user or user.get("password") != password:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "登入失敗"}
        )
    request.session["user_id"] = user["id"]
    return RedirectResponse(url="/posts", status_code=303)


@app.get("/logout")
async def logout(request: Request):
    """Log the current user out"""
    request.session.pop("user_id", None)
    return RedirectResponse(url="/posts", status_code=303)

@app.get("/posts", response_class=HTMLResponse)
async def get_posts(request: Request):
    """Get all posts"""
    user = get_current_user(request)
    posts_list = list(posts.values())
    # Sort by created_at (newest first)
    posts_list.sort(key=lambda x: x["created_at"], reverse=True)

    # Add author name to each post
    for post in posts_list:
        post["author_name"] = users.get(post["author_id"], {}).get("name", "未知")

    template_name = "posts_content.html" if request.headers.get("HX-Request") else "posts.html"
    return templates.TemplateResponse(
        template_name,
        {"request": request, "posts": posts_list, "user": user}
    )

@app.post("/posts/new", response_class=HTMLResponse)
async def create_post(
    request: Request,
    content: str = Form(...)
):
    """Create a new post"""
    global next_post_id
    
    if not content.strip():
        raise HTTPException(status_code=400, detail="貼文內容不能為空")
    
    # Require logged-in user
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="請先登入")
    user_id = user["id"]
    
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
    user = get_current_user(request)
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
        {"request": request, "comments": post_comments, "post_id": post_id, "user": user}
    )

@app.post("/posts/{post_id}/comments/new", response_class=HTMLResponse)
async def create_comment(
    request: Request,
    post_id: int,
    content: str = Form(...)
):
    """Create a new comment for a post"""
    global next_comment_id
    
    if post_id not in posts:
        raise HTTPException(status_code=404, detail="找不到貼文")
    
    if not content.strip():
        raise HTTPException(status_code=400, detail="留言內容不能為空")
    
    # Require logged-in user
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="請先登入")
    user_id = user["id"]
    
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
