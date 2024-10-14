from typing import Annotated
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime, func, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from datetime import timezone, datetime

BASE_DIR = Path(__file__).resolve().parent
DeclarativeBase = declarative_base()

class Log(DeclarativeBase):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
    command = Column('command', String)
    created_at = Column(DateTime, server_default=func.now(tz=timezone.utc))
    answer = Column('answer', String)

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'templates')))

engine = create_engine(url = DATABASE_URL, echo=True)

DeclarativeBase.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def get_main(request: Request, breed: int | None = None):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )

@app.get("/logs/{user_id}", response_class=HTMLResponse)
async def get_user_log(request: Request, user_id, offset: int | None = 0):
    limit = 10
    result = session.query(Log.id, Log.user_id, Log.command, Log.created_at, Log.answer).filter(Log.user_id == user_id).limit(limit).offset(offset).all()
    first = result[0][0]
    is_paginator = len(result) >= limit
    return templates.TemplateResponse(
        request=request, name="user-info.html", context={"result": result, "is_paginator": is_paginator, "first": first}
    )

@app.get("/logs", response_class=HTMLResponse)
async def get_logs(request: Request, offset: int | None = 0):
    limit = 10
    result = session.query(Log.id, Log.user_id, Log.command, Log.created_at, Log.answer).limit(limit).offset(offset).all()
    times = session.query(Log.created_at).all()
    timestamps = [time[0].timestamp() for time in times]
    times_with_stamps = [(time[0], stapm) for time, stapm in zip(times, timestamps)]
    first = result[0][0]
    is_paginator = len(result) >= limit
    return templates.TemplateResponse(
        request=request, name="logs-all.html", context={"result": result, "is_paginator": is_paginator, "first": first, "times": times_with_stamps, "len": len(result)}
    )

@app.post("/logs", response_class=HTMLResponse)
async def get_filtetered_logs(request: Request,  offset: int | None = 0, time: Annotated[datetime, Form()] = None):
    limit = 10
    result = session.query(Log.id, Log.user_id, Log.command, Log.created_at, Log.answer).limit(limit).offset(offset).all()
    if time:
        result = session.query(Log.id, Log.user_id, Log.command, Log.created_at, Log.answer).filter(Log.created_at == time).limit(limit).offset(offset).all()
        time = time.timestamp()
    times = session.query(Log.created_at).all()
    timestamps = [time[0].timestamp() for time in times]
    times_with_stamps = [(time[0], stapm) for time, stapm in zip(times, timestamps)]
    first = result[0][0]
    is_paginator = len(result) >= limit
    return templates.TemplateResponse(
        request=request, name="logs.html", context={"result": result, "is_paginator": is_paginator, "first": first, "times": times_with_stamps, "time_name": time, "len": len(result)}
    )
