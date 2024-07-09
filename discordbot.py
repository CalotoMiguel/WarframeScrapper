import datetime
import os
import time
from typing import List, Literal, Optional

import discord
from dotenv import load_dotenv
load_dotenv()

from endpoints import get_endpoints
from warframe import Warframe
import responsesBot

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = None
if os.getenv('GUILD_ID') is not None:
    GUILD = discord.Object(id=int(os.getenv('GUILD_ID')))

from viewsBot import *
import discord
from discord.ext import tasks
from discord import app_commands


class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.tree = app_commands.CommandTree(self)
        WarframeDB.refresh_endpoints(get_endpoints())
        WarframeDB.refresh_manifest(Warframe.getManifest())
        self.weapons = Warframe.getWeaponNames()
        self.mods = Warframe.getModNames()
        WarframeDB.refresh_unique_names(Warframe.getWeapons(), Warframe.getResources())

    async def setup_hook(self):
        self.add_view(WeaponView())
        self.add_view(RivensView())
        self.add_view(FisuresView())
        self.add_view(DeleteSubscriptionView())
        self.add_view(SubscriptionsView())
        self.add_view(BaroView())
        self.add_view(WorldTimersView())
        if GUILD is not None:
            self.tree.copy_global_to(guild=GUILD)
        await self.tree.sync(guild=GUILD)
        self.check_fisures.start()
        self.update_weapon_names.start()
        self.update_mod_names.start()
        self.refresh_unique_names.start()
        self.refresh_endpoints.start()
    
    @tasks.loop(seconds=10)
    async def check_fisures(self):
        for fisure in sorted(Warframe.getFisures(), key=lambda x: x["Expiry"], reverse=True):
            for (subId, userId) in WarframeDB.get_reliq_by_filter_time(
                ConverterDB.convert_to_dbfilter(
                    [fisure["Modifier"]],
                    [fisure["faction"]],
                    [fisure["MissionType"]],
                    [str(fisure["Hard"])]
                ),
                fisure["Expiry"]
            ):
                WarframeDB.update_time_by_id(subId, fisure["Expiry"])
                message = responsesBot.message_subscribed_fisures(
                    timestamp=datetime.datetime.now(),
                    fisure=fisure,
                    subId=subId
                )
                await client.get_user(int(userId)).send(**message, view=DeleteSubscriptionView())
    @check_fisures.before_loop
    async def before_check_fisures(self):
        await self.wait_until_ready()
    
    @tasks.loop(minutes=10)
    async def update_weapon_names(self):
        self.weapons = Warframe.getWeaponNames()
    @update_weapon_names.before_loop
    async def before_update_weapon_names(self):
        await self.wait_until_ready()
    
    @tasks.loop(minutes=10)
    async def update_mod_names(self):
        self.mods = Warframe.getModNames()

    @update_mod_names.before_loop
    async def before_update_mod_names(self):
        await self.wait_until_ready()
    
    @tasks.loop(minutes=10)
    async def refresh_unique_names(self):
        WarframeDB.refresh_unique_names(Warframe.getWeapons(), Warframe.getResources())

    @refresh_unique_names.before_loop
    async def before_refresh_unique_names(self):
        await self.wait_until_ready()

    @tasks.loop(minutes=10)
    async def refresh_endpoints(self):
        WarframeDB.refresh_endpoints(get_endpoints())

    @refresh_endpoints.before_loop
    async def before_refresh_endpoints(self):
        await self.wait_until_ready()

    @tasks.loop(minutes=10)
    async def refresh_manifest(self):
        WarframeDB.refresh_manifest(Warframe.getManifest())

    @refresh_manifest.before_loop
    async def before_refresh_manifest(self):
        await self.wait_until_ready()

client = MyClient()

async def weapon_autocomplete(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name=weapon, value=weapon)
            for weapon in client.weapons
            if weapon.lower().startswith(current.lower())
    ][:25]


@client.tree.command(name="weaponinfo", description="Fetch the information of a weapon", guild=GUILD)
@app_commands.autocomplete(weapon=weapon_autocomplete)
async def weaponinfo(interaction: discord.Interaction, weapon: str):
    await interaction.response.defer(thinking=True)
    await interaction.followup.send(
        **responsesBot.message_weapon_info(weapon, interaction.created_at),
        view=WeaponView(0)
    )


@client.tree.command(name="weaponacquisition", description="Fetch the acquisition of a weapon", guild=GUILD)
@app_commands.autocomplete(weapon=weapon_autocomplete)
async def weaponacquisition(interaction: discord.Interaction, weapon: str):
    await interaction.response.defer(thinking=True)
    await interaction.followup.send(
        **responsesBot.message_weapon_acquisition(weapon, interaction.created_at),
        view=WeaponView(1)
    )


@client.tree.command(name="rivencalculator", description="Calculator for riven of a weapon", guild=GUILD)
@app_commands.autocomplete(weapon=weapon_autocomplete)
async def rivencalculator(interaction: discord.Interaction, weapon: str):
    await interaction.response.defer(thinking=True)
    await interaction.followup.send(
        **responsesBot.message_riven_calculator(
            weapon,
            interaction.created_at
        ),
        view = RivensView()
    )


@client.tree.command(name="fisures", description="Fetch the active fisures", guild=GUILD)
async def fisures(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    await interaction.followup.send(
        **responsesBot.message_fisures(timestamp=interaction.created_at),
        view = FisuresView()
    )


@client.tree.command(name="managesubscriptions", description="Manage subscriptions", guild=GUILD)
async def managesubscriptions(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True, ephemeral=True)
    subscriptions = WarframeDB.get_reliq_by_user(interaction.user.id)
    args = { "ephemeral" : True }
    if len(subscriptions) > 0:
        args["view"] = SubscriptionsView(subscriptions=subscriptions)
    await interaction.followup.send(
        **responsesBot.message_manage_subscriptions(timestamp=interaction.created_at, subscriptions=subscriptions),
        **args
    )


@client.tree.command(name="baro", description="Baro Ki'Teer Offerings", guild=GUILD)
async def baro(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    await interaction.followup.send(
        **responsesBot.message_baro_weapons(timestamp=interaction.created_at),
        view = BaroView(0)
    )



async def mod_autocomplete(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name=mod, value=mod)
            for mod in client.mods
            if mod.lower().startswith(current.lower())
    ][:25]


@client.tree.command(name="mod", description="Fetch the information of a mod", guild=GUILD)
@app_commands.autocomplete(mod=mod_autocomplete)
async def mod(interaction: discord.Interaction, mod: str):
    await interaction.response.defer(thinking=True)
    await interaction.followup.send(
        **responsesBot.message_mod(mod, interaction.created_at)
    )


@client.tree.command(name="worldtimers", description="Show the local times of open worlds", guild=GUILD)
async def worldtimers(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    await interaction.followup.send(
        **responsesBot.message_world_timers(interaction.created_at),
        view=WorldTimersView()
    )


client.run(TOKEN)
