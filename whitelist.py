import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from dotenv import load_dotenv

load_dotenv()
OWNER_IDS = [int(owner_id) for owner_id in os.getenv('OWNER_IDS', '').split(',') if owner_id]
PURCHASED_FILE = 'database/purchased.json'

def load_purchased():
    try:
        with open(PURCHASED_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_purchased(server_ids):
    with open(PURCHASED_FILE, 'w') as f:
        json.dump(server_ids, f, indent=4)

class WhitelistCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="whitelist", description="Whitelist a server to use the bot (Owner Only)")
    async def whitelist(self, interaction: discord.Interaction, server_id: str):
        if interaction.user.id not in OWNER_IDS:
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
            return

        try:
            guild_id = int(server_id)
        except ValueError:
            await interaction.response.send_message("Invalid Server ID. Please enter a numeric Server ID.", ephemeral=True)
            return

        purchased_servers = load_purchased()
        if guild_id in purchased_servers:
            await interaction.response.send_message(f"Server ID {guild_id} is already whitelisted.", ephemeral=True)
            return

        purchased_servers.append(guild_id)
        save_purchased(purchased_servers)
        await interaction.response.send_message(f"Server ID {guild_id} has been whitelisted.", ephemeral=True)

    # ❌ REMOVE THIS if you had it
    # async def cog_load(self):
    #     self.bot.tree.add_command(self.whitelist)

async def setup(bot):
    await bot.add_cog(WhitelistCommand(bot))
