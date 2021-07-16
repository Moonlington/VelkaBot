import os

import discord
from discord.ext import commands

from utils import checks


class CoreCog(commands.Cog):
    """CoreCog"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(checks.is_owner)
    async def reload(self, ctx):
        try:
            for file in os.listdir("cogs"):
                if file.endswith(".py"):
                    name = file[:-3]
                    try:
                        self.bot.logger.info(
                            "Attempting to reload cog: %s", name)
                        self.bot.reload_extension(f"cogs.{name}")
                    except discord.ext.commands.ExtensionNotLoaded:  # if its a new cog thats not loaded
                        self.bot.load_extension(f"cogs.{name}")
                        self.bot.logger.info(
                            "Attempting to load cog: %s", name)

        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            self.bot.logger.error("Failed to reload cogs!")
            self.bot.logger.exception(e)
        else:
            await ctx.send('**Update done :ok_hand:**')


def setup(bot):
    bot.add_cog(CoreCog(bot))
