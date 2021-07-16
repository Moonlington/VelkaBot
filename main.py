import yaml
import os
import logging

import discord
from discord.ext.commands import AutoShardedBot


class Velka(AutoShardedBot):
    def __init__(self):
        with open("config.yml") as config:
            self.config = yaml.safe_load(config)

        super().__init__(command_prefix=self.config["prefix"])

        self.logger = logging.getLogger("Velka")
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler('VelkaLog.log')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        self.logger.addHandler(handler)

        self.logChannel = None
        self.mailChannel = None

    def load_cogs(self):
        for file in os.listdir("cogs"):
            filename, extension = os.path.splitext(file)
            if extension == ".py":
                try:
                    self.logger.info("Attempting to load cog: %s", filename)
                    self.load_extension(f"cogs.{filename}")
                except Exception as e:
                    self.logger.error("Failed to load cog: %s", filename)
                    self.logger.exception(e)
        self.logger.info("loaded cogs")

    async def on_ready(self):
        self.load_cogs()
        self.logChannel = self.get_channel(self.config["logChannel"]) or await self.fetch_channel(
            self.config["logChannel"])
        self.mailChannel = self.get_channel(self.config["mailChannel"]) or await self.fetch_channel(
            self.config["mailChannel"])
        customMsg = discord.Game(
            "DMs will be sent to the Mod Team!")
        await self.change_presence(activity=customMsg)
        self.logger.info("Velka loaded!")


if __name__ == "__main__":
    bot = Velka()
    bot.logger.info("Launching Velka...")
    bot.run(bot.config['token'])
