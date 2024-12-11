from fastapi import FastAPI, Response, Cookie, Request, Form, HTTPException, status
import sqlite3
import uvicorn
from fastapi.params import Depends
from fastapi.templating import Jinja2Templates
from data import db_session
from data.users import User
from data.news import News
from data.auth import create_access_token, get_token, get_user_from_token

db_session.global_init("db/users.db")
templates = Jinja2Templates(directory="templates")
app = FastAPI()


@app.get("/cookies")
async def root(cookie = Cookie()):
    return {"cookie": cookie}


@app.get("/registration")
async def getreg(request: Request):
    return templates.TemplateResponse("registration.html", {"request": request})

@app.post("/registration")
async def postreg(response: Response, email: str = Form(), password: str = Form()):
    db_sess = db_session.create_session()
    data = db_sess.query(User).filter(User.email == email).first()
    if not data:
        user = User(
            email=email
        )
        user.set_password(password)
        db_sess.add(user)
        db_sess.commit()
        db_sess.close()
        token = create_access_token({"email": email})
        response.set_cookie(key="access_token", value=token, httponly=True)
        return {"status": "success"}
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='Пользователь уже существует')

@app.get("/")
async def getlog(request: Request, response: Response):
    try:
        if a:= get_token(request):
            if get_user_from_token(a):
                return {"status": "success"}
    except Exception:
        pass
    return templates.TemplateResponse("log_in.html", {"request": request})
@app.post("/")
async def postlog(response: Response, request: Request, email: str = Form(), password: str = Form()):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == email).first()
    db_sess.close()
    try:
        if a:= get_token(request):
            if get_user_from_token(a):
                return {"status": "success"}
    except Exception:
        pass
    if user.check_password(password):
        token = create_access_token({"email": email})
        response.set_cookie(key="access_token", value=token, httponly=True)
        return {"status": "success"}
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='неверный логин или пароль')

@app.get("/me")
async def getme(user_data: User = Depends(get_user_from_token)):
    return user_data.__repr__()


@app.post("/news")
async  def new_news(user_data: User = Depends(get_user_from_token), title: str =Form(), content: str =Form()):
    db_sess = db_session.create_session()
    new = News(
        title=title,
        content=content,
        user_id=user_data.id
    )
    db_sess.add(new)
    db_sess.commit()
    db_sess.close()
    return {"status: ": "success"}


@app.get("/news")
async def send_news(user_data: User = Depends(get_user_from_token), n=0):
    db_sess = db_session.create_session()
    if n:
        news = db_sess.query(News)
        db_sess.close()
        return news
    news = db_sess.query(News).all()
    db_sess.close()
    return news

@app.delete("/news{id}")
async def rem_news(id : int, user_data: User = Depends(get_user_from_token)):
    db_sess = db_session.create_session()
    db_sess.query(News).filter(News.user_id == user_data.id and News.id == id).delete()
    db_sess.commit()
    db_sess.close()
    return {"status": "success"}



if __name__ == "__main__":
    uvicorn.run(app, port=8000)