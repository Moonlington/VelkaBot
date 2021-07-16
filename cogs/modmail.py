import discord
from discord.ext import commands
import os.path
import json

from utils import checks


class ModMailCog(commands.Cog):
    """ModMailCog"""

    def __init__(self, bot):
        self.bot = bot
        with open("mailblacklist.json", "r") as f:
            self.blacklistedIDs = json.load(f)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if not isinstance(message.channel, discord.DMChannel):
            return

        if message.author.id in self.blacklistedIDs:
            await message.channel.send("You are blacklisted from sending mail to the moderation team.\nYour message has not been sent.")
            return

        em = discord.Embed(
            description=f"{message.clean_content}\n\n**Message was sent by {message.author.mention}**",
            color=0xddaa35)
        em.set_author(
            name=f"Mail from {message.author.name}",
            icon_url=message.author.avatar_url_as())
        em.timestamp = message.created_at

        if len(message.attachments) > 0:
            em.set_image(url=message.attachments[0].url)

        await self.bot.mailChannel.send(embed=em)
        await message.channel.send("Your message was successfully sent to the moderation team!\nA member of the team will follow up with you separately if there's any more info to share.")

    @commands.command()
    @commands.check(checks.is_mod)
    async def blacklist(self, ctx, *, member: discord.Member):
        if member.id in self.blacklistedIDs:
            await ctx.send(f"{member.display_name} is already blacklisted")
            return
        self.blacklistedIDs.append(member.id)
        with open("mailblacklist.json", "w") as f:
            json.dump(self.blacklistedIDs, f)
        await ctx.send(f"{member.display_name} is now blacklisted from sending modmail")

    @commands.command()
    @commands.check(checks.is_mod)
    async def unblacklist(self, ctx, *, member: discord.Member):
        if member.id not in self.blacklistedIDs:
            await ctx.send(f"{member.display_name} is not blacklisted")
            return
        self.blacklistedIDs.remove(member.id)
        with open("mailblacklist.json", "w") as f:
            json.dump(self.blacklistedIDs, f)
        await ctx.send(f"{member.display_name} is now no longer blacklisted")


def setup(bot):
    if not os.path.isfile("mailblacklist.json"):
        with open("mailblacklist.json", "w") as f:
            json.dump([], f)
    bot.add_cog(ModMailCog(bot))
