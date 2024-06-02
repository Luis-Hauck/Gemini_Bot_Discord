import discord
import google.generativeai as genai
from discord.ext import commands


DISCORD_BOT_TOKEN = "SUA_CHAVE"
GEMINI_API_KEY = "SUA_CHAVE"

intents = discord.Intents.default()
intents.messages = True
bot = discord.Client(intents=intents)

genai.configure(api_key=GEMINI_API_KEY)

generation_config = {
    'candidate_count': 1,
    'temperature': 0.5,
    'max_output_tokens': 150,
}

model = genai.GenerativeModel(model_name='gemini-1.0-pro',
                              generation_config=generation_config)

chat = model.start_chat(history=[])

responded_messages = set()

async def buscar_historico_canal(canal, limit=5):
    messages_list = []
    async for message in canal.history(limit=limit):
        if message.author != bot.user:  # Exclude bot's own messages
            messages_list.append(message)
    messages_list.reverse()  # Ensure chronological order
    return messages_list

def ask_gemini(mensagens):
    response = chat.send_message(mensagens)
    return response.text

@bot.event
async def on_ready():
    print(f"O {bot.user.name} está ligado!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.mentions and bot.user in message.mentions:
        async with message.channel.typing():
            historico = await buscar_historico_canal(message.channel, limit=5)
            for msg in historico:
                if msg.id not in responded_messages:
                    msg_content = msg.content
                    for mention in msg.mentions:
                        if mention == bot.user:
                            msg_content = msg_content.replace(f"<@{mention.id}>", "").strip()
                    if msg_content:  # Only send non-empty messages
                        resposta = ask_gemini(msg_content)
                        await message.reply(resposta)
                        responded_messages.add(msg.id)  # Mark this message as responded


bot.run(DISCORD_BOT_TOKEN)
