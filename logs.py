# cmds/logs.py

import discord
from discord.ext import commands
import json
import os

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Ensure the database directory exists
        if not os.path.exists('database'):
            os.makedirs('database')

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.__class__.__name__} cog loaded.')
        # It's generally better to sync application commands in the main bot file's on_ready event
        # await self.bot.tree.sync()

    @commands.hybrid_command(name='log_setup', description='Sets up the current channel for server logs.')
    async def log_setup(self, ctx: commands.Context):
        guild_id = str(ctx.guild.id)
        channel_id = str(ctx.channel.id)

        log_data = {}
        if os.path.exists('database/logs.json'):
            with open('database/logs.json', 'r') as f:
                try:
                    log_data = json.load(f)
                except json.JSONDecodeError:
                    log_data = {}

        log_data[guild_id] = channel_id

        with open('database/logs.json', 'w') as f:
            json.dump(log_data, f, indent=4)

        await ctx.send(f'Log channel for this server has been set to <#{channel_id}>.', ephemeral=True)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        guild_id = str(channel.guild.id)
        channel_id = str(channel.id)
        channel_name = channel.name

        if os.path.exists('database/logs.json'):
            with open('database/logs.json', 'r') as f:
                try:
                    log_data = json.load(f)
                    if guild_id in log_data:
                        log_channel_id = log_data[guild_id]
                        log_channel = self.bot.get_channel(int(log_channel_id))
                        if log_channel:
                            embed = discord.Embed(title="Channel Created", color=0xc9a0ec)
                            embed.add_field(name="Name", value=channel_name, inline=False)
                            embed.add_field(name="ID", value=channel_id, inline=False)
                            embed.timestamp = discord.utils.utcnow()
                            await log_channel.send(embed=embed)
                except (json.JSONDecodeError, FileNotFoundError):
                    pass # Handle potential errors when reading the log file

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        guild_id = str(channel.guild.id)
        channel_id = str(channel.id)
        channel_name = channel.name

        if os.path.exists('database/logs.json'):
            with open('database/logs.json', 'r') as f:
                try:
                    log_data = json.load(f)
                    if guild_id in log_data:
                        log_channel_id = log_data[guild_id]
                        log_channel = self.bot.get_channel(int(log_channel_id))
                        if log_channel:
                            embed = discord.Embed(title="Channel Deleted", color=0xc9a0ec)
                            embed.add_field(name="Name", value=channel_name, inline=False)
                            embed.add_field(name="ID", value=channel_id, inline=False)
                            embed.timestamp = discord.utils.utcnow()
                            await log_channel.send(embed=embed)
                except (json.JSONDecodeError, FileNotFoundError):
                    pass # Handle potential errors when reading the log file

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        guild_id = str(before.guild.id)

        if os.path.exists('database/logs.json'):
            with open('database/logs.json', 'r') as f:
                try:
                    log_data = json.load(f)
                    if guild_id in log_data:
                        log_channel_id = log_data[guild_id]
                        log_channel = self.bot.get_channel(int(log_channel_id))
                        if log_channel:
                            embed = discord.Embed(title="Channel Updated", color=0xc9a0ec)
                            if before.name != after.name:
                                embed.add_field(name="Name Changed", value=f"Before: {before.name}\nAfter: {after.name}", inline=False)
                            # Add more checks for other channel updates as needed (e.g., topic, permissions)
                            if embed.fields:
                                embed.timestamp = discord.utils.utcnow()
                                await log_channel.send(embed=embed)
                except (json.JSONDecodeError, FileNotFoundError):
                    pass # Handle potential errors when reading the log file

async def setup(bot):
    await bot.add_cog(Logging(bot))