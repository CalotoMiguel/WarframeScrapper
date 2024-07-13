
import datetime
import io
import time
from typing import Dict, Any

import discord
from warframe import Warframe
from warframeInternalMapper import *
from functools import reduce
import re
from collections import Counter

bonus_not_possible = ["WeaponMeleeComboPointsOnHitMod"]
curse_not_possible = ["WeaponFreezeDamageMod", "WeaponFireDamageMod", "WeaponToxinDamageMod", "WeaponPunctureDepthMod", "WeaponElectricityDamageMod", "WeaponMeleeDamageMod"]

def message_thinking(timestamp: datetime.datetime, edit: bool = False) -> Dict[str, Any]:
    embed = discord.Embed(
        title='Thinking ...',
        color=discord.Color.dark_orange(),
        timestamp=timestamp
    )
    files = 'attachments' if edit else 'files'
    return {
        'embed': embed,
        files: []
    }

def message_weapon_info(weapon: str, timestamp: datetime.datetime, edit: bool = False) -> Dict[str, Any]:
    weaponinfo = Warframe.getWeaponByName(weapon)
    if not weaponinfo:
        embed = discord.Embed(
            title=weapon,
            description='Weapon not recognized',
            color=discord.Color.red(),
            timestamp=timestamp
        )
    
        return {'embed': embed}
    file = discord.File(Warframe.getImage(weaponinfo["uniqueName"]), filename='weapon.png')
    embed = discord.Embed(
        title=weaponinfo["name"],
        description=DamageTypes.replaceWithEmoji(weaponinfo["description"]),
        color=discord.Color.blue(),
        timestamp=timestamp)
    embed.set_thumbnail(url='attachment://weapon.png')

    damages = map(lambda x, z : f'{z[2]} {x}', weaponinfo["damagePerShot"], DamageTypes.get())
    damages = filter(lambda x : x[-2:] != ' 0', damages)
    damages = reduce(lambda x, z : f'{x}\n{z}', damages)

    embed.add_field(name="Damage", value=damages)
    embed.add_field(name="Total Damage", value=weaponinfo["totalDamage"])
    if "multishot" in weaponinfo:
        embed.add_field(name="Multishot", value=weaponinfo["multishot"])
    if "masteryReq" in weaponinfo:
        embed.add_field(name="MR", value=weaponinfo["masteryReq"])
    if "fireRate" in weaponinfo:
        embed.add_field(name="Fire Rate", value=weaponinfo["fireRate"])
    if "range" in weaponinfo:
        embed.add_field(name="Range", value=weaponinfo["range"])
    if "comboDuration" in weaponinfo:
        embed.add_field(name="Combo Duration", value=weaponinfo["comboDuration"])
    if "criticalChance" in weaponinfo:
        embed.add_field(name="Critical Chance", value=f'{weaponinfo["criticalChance"] * 100:.0f} %')
    if "criticalMultiplier" in weaponinfo:
        embed.add_field(name="Critical Multiplier", value=f'{weaponinfo["criticalMultiplier"]:.1f}')
    if "procChance" in weaponinfo:
        embed.add_field(name="Status Chance", value=f'{weaponinfo["procChance"] * 100:.0f} %')
    if "omegaAttenuation" in weaponinfo:
        embed.add_field(name="Riven Disposition", value=f'{weaponinfo["omegaAttenuation"]:.2f}')
    files = 'attachments' if edit else 'files'
    return {
        'embed': embed,
        files: [file]
    }

def message_weapon_acquisition(weapon: str, timestamp: datetime.datetime, edit: bool = False) -> Dict[Counter, Any]:
    weaponinfo = Warframe.getWeaponByName(weapon)
    if not weaponinfo:
        embed = discord.Embed(
            title=weapon,
            description='Weapon not recognized',
            color=discord.Color.red(),
            timestamp=timestamp
        )
    
        return {'embed': embed}
    
    ingredients, image_bytes = Warframe.getRecipe(weaponinfo["uniqueName"], weaponinfo["name"])
    file_tree = discord.File(image_bytes, filename='weapon-crafting-tree.png')
    file = discord.File(Warframe.getImage(weaponinfo["uniqueName"]), filename='weapon.png')
    embed = discord.Embed(
        title=weaponinfo["name"],
        description="Required amount per resource",
        color=discord.Color.blue(),
        timestamp=timestamp
    )
    embed.set_thumbnail(url='attachment://weapon.png')
    
    for ingredient in ingredients.keys():
        embed.add_field(name=ingredient, value=ingredients[ingredient])
    files = 'attachments' if edit else 'files'
    return {
        'embed': embed,
        files: [file_tree, file]
    }

def message_riven_calculator(
        weapon: str,
        timestamp: datetime.datetime,
        edit: bool = False,
        has2bonus: bool = True,
        hasCurse: bool = False,
        lvl: int = 8) -> Dict[str, Any]:
    weaponinfo = Warframe.getWeaponByName(weapon)
    if not weaponinfo:
        embed = discord.Embed(
            title=weapon,
            description='Weapon not recognized',
            color=discord.Color.red(),
            timestamp=timestamp
        )
        return {'embed': embed}
    
    if has2bonus and hasCurse:
        bonus = 1.2375
        curse = -0.495
    if has2bonus and not hasCurse:
        bonus = 0.99
        curse = 0
    if not has2bonus and not hasCurse:
        bonus = 0.75
        curse = 0
    if not has2bonus and hasCurse:
        bonus = 0.9375
        curse = -0.75

    file = discord.File(Warframe.getImage(weaponinfo["uniqueName"]), filename='weapon.png')
    embed = discord.Embed(
        title=weaponinfo["name"],
        description="Riven Calculator",
        color=discord.Color.blue(),
        timestamp=timestamp
    )
    embed.set_thumbnail(url='attachment://weapon.png')
    stats = None
    if weaponinfo["productCategory"] == "LongGuns":
        if weaponinfo["multishot"] > 3:
            stats = Warframe.getShotgunRiven()
        else:
            stats = Warframe.getRifleRiven()
    elif weaponinfo["productCategory"] == "Pistols":
        stats = Warframe.getPistolRiven()
    elif weaponinfo["productCategory"] == "Melee":
        stats = Warframe.getMeleeRiven()
    elif weaponinfo["productCategory"] == "SpaceGuns":
        stats = Warframe.getArchGunRiven()
    
    if stats:
        text = ""
        
        for name in stats:
            if name not in bonus_not_possible:
                val = stats[name]["value"] * weaponinfo["omegaAttenuation"] * bonus * (lvl + 1) * 10
                if "reverseValueSymbol" in stats[name]:
                    val *= -1
                aux = str.replace(stats[name]["locTag"], "|STAT1|", "|val|")
                aux = str.replace(aux, "|val|%", f"({val * 90:.1f} to {val * 110:.1f})")
                aux = str.replace(aux, "|val| Damage to", f"(x{1 + val * 0.9:.2f} to x{1 + val * 1.1:.2f}) Damage to")
                aux = str.replace(aux, "|val|", f"({val * 0.9:.1f} to {val * 1.1:.1f})")
                text += aux + "\n"
        
        embed.add_field(name="Bonuses", value=DamageTypes.replaceWithEmoji(text))
        if hasCurse:
            text = ""
            for name in stats:
                if name not in curse_not_possible:
                    val = stats[name]["value"] * weaponinfo["omegaAttenuation"] * curse * (lvl + 1) * 10
                    if "reverseValueSymbol" in stats[name]:
                        val *= -1
                    aux = str.replace(stats[name]["locTag"], "|STAT1|", "|val|")
                    aux = str.replace(aux, "|val|%", f"({val * 110:.1f} to {val * 90:.1f})")
                    aux = str.replace(aux, "|val| Damage to", f"(x{1 + val * 1.1:.2f} to x{1 + val * 0.9:.2f}) Damage to")
                    aux = str.replace(aux, "|val|", f"({val * 1.1:.1f} to {val * 0.9:.1f})")
                    text += aux + "\n"

            embed.add_field(name="Curses", value=DamageTypes.replaceWithEmoji(text))

    files = 'attachments' if edit else 'files'
    return {
        'embed': embed,
        files: [file]
    }

def message_fisures(
    timestamp: datetime.datetime,
    select_relics: List[str] = None,
    select_factions: List[str] = None,
    select_missions: List[str] = None,
    select_sp: List[str] = None
):

    fisures = Warframe.getFisures()

    embed = discord.Embed(
        title="Fisures",
        color=discord.Color.blue(),
        timestamp=timestamp
    )
    
    def apply_filters(
        fisures: List[Dict],
        select_relics: List[str] = None,
        select_factions: List[str] = None,
        select_missions: List[str] = None,
        select_sp: List[str] = None
    ):
        return filter(
            lambda fisure : (
                (select_relics == None or fisure['Modifier'] in select_relics) and
                (select_factions == None or fisure['faction'] in select_factions) and
                (select_missions == None or fisure['MissionType'] in select_missions) and
                (select_sp == None or str(fisure['Hard']) in select_sp)
            ), fisures
        )
    
    fisures = apply_filters(fisures, select_relics, select_factions, select_missions, select_sp)
    flag = True
    for fisure in fisures:
        embed.add_field(name=f"{fisure['name']} ({fisure['systemName']})", value=Formatter.format_fisure(fisure))
        flag = False
    if flag:
        embed.add_field(name="There are no active fisures with the current filters", value="")
    return {'embed': embed}

def message_subscribe_fisures(
    userId: int,
    filter: int
):
    message = ""
    subscriptions = WarframeDB.get_reliq_by_user_filter(userId, filter)
    if (subscriptions != None and len(subscriptions) > 0):
        message = "You have subscriptions containing this filters"
    else:
        if (WarframeDB.get_num_reliq_by_user(userId) > 5):
            message = "You have reached the maximum number of subscriptions, this subscription will not be added"
        else:
            WarframeDB.insert_reliq(userId, filter)
            message = "Subscription has been added succesfully"
    return {'content': message }

def message_subscribed_fisures(
    timestamp: datetime.datetime,
    fisure: Dict,
    subId: int
):
    embed = discord.Embed(
        title="New fisure",
        color=discord.Color.blue(),
        timestamp=timestamp,
        description=f"SubscriptionId: {str(subId)}"
    )
    embed.add_field(name=f"{fisure['name']} ({fisure['systemName']})", value=Formatter.format_fisure(fisure))
    return {'embed': embed}

def message_manage_subscriptions(
    timestamp: datetime.datetime,
    subscriptions: List[Dict[str, Any]],
):
    embed = discord.Embed(
        title="Manage subscriptions",
        color=discord.Color.blue(),
        timestamp=timestamp
    )
    flag = True
    for subscription in subscriptions:
        filters = ConverterDB.convert_from_dbfilter(subscription[2])
        embed.add_field(name=f"SubscriptionId: {subscription[0]}", value=' | '.join([' | '.join(v) for v in filters.values()]))
        flag = False
    if flag:
        embed.add_field(name="You have not subscribed to any fisure yet", value="")
    return {
        'embed': embed
    }

def message_delete_subscription(
    timestamp: datetime.datetime,
    subscriptionId: int
):
    embed = discord.Embed(
        title="SubscriptionId: " + str(subscriptionId),
        color=discord.Color.blue(),
        timestamp=timestamp
    )
    subscription = WarframeDB.get_reliq_by_id(subscriptionId)
    filters = ConverterDB.convert_from_dbfilter(subscription[2])
    embed.add_field(name="Relic Types", value=' | '.join(filters["select_relics"]))
    embed.add_field(name="\t", value="\t")
    embed.add_field(name="\t", value="\t")
    embed.add_field(name="Faction Types", value=' | '.join(filters["select_factions"]))
    embed.add_field(name="\t", value="\t")
    embed.add_field(name="\t", value="\t")
    embed.add_field(name="Mission Types", value=' | '.join(filters["select_missions"]))
    embed.add_field(name="\t", value="\t")
    embed.add_field(name="\t", value="\t")
    embed.add_field(name="Difficulty", value=' | '.join(filters["select_sp"]))

    return {
        'embed': embed
    }

def message_deleted_subscription(
    timestamp: datetime.datetime,
    subscriptionId: int
):
    WarframeDB.delete_reliq(subscriptionId)
    embed = discord.Embed(
        title=f"Subscription with id {subscriptionId} was succesfully deleted",
        color=discord.Color.blue(),
        timestamp=timestamp
    )
    return {
        'embed': embed
    }

def __get_embed_baro(timestamp: datetime.datetime, collection: List[Dict], command: str) -> discord.Embed :
    baro = Warframe.getBaro()
    now = time.time()
    if not (int(baro['Activation']['$date']['$numberLong'][:-3]) < now < int(baro['Expiry']['$date']['$numberLong'][:-3])):
        embed = discord.Embed(
            title=f"Baro is set to arive <t:{baro['Activation']['$date']['$numberLong'][:-3]}:R>",
            color=discord.Color.blue(),
            timestamp=timestamp
        )
    else:
        embed = discord.Embed(
            title=f"Baro Ki'Teer leaves <t:{baro['Expiry']['$date']['$numberLong'][:-3]}:R>",
            color=discord.Color.blue(),
            timestamp=timestamp,
            description=command
        )
        for item in baro["Manifest"]:
            item_name = item["ItemType"][17:]
            complete_item = next(filter(lambda c : item_name == c["uniqueName"][6:], collection), None)
            if complete_item is not None:
                embed.add_field(name=complete_item["name"], value=f"<:credit:1246412644802367540> {item['RegularPrice']}\n<:ducat:1246412486308266056>{item['PrimePrice']}")
    return embed

def message_baro_weapons(timestamp: datetime.datetime):
    return {
        'embed': __get_embed_baro(
            timestamp,
            Warframe.getWeapons(),
            "Use </weaponinfo:1251458297584947280> to see more info about the weapons"
        )
    }

def message_baro_mods(timestamp: datetime.datetime):
    return {
        'embed': __get_embed_baro(
            timestamp,
            Warframe.getMods(),
            "Use </mod:1251458297781817408> to see more info about the mods"
        )
    }

def message_baro_cosmetics(timestamp: datetime.datetime):
    return {
        'embed': __get_embed_baro(
            timestamp,
            Warframe.getCustoms(),
            ""
        )
    }

def message_baro_resources(timestamp: datetime.datetime):
    return {
        'embed': __get_embed_baro(
            timestamp,
            Warframe.getResources(),
            ""
        )
    }

def message_mod(mod: str, timestamp: datetime.datetime):
    mod = Warframe.getModByName(mod)
    if not mod:
        embed = discord.Embed(
            title=mod,
            description='Mod not recognized',
            color=discord.Color.red(),
            timestamp=timestamp
        )
    
        return {'embed': embed}
    description = ""
    if "description" in mod:
        description = reduce(lambda x, z : f'{x}\n{z}', mod["description"])
    embed = discord.Embed(
        title=mod["name"],
        color=discord.Color.blue(),
        timestamp=timestamp,
        description=description)
    embed.set_thumbnail(url='mod://weapon.png')

    embed.add_field(name="Type", value=mod["type"].upper())
    embed.add_field(name="Compatibility", value=mod["compatName"].upper())
    embed.add_field(name="Polarity", value=PolarityTypes.replaceWithEmoji(mod["polarity"]))
    embed.add_field(name="Drain", value=mod["baseDrain"] + mod["fusionLimit"] if mod["baseDrain"] > 0 else mod["baseDrain"] - mod["fusionLimit"])
    if "levelStats" in mod:
        stats = reduce(lambda x, z : f'{x}\n{z}', mod["levelStats"][-1]["stats"])
        embed.add_field(name="Stats", value=DamageTypes.replaceWithEmoji(stats))
    return {
        'embed': embed
    }

def message_world_timers(timestamp: datetime.datetime):
    embed = discord.Embed(
        title="World Timers",
        color=discord.Color.blue(),
        timestamp=timestamp)
    now = int(timestamp.timestamp())
    cetus_end = Warframe.getCetusTimeCycle()

    cetus_night = 3000
    cetus_timer = cetus_end - now

    if cetus_timer < cetus_night:
        embed.add_field(name='Plains of Eidolon: Night', value=f"Day <t:{cetus_end}:R>")
    else:
        embed.add_field(name='Plains of Eidolon: Day', value=f"Night <t:{cetus_end - cetus_night}:R>")

    orb_start = 1718224833
    orb_loop = 1600
    orb_warm = 400
    orb_timer = (now - orb_start) % orb_loop
    if orb_timer < orb_warm:
        embed.add_field(name='Orb Vallis: Warm', value=f"Cold <t:{orb_warm-orb_timer+now}:R>")
    else:
        embed.add_field(name='Orb Vallis: Cold', value=f"Warm <t:{orb_loop-orb_timer+now}:R>")

    if cetus_timer < cetus_night:
        embed.add_field(name='Cambion Drift: Vome', value=f"Fass <t:{cetus_end}:R>")
    else:
        embed.add_field(name='Cambion Drift: Fass', value=f"Vome <t:{cetus_end - cetus_night}:R>")
    return {
        'embed': embed
    }

