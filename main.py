import logging
import whisper
from aiogram import Bot, Dispatcher, executor, types
from pathlib import Path
import os
from dotenv import dotenv_values

config = dotenv_values(".env") 
logging.basicConfig(level=logging.INFO)
bot = Bot(token=config["API_TOKEN"])
dp = Dispatcher(bot)
model = whisper.load_model("base")

def translate(data):
    result = model.transcribe(data)
    return result["text"]

@dp.message_handler(content_types=[
    types.ContentType.VOICE,
    types.ContentType.AUDIO,
    types.ContentType.DOCUMENT
    ]
)
async def voice_message_handler(message: types.Message):
    if message.content_type == types.ContentType.VOICE:
        file_id = message.voice.file_id
    elif message.content_type == types.ContentType.AUDIO:
        file_id = message.audio.file_id
    elif message.content_type == types.ContentType.DOCUMENT:
        file_id = message.document.file_id
    else:
        await message.reply("Формат документа не поддерживается")
        return
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path("", f"{file_id}.tmp")
    await bot.download_file(file_path, destination=file_on_disk)
    await message.reply("Аудио получено")
    text = translate(str(file_on_disk))
    if not text:
        text = "Формат документа не поддерживается"
    if len(text) > 4000:
        for x in range(0, len(text), 4000):
            await message.answer(text[x:x+4000])
    else:
        await message.answer(text)
    os.remove(file_on_disk)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Texter - бот для перевода аудио в текст. Присылай любой вид аудио.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)