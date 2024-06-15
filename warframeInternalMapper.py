
from typing import Dict, List, Tuple

from database import WarframeDB
import re

class Formatter():
    @staticmethod
    def format_fisure(fisure: Dict) -> str:
        return f"\
            Type: {RelicTypes.get_by_internal(fisure['Modifier'])}\n\
            Mission Type: {MissionTypes.get_by_internal(fisure['MissionType'])}\n\
            Faction: {fisure['faction']}\n\
            SP: {True if fisure['Hard'] else False}\n\
            Expires: <t:{fisure['Expiry']}:R>"

class MissionTypes():
    @staticmethod
    def get() -> List[Tuple[int, str, str]]:
        return [
            (0, "Assassination", "MT_ASSASSINATION"),
            (1, "Exterminate", "MT_EXTERMINATION"),
            (2, "Survival", "MT_SURVIVAL"),
            (3, "Rescue", "MT_RESCUE"),
            (4, "Sabotage", "MT_SABOTAGE"),
            (5, "Capture", "MT_CAPTURE"),
            (6, "Unknown", ""),
            (7, "Spy", "MT_INTEL"),
            (8, "Defense", "MT_DEFENSE"),
            (9, "Mobile Defense", "MT_MOBILE_DEFENSE"),
            (10, "Unknown", ""),
            (11, "Unknown", ""),
            (12, "Unknown", ""),
            (13, "Interception", "MT_TERRITORY"),
            (14, "Hijack", "MT_RETRIEVAL"),
            (15, "Hive Sabotage", "MT_HIVE"),
            (16, "Unknown", ""),
            (17, "Excavation", "MT_EXCAVATE"),
            (18, "Unknown", ""),
            (19, "Unknown", ""),
            (20, "Unknown", ""),
            (21, "Alchemy", "MT_ALCHEMY"),
            (22, "Arena", "MT_ARENA"),
            (23, "Unknown", ""),
            (24, "Pursuit", ""),
            (25, "Rush", "MT_RACE"),
            (26, "Assault", "MT_ASSAULT"),
            (27, "Defection", "MT_EVACUATION"),
            (28, "Landscape", "MT_LANDSCAPE"),
            (29, "Unknown", ""),
            (30, "Unknown", ""),
            (31, "Unknown", ""),
            (32, "Disruption", "MT_ARTIFACT"),
            (33, "Void Flood", "MT_CORRUPTION"),
            (34, "Void Cascade", "MT_VOID_CASCADE"),
            (35, "Void Armageddon", "MT_ARMAGEDDON")
        ]
    
    @staticmethod
    def get_by_internal(internal: str) -> str:
        return next(filter(lambda x : x[2] == internal, MissionTypes.get()), None)[1]
    
    @staticmethod
    def get_id_by_list_internal(internal: List[str]) -> List[int]:
        return map(lambda x : x[0], filter(lambda x : x[2] in internal, MissionTypes.get()))
    
class DamageTypes():
    @staticmethod
    def get() -> List[Tuple[int, str, str]]:
        return [
            (0, '<DT_IMPACT>', '<:impact:1204552392587345970>'),
            (1, '<DT_PUNCTURE>', '<:puncture:1204881523896221746>'),
            (2, '<DT_SLASH>', '<:slash:1204881625997901885>'),
            (3, '<DT_FIRE>', '<:heat:1204881859255738460>'),
            (4, '<DT_FREEZE>', '<:cold:1204881710466994308>'),
            (5, '<DT_ELECTRICITY>', '<:electic:1204881772568117248>'),
            (6, '<DT_POISON>', '<:toxin:1204881925773201408>'),
            (7, '<DT_EXPLOSION>', '<:blast:1204882016240275566>'),
            (8, '<DT_RADIATION>', '<:radiation:1204882305991057459>'),
            (9, '<DT_GAS>', '<:gas:1204882181210775583>'),
            (10, '<DT_MAGNETIC>', '<:magnetic:1204882245069053952>'),
            (11, '<DT_VIRAL>', '<:viral:1204882377504067634>'),
            (12, '<DT_CORROSIVE>', '<:corrosive:1204882079586979860>'),
            (13, '<DT_RADIANT>', '<:void:1204882498920644649>'),
            (14, '<DT_SENTIENT>', '<:tau:1204883887847776256>'),
            (15, '<DT_CINEMATIC>', '<DT_CINEMATIC>'),
            (16, '<DT_SHIELD_DRAIN>', '<DT_SHIELD_DRAIN>'),
            (17, '<DT_HEALTH_DRAIN>', '<:true:1204882438531063829>'),
            (18, '<DT_ENERGY_DRAIN>', '<DT_ENERGY_DRAIN>'),
            (19, '<DT_HEALTH_DRAIN>', '<:true:1204882438531063829>')
        ]
    
    @staticmethod
    def replaceWithEmoji(string: str) -> str:
        pattern = '|'.join(sorted(re.escape(item[1]) for item in DamageTypes.get()))
        return re.sub(pattern, lambda m: DamageTypes.get_emoji_by_internal(m.group(0).upper()) + " ", string, flags=re.IGNORECASE)
    
    @staticmethod
    def get_emoji_by_internal(internal: str) -> str:
        return next(filter(lambda x : x[1] == internal, DamageTypes.get()), None)[2]
class RelicTypes():
    @staticmethod
    def get() -> List[Tuple[str, str]]:
        return [
            (0, "Lith", "VoidT1"),
            (1, "Meso", "VoidT2"),
            (2, "Neo", "VoidT3"),
            (3, "Axi", "VoidT4"),
            (4, "Requiem", "VoidT5"),
            (5, "Omnia", "VoidT6")
        ]
    
    @staticmethod
    def get_by_internal(internal: str) -> str:
        return next(filter(lambda x : x[2] == internal, RelicTypes.get()), None)[1]
    
    @staticmethod
    def get_id_by_list_internal(internal: List[str]) -> List[int]:
        return map(lambda x : x[0], filter(lambda x : x[2] in internal, RelicTypes.get()))
    
class FactionTypes():
    @staticmethod
    def get() -> List[Tuple[int, str]]:
        return [
            (0, "Greneer"),
            (1, "Corpus"),
            (2, "Infestation"),
            (3, "Orokin"),
            (7, "The Murmur")
        ]
    
    @staticmethod
    def get_by_index(index: str) -> str:
        return next(filter(lambda x : x[0] == index, FactionTypes.get()), None)[1]
    
    @staticmethod
    def get_id_by_list_internal(internal: List[str]) -> List[int]:
        return map(lambda x : x[0], filter(lambda x : x[1] in internal, FactionTypes.get()))
    
    
class PolarityTypes():
    @staticmethod
    def get() -> List[Tuple[str, str]]:
        return [
            ('AP_ANY', '<:anypolarity:1246452363905204324>'),
            ('AP_UMBRA', '<:umbra:1246452305184948305>'),
            ('AP_UNIVERSAL', '<:anypolarity:1246452363905204324>'),
            ('AP_PRECEPT', '<:penjaga:1246452231813730446>'),
            ('AP_ATTACK', '<:madurai:1246451686046826569>'),
            ('AP_WARD', '<:unairu:1246452164704862288>'),
            ('AP_DEFENSE', '<:vazarin:1246451970860908646>'),
            ('AP_TACTIC', '<:naramon:1246452050154491974>'),
            ('AP_POWER', '<:zenurik:1246452097059127447>')
        ]
    
    @staticmethod
    def replaceWithEmoji(string: str) -> str:
        pattern = '|'.join(sorted(re.escape(item[0]) for item in PolarityTypes.get()))
        return re.sub(pattern, lambda m: PolarityTypes.get_emoji_by_internal(m.group(0).upper()) + " ", string, flags=re.IGNORECASE)
    
    @staticmethod
    def get_emoji_by_internal(internal: str) -> str:
        return next(filter(lambda x : x[0] == internal, PolarityTypes.get()), None)[1]
    
class ConverterDB:
    
    @staticmethod
    def convert_to_dbfilter(reliq: List[str], faction: List[str], mission: List[str], sp: List[str]) -> int:
        return WarframeDB.get_filter_number(
            set(RelicTypes.get_id_by_list_internal(reliq)) |
            set(map(lambda x : x + 10, FactionTypes.get_id_by_list_internal(faction))) |
            set(map(lambda x : x + 20, MissionTypes.get_id_by_list_internal(mission))) |
            set(map(lambda x : bool(x) + 60, sp))
        )