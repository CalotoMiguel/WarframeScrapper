from time import sleep
from typing import Any
import discord
import responsesBot
from warframeInternalMapper import *


class WeaponView(discord.ui.View):
    def __init__(self, button: int = 0):
        super().__init__(timeout=None)
        self.update_buttons(button)

    def get_view(self, button: int = 0):
        self.update_buttons(button)
        return self

    def update_buttons(self, button: int):
        self.weapon_info_button.disabled = True if button == 0 or button < 0 else False
        self.weapon_acquisition_button.disabled = True if button == 1 or button < 0 else False
        self.riven_calculator_button.disabled = True if button == 2 or button < 0 else False

    @discord.ui.button(label="Weapon Info", custom_id="weapon-info-button", style=discord.ButtonStyle.primary, row=2)
    async def weapon_info_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.edit(
            **responsesBot.message_weapon_info(
                interaction.message.embeds[0].title,
                interaction.created_at,
                True
            ),
            view = self.get_view(0)
        )
        await interaction.response.defer()

    @discord.ui.button(label="Weapon Acquisition", custom_id="weapon-acquisition-button", style=discord.ButtonStyle.primary, row=2)
    async def weapon_acquisition_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        weapon = interaction.message.embeds[0].title
        await interaction.message.edit(
            **responsesBot.message_thinking(interaction.created_at, True),
            view = self.get_view(-1)
        )
        await interaction.response.defer()
        await interaction.message.edit(
            **responsesBot.message_weapon_acquisition(
                weapon,
                interaction.created_at,
                True
            ),
            view = self.get_view(1)
        )

    @discord.ui.button(label="Riven Calculator", custom_id="riven-calculator-button", style=discord.ButtonStyle.primary, row=2)
    async def riven_calculator_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.edit(
            **responsesBot.message_riven_calculator(
                interaction.message.embeds[0].title,
                interaction.created_at,
                True
            ),
            view = RivensView()
        )
        await interaction.response.defer()
    

class RivensView(WeaponView):
    def __init__(self, button: int = 0):
        super().__init__()
        self.update_riven(True, False, '8')

    def update_buttons(self, button: int):
        self.weapon_info_button.disabled = False
        self.weapon_acquisition_button.disabled = False
        self.riven_calculator_button.disabled = True
    
    def get_has2bonuses(self, interaction: discord.Interaction) -> bool:
        return interaction.message.components[0].children[0].disabled
    
    def get_hascurse(self, interaction: discord.Interaction) -> bool:
        return interaction.message.components[0].children[2].disabled

    def get_lvl(self, interaction: discord.Interaction) -> str:
        return [option.value for option in interaction.message.components[1].children[0].options if option.default == True][0]
    
    def update_riven(self, has2bonus: bool, hascurse: bool, lvl: str):
        for option in self.riven_lvl_select.options:
            option.default = option.value == lvl
        self.riven_2bonuses_button.disabled = has2bonus
        self.riven_3bonuses_button.disabled = not has2bonus
        self.riven_curse_button.disabled = hascurse
        self.riven_notcurse_button.disabled = not hascurse

    def get_view(self, button: int = 0):
        return WeaponView(button)
    

    @discord.ui.button(label="2 Bonuses", custom_id="riven-2bonuses-button", style=discord.ButtonStyle.primary, disabled=True, row=0)
    async def riven_2bonuses_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.update_riven(
            True,
            self.get_hascurse(interaction),
            self.get_lvl(interaction)
        )
        await interaction.message.edit(
            **responsesBot.message_riven_calculator(
                interaction.message.embeds[0].title,
                interaction.created_at,
                True,
                True,
                self.get_hascurse(interaction),
                int(self.get_lvl(interaction))
            ),
            view = self
        )
        await interaction.response.defer()

    @discord.ui.button(label="3 Bonuses", custom_id="riven-3bonuses-button", style=discord.ButtonStyle.primary, row=0)
    async def riven_3bonuses_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.update_riven(
            False,
            self.get_hascurse(interaction),
            self.get_lvl(interaction)
        )
        await interaction.message.edit(
            **responsesBot.message_riven_calculator(
                interaction.message.embeds[0].title,
                interaction.created_at,
                True,
                False,
                self.get_hascurse(interaction),
                int(self.get_lvl(interaction))
            ),
            view = self
        )
        await interaction.response.defer()

    @discord.ui.button(label="Has curse", custom_id="riven-curse-button", style=discord.ButtonStyle.danger, row=0)
    async def riven_curse_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.update_riven(
            self.get_has2bonuses(interaction),
            True,
            self.get_lvl(interaction)
        )
        await interaction.message.edit(
            **responsesBot.message_riven_calculator(
                interaction.message.embeds[0].title,
                interaction.created_at,
                True,
                self.get_has2bonuses(interaction),
                True,
                int(self.get_lvl(interaction))
            ),
            view = self
        )
        await interaction.response.defer()

    @discord.ui.button(label="Does not have curse", custom_id="riven-notcurse-button", style=discord.ButtonStyle.danger, row=0, disabled=True)
    async def riven_notcurse_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.update_riven(
            self.get_has2bonuses(interaction),
            False,
            self.get_lvl(interaction)
        )
        await interaction.message.edit(
            **responsesBot.message_riven_calculator(
                interaction.message.embeds[0].title,
                interaction.created_at,
                True,
                self.get_has2bonuses(interaction),
                False,
                int(self.get_lvl(interaction))
            ),
            view = self
        )
        await interaction.response.defer()

    riven_lvl_options=[
                discord.SelectOption(label=num, value=num, default=(num == 8)) for num in range(0,9)
            ]
    @discord.ui.select(custom_id="riven-lvl-button", row=1, options=riven_lvl_options)
    async def riven_lvl_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.update_riven(
            self.get_has2bonuses(interaction),
            self.get_hascurse(interaction),
            select.values[0]
        )
        await interaction.message.edit(
            **responsesBot.message_riven_calculator(
                interaction.message.embeds[0].title,
                interaction.created_at,
                True,
                self.get_has2bonuses(interaction),
                self.get_hascurse(interaction),
                int(select.values[0])
            ),
            view = self
        )
        await interaction.response.defer()

class FisuresView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.update_selects(None, None, None, None)
    
    def get_values_from_interaction(self, interaction: discord.Interaction, row: int) -> Dict[str, List]:
        returned = {}
        if row != 0:
            returned["select_relics"] = [option.value for option in interaction.message.components[0].children[0].options if option.default == True]
        if row != 1:
            returned["select_factions"] = [option.value for option in interaction.message.components[1].children[0].options if option.default == True]
        if row != 2:
            returned["select_missions"] = [option.value for option in interaction.message.components[2].children[0].options if option.default == True]
        if row != 3:
            returned["select_sp"] = [option.value for option in interaction.message.components[3].children[0].options if option.default == True]
        return returned

    def update_selects(self, select_relics, select_factions, select_missions, select_sp):
        for option in self.faction_types_fisures_select.options:
            option.default = True if select_factions == None else str(option.value) in select_factions
        for option in self.relic_types_fisures_select.options:
            option.default = True if select_relics == None else str(option.value) in select_relics
        for option in self.mission_types_fisures_select.options:
            option.default = True if select_relics == None else str(option.value) in select_missions
        for option in self.sp_fisures_select.options:
            option.default = True if select_sp == None else str(option.value) in select_sp
        

    relic_type_options=[
            discord.SelectOption(label=relic_type[1], value=relic_type[2], default=True) for relic_type in RelicTypes.get()
        ]
    @discord.ui.select(custom_id="relic-types-fisures-select", min_values=1, max_values=len(relic_type_options), options=relic_type_options, row=0)
    async def relic_types_fisures_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.update_selects(
            select_relics=select.values,
            **self.get_values_from_interaction(interaction, 0)
        )
        await interaction.message.edit(
            **responsesBot.message_fisures(
                interaction.created_at,
                select_relics=select.values,
                **self.get_values_from_interaction(interaction, 0)),
            view = self
        )
        await interaction.response.defer()
    
    faction_type_options=[
            discord.SelectOption(label=faction_type[1], value=faction_type[1], default=True) for faction_type in FactionTypes.get()
        ]
    @discord.ui.select(custom_id="faction-types-fisures-select", min_values=1, max_values=len(faction_type_options), options=faction_type_options, row=1)
    async def faction_types_fisures_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.update_selects(
            select_factions=select.values,
            **self.get_values_from_interaction(interaction, 1)
        )
        await interaction.message.edit(
            **responsesBot.message_fisures(
                interaction.created_at,
                select_factions=select.values,
                **self.get_values_from_interaction(interaction, 1)),
            view = self
        )
        await interaction.response.defer()
    
    mission_type_options=[
            discord.SelectOption(label=mission_type[1], value=mission_type[2], default=True) for mission_type in MissionTypes.get() if mission_type[2] != ""
        ]
    @discord.ui.select(custom_id="mission-types-fisures-select", min_values=1, max_values=len(mission_type_options), options=mission_type_options, row=2)
    async def mission_types_fisures_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.update_selects(
            select_missions=select.values,
            **self.get_values_from_interaction(interaction, 2)
        )
        await interaction.message.edit(
            **responsesBot.message_fisures(
                interaction.created_at,
                select_missions=select.values,
                **self.get_values_from_interaction(interaction, 2)),
            view = self
        )
        await interaction.response.defer()

    sp_options=[
            discord.SelectOption(label="Steel Path", value='True', default=True),
            discord.SelectOption(label="Normal", value='False', default=True)
        ]
    
    @discord.ui.select(custom_id="sp-fisures-select", min_values=1, max_values=len(sp_options), options=sp_options, row=3)
    async def sp_fisures_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.update_selects(
            select_sp=select.values,
            **self.get_values_from_interaction(interaction, 3)
        )
        await interaction.message.edit(
            **responsesBot.message_fisures(
                interaction.created_at,
                select_sp=select.values,
                **self.get_values_from_interaction(interaction, 3)),
            view = self
        )
        await interaction.response.defer()

    @discord.ui.button(label="⟳ Reload", custom_id="reload-fisures-button", style=discord.ButtonStyle.success, row=4)
    async def reload_fisures_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.update_selects(
            **self.get_values_from_interaction(interaction, -1)
        )
        await interaction.message.edit(
            **responsesBot.message_fisures(
                interaction.created_at,
                **self.get_values_from_interaction(interaction, -1)),
            view = self
        )
        await interaction.response.defer()

    @discord.ui.button(label="Subscribe", custom_id="subscribe-fisures-button", style=discord.ButtonStyle.success, row=4)
    async def subscribe_fisures_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        filter = ConverterDB.convert_to_dbfilter(
            **self.get_values_from_interaction(interaction, -1)
        )
        await interaction.response.send_message(
            **responsesBot.message_subscribe_fisures(interaction.user.id, filter),
            ephemeral=True
        )

    @discord.ui.button(label="Select All", custom_id="select-fisures-button", style=discord.ButtonStyle.primary, row=4)
    async def select_fisures_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.update_selects(None, None, None, None)
        await interaction.message.edit(
            **responsesBot.message_fisures(interaction.created_at),
            view = self
        )
        await interaction.response.defer()

    @discord.ui.button(label="Unselect All", custom_id="unselect-fisures-button", style=discord.ButtonStyle.danger, row=4)
    async def unselect_fisures_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.update_selects(
            [self.relic_types_fisures_select.options[0].value],
            [self.faction_types_fisures_select.options[0].value],
            [self.mission_types_fisures_select.options[0].value],
            [self.sp_fisures_select.options[0].value])
        await interaction.message.edit(
            **responsesBot.message_fisures(
                interaction.created_at,
                select_relics=[self.relic_types_fisures_select.options[0].value],
                select_factions=[self.faction_types_fisures_select.options[0].value],
                select_missions=[self.mission_types_fisures_select.options[0].value],
                select_sp=[self.sp_fisures_select.options[0].value]),
            view = self
        )
        await interaction.response.defer()

class DeleteSubscriptionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Delete", custom_id="delete-subscription", style=discord.ButtonStyle.danger, row=4)
    async def delete_subscription(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.message.embeds[0].title.startswith("SubscriptionId: "):
            subscriptionId = int(interaction.message.embeds[0].title[len("SubscriptionId: "):])
        else:
            subscriptionId = int(interaction.message.embeds[0].description[len("SubscriptionId: "):])
        await interaction.response.edit_message(
            **responsesBot.message_deleted_subscription(
                interaction.created_at,
                subscriptionId),
            view=None
        )

class SubscriptionsView(discord.ui.View):
    def __init__(self, subscriptions: List[Dict[str, Any]] = []):
        super().__init__(timeout=None)
        self.selected_subscription.options = self.getOptions(subscriptions)


    def getOptions(self, subscriptions: List[Dict[str, Any]]) -> List[discord.SelectOption]:
        return [
            discord.SelectOption(label=subscription[0]) for subscription in subscriptions
        ]

    @discord.ui.select(custom_id="subscription-list", options = None)
    async def selected_subscription(self, interaction: discord.Interaction, select: discord.ui.Select):
        
        await interaction.response.edit_message(
            **responsesBot.message_delete_subscription(
                interaction.created_at,
                int(select.values[0])
            ),
            view = DeleteSubscriptionView()
        )

class BaroView(discord.ui.View):
    def __init__(self, button: int = 0):
        super().__init__(timeout=None)
        self.update_buttons(button)

    def update_buttons(self, button: int):
        self.baro_weapons.disabled = True if button == 0 else False
        self.baro_mods.disabled = True if button == 1 else False
        self.baro_cosmetics.disabled = True if button == 2 else False
        self.baro_resources.disabled = True if button == 3 else False

    @discord.ui.button(label="Weapons", custom_id="baro-weapons", style=discord.ButtonStyle.primary, row=2)
    async def baro_weapons(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.update_buttons(0)
        await interaction.message.edit(
            **responsesBot.message_baro_weapons(interaction.created_at),
            view = self
        )
        await interaction.response.defer()

    @discord.ui.button(label="Mods", custom_id="baro-mods", style=discord.ButtonStyle.primary, row=2)
    async def baro_mods(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.update_buttons(1)
        await interaction.message.edit(
            **responsesBot.message_baro_mods(interaction.created_at),
            view = self
        )
        await interaction.response.defer()

    @discord.ui.button(label="Cosmetics", custom_id="baro-cosmetics", style=discord.ButtonStyle.primary, row=2)
    async def baro_cosmetics(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.update_buttons(2)
        await interaction.message.edit(
            **responsesBot.message_baro_cosmetics(interaction.created_at),
            view = self
        )
        await interaction.response.defer()

    @discord.ui.button(label="Resources", custom_id="baro-resources", style=discord.ButtonStyle.primary, row=2)
    async def baro_resources(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.update_buttons(3)
        await interaction.message.edit(
            **responsesBot.message_baro_resources(interaction.created_at),
            view = self
        )
        await interaction.response.defer()

class WorldTimersView(discord.ui.View):
    def __init__(self, button: int = 0):
        super().__init__(timeout=None)

    @discord.ui.button(label="⟳ Reload", custom_id="reload-timers-button", style=discord.ButtonStyle.success, row=4)
    async def baro_weapons(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.edit(
            **responsesBot.message_word_timers(interaction.created_at),
            view = self
        )
        await interaction.response.defer()
