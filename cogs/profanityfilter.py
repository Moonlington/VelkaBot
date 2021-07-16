import discord
from discord.ext import commands
from cachetools import LRUCache
from threading import Lock
from utils import checks
import json

from better_profanity import profanity


class ProfanityFilterCog(commands.Cog):
    """ProfanityFilterCog"""

    def __init__(self, bot):
        self.bot = bot
        with open("censor_words.json", "r") as f:
            self.censor_words = json.load(f)
        profanity.load_censor_words(self.censor_words)
        self.lock = Lock()
        self.cache = LRUCache(maxsize=128)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if isinstance(message.channel, discord.DMChannel):
            return

        if not profanity.contains_profanity(message.content):
            return

        em = discord.Embed(
            description=f"{message.clean_content}\n\n**Profanity detected!** {message.author.mention} in {message.channel.mention}\n[Jump!]({message.jump_url})",
            color=0xE71D3B,
        )
        em.set_author(
            name=f"Profanity from {message.author.name}",
            icon_url=message.author.avatar_url_as(),
        )
        em.timestamp = message.created_at

        logmsg = await self.bot.logChannel.send(embed=em)
        with self.lock:
            self.cache[message.id] = logmsg

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if after.author.bot:
            return

        if before.clean_content == after.clean_content:
            return

        if isinstance(after.channel, discord.DMChannel):
            return

        if (
            not profanity.contains_profanity(after.content)
            and self.cache.get(after.id) is None
        ):
            return

        em = discord.Embed(
            description=f"**From:** {before.clean_content}\n**To:** {after.clean_content}\n\n**Profanity detected!** {after.author.mention} in {after.channel.mention}\n[Jump!]({after.jump_url})",
            color=0xE71D3B,
        )
        em.set_author(
            name=f"Edited profanity from {after.author.name}",
            icon_url=after.author.avatar_url_as(),
        )

        em.timestamp = after.created_at
        with self.lock:
            if self.cache.get(after.id) is None:
                logmsg = await self.bot.logChannel.send(embed=em)
                self.cache[after.id] = logmsg
            else:
                await self.cache.get(after.id).edit(embed=em)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return

        if isinstance(message.channel, discord.DMChannel):
            return

        if (
            not profanity.contains_profanity(message.content)
            and self.cache.get(message.id) is None
        ):
            return

        em = discord.Embed(
            description=f"{message.clean_content}\n**This message was deleted!**\n\n**Profanity detected!** {message.author.mention} in {message.channel.mention}\n[Jump!]({message.jump_url})",
            color=0xE71D3B,
        )
        em.set_author(
            name=f"Profanity from {message.author.name}",
            icon_url=message.author.avatar_url_as(),
        )

        em.timestamp = message.created_at

        with self.lock:
            if self.cache.get(message.id) is None:
                logmsg = await self.bot.logChannel.send(embed=em)
                self.cache[message.id] = logmsg
            else:
                await self.cache.get(message.id).edit(embed=em)

    @commands.command()
    @commands.check(checks.is_mod)
    async def filter(self, ctx, *, argument: str):
        if argument.lower() in self.censor_words:
            await ctx.send(f"{argument.lower()} is already being filtered")
            return
        self.censor_words.append(argument.lower())
        with open("censor_words.json", "w") as f:
            json.dump(self.censor_words, f)
        profanity.load_censor_words(self.censor_words)
        await ctx.send(f"{argument.lower()} is now being filtered")

    @commands.command()
    @commands.check(checks.is_mod)
    async def unfilter(self, ctx, *, argument: str):
        if argument.lower() not in self.censor_words:
            await ctx.send(f"{argument.lower()} is not being filtered")
            return
        self.censor_words.remove(argument.lower())
        with open("censor_words.json", "w") as f:
            json.dump(self.censor_words, f)
        profanity.load_censor_words(self.censor_words)
        await ctx.send(f"{argument.lower()} is now no longer being filtered")

    @commands.command()
    @commands.check(checks.is_mod)
    async def filterlist(self, ctx):
        await ctx.send(
            "Words that are currently being filtered:\n`"
            + "`\n`".join(self.censor_words)
            + "`"
        )


def setup(bot):
    bot.add_cog(ProfanityFilterCog(bot))
