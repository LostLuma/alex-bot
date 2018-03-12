# -*- coding: utf-8 -*-

import re
import time

import discord
from discord.ext import commands
from lxml import html
from datetime import datetime
import json
import humanize

from ..tools import Cog
from ..tools import get_text
from ..tools import get_json


class Weather(Cog):
    @commands.command()
    async def weather(self, ctx, unit="c"):
        """Lets you access the alext.duckdns.org/weewx/{,c/} weather station from discord"""
        if unit.lower() not in set("fck"):
            raise commands.BadArgument("the only units i understand are [F, K, C].")
        if unit.lower() == "f":
            url = "http://alext.duckdns.org/weewx"
        else:
            url = "http://alext.duckdns.org/weewx/c"
        data = html.fromstring(await get_text(self.bot.session, url))

        temp = data.xpath('//*[@id="stats_group"]/div[1]/table/tbody/tr[1]/td[2]/text()')[0]
        wind = data.xpath('//*[@id="stats_group"]/div[1]/table/tbody/tr[8]/td[2]/text()')[0]
        in_temp = data.xpath('//*[@id="stats_group"]/div[1]/table/tbody/tr[10]/td[2]/text()')[0]

        if unit.lower() == "k":
            # add 237.15 to C to get kelvin for some WEIRDO
            rec = re.compile("-?([\d.])")
            temp = int(rec.search(temp).group(0))
            temp = f"{temp+237.15}k"
            in_temp = int(rec.search(in_temp).group(0))
            in_temp = f"{in_temp+237.15}k"
            # set the URL to none to prevent getting a graph for K that doesnt exist.
            url = None

        if "N/A" in wind:
            msg = f"Weather at Alex's Home:\nTemp: {temp}\nInside Tempature: {in_temp}"
        else:
            msg = f"Weather at Alex's Home:\nTemp: {temp}\nWind speed: {wind}\nInside Tempature: {in_temp}"

        if url is not None:
            embed = discord.Embed()
            embed.set_image(url=f"{url}/daytempdew.png?t={int(time.time()/300)}")
            await ctx.send(msg, embed=embed)
        else:
            await ctx.send(msg)

    @commands.command()
    async def metar(self, ctx, station: str):
        """Returns the METAR report for a station. acccepts ICAO stations. uses avwx.rest as a data source."""
        station = station.upper()
        data = await get_json(self.bot.session, f'https://avwx.rest/api/metar/{station}?options=info,speech,translate')
        if 'Error' in data:
            raise commands.errors.BadArgument(data['Error'])

        embed = discord.Embed()
        now = datetime.utcnow()
        report_time = datetime.strptime(data['Time'], "%d%H%MZ")
        report_time = report_time.replace(year=now.year, month=now.month)  # this will fail around end of month / year
        color = data['Flight-Rules']

        if color == "VFR":
            color = discord.Color.green()
        elif color == "MVFR":
            color = discord.Color.blue()
        elif color == "IFR":
            color = discord.Color.red()
        elif color == "LIFR":
            color = discord.Color.magenta()
        else:
            color = discord.Color.default()
        embed.colour = color
        embed.set_footer(text=f"METAR from {station} from {humanize.naturaldelta(report_time-now)} ago")
        info = data['Info']
        try:
            if info['City'] == '':
                city = None
            else:
                city = info['City']

            if info['State'] == '':
                state = None
            else:
                state = info['State']

            if info['Country'] == '':
                    country = None
            else:
                country = info['Country']
        except KeyError:
            city = None
            state = None
            country = None
        try:
            if info['Name'] == '':
                embed.title = station
            else:
                embed.title = info['Name']
        except KeyError:
            embed.title = station

        if city is not None:
            embed.title += f", {city}"
        if state is not None:
            embed.title += f", {state}"
        if country is not None:
            embed.title += f", {country}"

        embed.add_field(name="Raw", value=data['Raw-Report'])
        embed.add_field(name="Readable", value=data['Speech'])
        embed.add_field(name="Clouds", value=data['Translations']['Clouds'])
        embed.add_field(name="Wind", value=data['Translations']['Wind'])
        embed.add_field(name="Altimeter", value=data['Translations']['Altimeter'], inline=True)
        embed.add_field(name="Temperature", value=data['Translations']['Temperature'], inline=True)
        embed.add_field(name="Flight Rule", value=data['Flight-Rules'], inline=True)
        embed.add_field(name="Visibility", value=data['Translations']['Visibility'], inline=True)
        embed.timestamp = report_time

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Weather(bot))
