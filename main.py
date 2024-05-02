from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from config import DB_URL
from route import main_router

app = FastAPI()
app.include_router(main_router)

register_tortoise(
    app,
    db_url=DB_URL,
    modules={'models': ['models']},
    generate_schemas=True
)
