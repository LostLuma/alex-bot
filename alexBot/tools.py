import json
from logging import getLogger


import config
import aiohttp
import xmltodict
from discord.ext import commands

log = getLogger(__name__)

configKeys = {
    "ayy": False,
    "tikTok": False,
    "veryCool": False,
}


class Cog(commands.Cog):
    """ The Cog base class that all cogs should inherit from. """

    def __init__(self, bot):
        self.bot = bot


class BoolConverter(commands.Converter):
    async def convert(self, ctx, argument):
        if argument[0].lower() == "f":
            return False
        elif argument[0].lower() == "t":
            return True
        else:
            raise commands.BadArgument(f'can not convert {argument} to True or False')


async def get_text(session: aiohttp.ClientSession, url) -> str:
    if config.location == 'dev':
        log.debug(f"fetched url: {url}")
    async with session.get(url) as content:
        return await content.text()


async def get_json(session: aiohttp.ClientSession, url, body=None) -> dict:
    if config.location == 'dev':
        log.debug(f"fetched json: {url}, body: {body}")

    async with session.get(url, data=body) as content:
        return await content.json()


async def get_xml(session: aiohttp.ClientSession, url) -> dict:
    if config.location == 'dev':
        log.debug(f"fetched xml: {url}")
    async with session.get(url) as content:
        return xmltodict.parse(await content.text())


async def create_guild_config(bot, guild_id: int) -> dict:
    log.info(f'creating a guild config for {guild_id}')
    cfg = json.dumps(configKeys)
    await bot.db.execute("""INSERT INTO configs (id, data) VALUES (?, ?)""", (guild_id, cfg))
    await bot.db.commit()
    return configKeys


async def get_guild_config(bot, guild_id: int) -> dict:
    ret = {}
    try:
        ret = bot.configs[guild_id]
    except KeyError:
        async with bot.db.cursor() as cur:
            await cur.execute("""SELECT data FROM configs WHERE id=?""", (guild_id,))
            ret = await cur.fetchone()

        if ret is None:
            ret = await create_guild_config(bot, guild_id)
        else:
            ret = json.loads(ret[0])
    finally:
        ret = {**configKeys, **ret}
        bot.configs[guild_id] = ret
    return ret


async def update_guild_key(bot, guild_id: int, key: str, value):
    """updates the `key` to be `value`.
    note: this method is extremely dumb,
    as it does no error checking to ensure that you are giving it the right value for a key."""
    bot.configs[guild_id][key] = value
    cfg = json.dumps(bot.configs[guild_id])
    await bot.db.execute("""UPDATE configs SET data=? WHERE id=?""", (cfg, guild_id))
    await bot.db.commit()


def metar_only_in_vasa(ctx: commands.Context):
    try:
        return not (ctx.guild.id == 377567755743789064 and ctx.command.name not in ['help', 'invite', 'info', 'metar'])
    except AttributeError:
        return True
