# app/main.py
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")

# Frontend routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    todos = crud.get_todos(db)
    return templates.TemplateResponse("index.html", {"request": request, "todos": todos})

@app.post("/add", response_class=RedirectResponse)
async def add_todo(request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    todo = schemas.TodoCreate(
        title=form_data["title"],
        description=form_data.get("description", ""),
        completed=False
    )
    crud.create_todo(db, todo)
    return RedirectResponse(url="/", status_code=303)

@app.get("/complete/{todo_id}", response_class=RedirectResponse)
async def complete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = crud.get_todo(db, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    update_data = {"completed": not todo.completed}
    if todo.title:
        update_data["title"] = todo.title
    if todo.description:
        update_data["description"] = todo.description
    crud.update_todo(db, todo_id, schemas.TodoBase(**update_data))
    return RedirectResponse(url="/", status_code=303)

@app.get("/delete/{todo_id}", response_class=RedirectResponse)
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    crud.delete_todo(db, todo_id)
    return RedirectResponse(url="/", status_code=303)

# API routes (optional)
@app.post("/api/todos/", response_model=schemas.Todo)
def create_todo_api(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    return crud.create_todo(db, todo)

@app.get("/api/todos/", response_model=list[schemas.Todo])
def read_todos_api(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    todos = crud.get_todos(db, skip=skip, limit=limit)
    return todos

@app.put("/api/todos/{todo_id}", response_model=schemas.Todo)
def update_todo_api(todo_id: int, todo: schemas.TodoBase, db: Session = Depends(get_db)):
    db_todo = crud.update_todo(db, todo_id, todo)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo

@app.delete("/api/todos/{todo_id}")
def delete_todo_api(todo_id: int, db: Session = Depends(get_db)):
    db_todo = crud.delete_todo(db, todo_id)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted successfully"}