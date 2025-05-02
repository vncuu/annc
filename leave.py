import discord
from discord.ext import commands
import json
import os

PURCHASED_FILE = 'database/purchased.json'

def load_purchased():
    """Load the purchased server IDs and ensure they are integers."""
    try:
        with open(PURCHASED_FILE, 'r') as f:
            data = json.load(f)
            # Log the data being loaded from the file
            print(f"[DEBUG] Loaded purchased server IDs: {data}")
            return [int(server_id) for server_id in data]
    except (FileNotFoundError, json.JSONDecodeError):
        print("[ERROR] Failed to load purchased.json. Returning an empty list.")
        return []

class LeaveCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        # Reload purchased list from file and check if the server is whitelisted
        purchased_servers = load_purchased()
        print(f"[DEBUG] Checking if server {guild.id} ({guild.name}) is in purchased list...")

        if guild.id in purchased_servers:
            print(f"✅ Guild {guild.name} ({guild.id}) is whitelisted. Staying in the server.")
        else:
            print(f"❌ Guild {guild.name} ({guild.id}) is NOT whitelisted. Leaving the server.")
            await guild.leave()

async def setup(bot):
    await bot.add_cog(LeaveCog(bot))
