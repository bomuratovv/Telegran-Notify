from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic_types import MessageRequest
from aiogram import types
from bot import send_message_to_user, bot, dp
from utils.create_text import create_text
from config import TELEGRAM_BOT_TOKEN
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



app = FastAPI()
router = APIRouter()

origins = ["*"]

WEBHOOK_PATH = f"/bot/{TELEGRAM_BOT_TOKEN}"
WEBHOOK_URL = "https://fcfa-84-54-82-236.ngrok-free.app" + WEBHOOK_PATH

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    logger.info("Startup: Setting webhook.")
    print("Опять работа...")
    await bot.set_webhook(WEBHOOK_URL)
    


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    logger.info(f"Webhook received update: {update}")
    update = types.Update(**update)
    await dp.feed_update(bot, update)


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Shutdown: Deleting webhook and closing bot session.")
    print("Нужно больше золото...")
    await bot.delete_webhook()
    await bot.session.close()


@app.post("/send_message/")
async def send_message_users(message: MessageRequest):
    text = create_text(message.dict())
    users_id = [user.chat_id for user in message.observers_profile]
    ex_id = (
        message.executor_profile.chat_id if message.executor_profile.chat_id else None
    )
    await send_message_to_user(ex_id, text)
    for user_id in users_id:
        await send_message_to_user(user_id, text)

    return {"status": "messages sent"}



# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)