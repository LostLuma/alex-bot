# -*- coding: utf-8 -*-

import asyncio
import datetime
import re

import discord
import humanize
from discord.ext import commands

from ..tools import Cog

DATEFORMAT = "%a, %e %b %Y %H:%M:%S (%-I:%M %p)"


class Utils(Cog):
    """The description for Utils goes here."""

    @commands.command(aliases=['p'])
    async def ping(self, ctx: commands.Context):
        """returns the webscocket and rest ping times."""
        start = await ctx.send(f"Pong! WS: {ctx.bot.latency * 1000:.2f} ms,..")
        a = start.created_at
        now = datetime.datetime.utcnow()
        ping = now - a

        await start.edit(content=f"Pong! WS: {ctx.bot.latency * 1000:.2f} ms, rest: {ping.microseconds / 1000:.2f} ms")

    @commands.command()
    async def time(self, ctx: commands.Context):
        """Displays the time in alaska"""
        time = datetime.datetime.now()
        await ctx.send(f'the time in alaska is {time.strftime(DATEFORMAT)}')

    @commands.command(aliases=['diff'])
    async def difference(self, ctx: commands.Context, object_one: int, object_two: int = None):
        """Compares the creation time of two IDs. default to comparing to the current time."""
        one = discord.utils.snowflake_time(object_one)
        now = False
        if object_two is None:
            object_two = ctx.message.id
            now = True
        two = discord.utils.snowflake_time(object_two)
        if one > two:
            diff = one - two
        else:
            diff = two - one
        await ctx.send(
            f'time difference from {f"`{two}`" if not now else "Now"} to `{one}` is `{diff}` (around {humanize.naturaldelta(diff)}).'
        )

    @commands.command(name='info', aliases='source about git'.split())
    async def info(self, ctx):
        """general bot information"""
        ret = discord.Embed()
        ret.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        ret.add_field(name='Support Server', value='[link](https://discord.gg/jMwPFqp)')
        ret.add_field(name='Source Code', value='[github](https://github.com/mralext20/alex-bot)')
        ret.add_field(name='Servers', value=str(len(self.bot.guilds)))
        ret.add_field(name='Members', value=str(len(list(self.bot.get_all_members()))))
        await ctx.send(embed=ret)

    @commands.command(name='inviteDetails')
    async def inviteDetails(self, ctx, invite: discord.Invite):
        """Tells you about an invite, such as how many members the server it's pointed to has and more!"""
        if invite.revoked:
            return await ctx.send("That invite is revoked...")
        ret = discord.Embed()
        ret.set_thumbnail(url=invite.guild.icon_url)
        ret.title = invite.guild.name
        ret.add_field(name='aprox members', value=invite.approximate_member_count, inline=True)
        ret.add_field(name='Aprox Present Members', value=invite.approximate_presence_count, inline=True)
        ret.add_field(name='guild created at', value=invite.guild.created_at, inline=True)
        ret.add_field(name='guild ID', value=invite.guild.id, inline=True)
        ret.add_field(name='verification level', value=invite.guild.verification_level, inline=True)
        if invite.guild.features:
            ret.add_field(name='features:', value=', '.join(invite.guild.features), inline=False)
        if invite.inviter:
            ret.add_field(name='inviter name', value=invite.inviter.name, inline=True)
            ret.add_field(name='inviter id', value=invite.inviter.id, inline=True)
        if invite.channel:
            ret.add_field(name='channel target', value=invite.channel.name, inline=True)
            ret.add_field(name='channel Type', value=invite.channel.type, inline=True)

        await ctx.send(embed=ret)

    @commands.command()
    async def invite(self, ctx):
        """tells you my invite link!"""
        await ctx.send(
            f"<https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&scope=bot%20applications.commands>"
        )

    @commands.command()
    @commands.has_guild_permissions(move_members=True)
    @commands.bot_has_guild_permissions(move_members=True)
    async def voice_move(self, ctx: commands.Context, target: discord.VoiceChannel):
        if not ctx.author.voice:
            raise ValueError("you must be in a voice call!")
        for user in ctx.author.voice.channel.members:
            ctx.bot.loop.create_task(user.move_to(target, reason=f"as requested by {ctx.author}"))
        await ctx.send(":ok_hand:")


def setup(bot):
    bot.add_cog(Utils(bot))
