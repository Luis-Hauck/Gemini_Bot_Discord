import discord
import google.generativeai as genai
from dotenv import load_dotenv
from discord.ext import commands
import os

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

genai.configure(api_key=GEMINI_API_KEY)

generation_config = {
    'candidate_count': 1,
    'temperature': 0.5,
}


model = genai.GenerativeModel(model_name='gemini-1.0-pro',
                              generation_config=generation_config
                              )

chat = model.start_chat(history=[])


async def buscar_historico_canal(canal, limit=5):
    messages_list = []

    async for message in canal.history(limit=limit):
        messages_list.append(message.content)  # Only append message content
        messages_list.reverse()

    return messages_list


def ask_gemini(mensagens):
    response = chat.send_message(mensagens)

    return response.text


@bot.event
async def on_ready():
    print(f"O {bot.user.name} ficou ligado!")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    async with message.channel.typing():
        # Check if the bot is mentioned
        if message.mentions and bot.user in message.mentions:
            # Extract the message content without the mention
            content = message.content.split(maxsplit=1)[1].strip()  # Remove "@gemini "
            resposta = ask_gemini(content)
            await message.reply(resposta)

    await bot.process_commands(message)


bot.run(DISCORD_BOT_TOKEN)
