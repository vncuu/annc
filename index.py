import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

# Set up intents
intents = discord.Intents.default()
intents.guilds = True  # Required for slash commands
intents.message_content = True # Needed for on_message and possibly other events in cogs

# Create the bot instance
bot = commands.Bot(command_prefix='g', intents=intents)

async def load_extensions():
    # Load command cogs from ./cmds
    for filename in os.listdir('./cmds'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cmds.{filename[:-3]}')
                print(f"✅ Loaded command: cmds.{filename}")
            except Exception as e:
                print(f"❌ Failed to load cmds.{filename}: {e}")

    # Load event cogs from ./events
    for filename in os.listdir('./events'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'events.{filename[:-3]}')
                print(f"✅ Loaded event: events.{filename}")
            except Exception as e:
                print(f"❌ Failed to load events.{filename}: {e}")

@bot.event
async def on_ready():
    print(f"🤖 Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Streaming(
        name="47 Shards | govern.vnc",
        url="https://www.twitch.tv/itzvncuu"
    ))

    # Sync slash commands globally
    try:
        synced = await bot.tree.sync()
        print(f"🌐 Synced {len(synced)} global slash command(s).")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")

# Main entry point
async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

# Run the bot
asyncio.run(main())
