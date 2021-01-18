import logging

from ..tools import Cog

from discord.ext import commands
import discord

log = logging.getLogger(__name__)


class Highlighter(Cog):
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if self.bot.location == 'dev' or message.guild is None:
            return
        if message.guild.id in self.bot.config.listenServers and message.author.id != self.bot.owner.id and not message.author.bot:
            if any(each.lower() in message.content.lower() for each in self.bot.config.listens):
                tosend = (f"highlight: {message.author.mention} ({message.author})"
                          f"in {message.channel.mention}({message.channel})"
                          f"\n{message.jump_url}\n\n{message.content}")
                if len(tosend) > 2000:
                    # message too long to send, crop content
                    tosend = (f"highlight: {message.author.mention} ({message.author})"
                              f"in {message.channel.mention}({message.channel})"
                              f"\n{message.jump_url}\n\n{message.content[:500]}")

                await self.bot.owner.send(tosend)


def setup(bot):
    bot.add_cog(Highlighter(bot))
