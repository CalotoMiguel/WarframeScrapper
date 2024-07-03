import io
from typing import Any, List, Optional, Tuple, Dict
import requests
import json
from collections import Counter
import time

from warframeInternalMapper import *
from PIL import Image, ImageDraw

class Warframe:
    @staticmethod
    def getImage(uniqueName: str, session: requests.Session = None, manifest: List[Dict] = None) -> io.BytesIO:
        if session is None:
            session = requests.Session()
        url = 'https://content.warframe.com/PublicExport/'
        URLImage = WarframeDB.get_location(uniqueName)
        response = session.get(url[:-1] + URLImage, stream=True)
        return io.BytesIO(response.raw.read())

    @staticmethod
    def getWeapons() -> List[Dict]:
        endpoint = WarframeDB.get_endpoint("ExportWeapons_en")
        url = 'https://content.warframe.com/PublicExport/'
        response = requests.get(url + endpoint)
        return json.loads(response.content, strict=False)["ExportWeapons"]

    @staticmethod
    def getManifest() -> List[Dict]:
        endpoint = WarframeDB.get_endpoint("ExportManifest")
        url = 'https://content.warframe.com/PublicExport/'
        response = requests.get(url + endpoint)
        return json.loads(response.content, strict=False)["Manifest"]

    @staticmethod
    def getWeaponNames() -> List[str]:
        endpoint = WarframeDB.get_endpoint("ExportWeapons_en")
        url = 'https://content.warframe.com/PublicExport/'
        response = requests.get(url + endpoint)
        response = json.loads(response.content, strict=False)
        return list(map(lambda a : a["name"], response["ExportWeapons"]))
    
    @staticmethod
    def getWeaponByName(name: str) -> Optional[Dict]:
        endpoint = WarframeDB.get_endpoint("ExportWeapons_en")
        url = 'https://content.warframe.com/PublicExport/'
        response = requests.get(url + endpoint)
        response = json.loads(response.content, strict=False)
        return next(filter(lambda a : a["name"] == name, response["ExportWeapons"]), None)
    
    @staticmethod
    def getNodes() -> List[Dict]:
        endpoint = WarframeDB.get_endpoint("ExportRegions_en")
        url = 'https://content.warframe.com/PublicExport/'
        response = requests.get(url + endpoint)
        response = json.loads(response.content, strict=False)
        return response["ExportRegions"]
    
    @staticmethod
    def getFisures() -> List[Dict]:
        nodes = Warframe.getNodes()
        def is_active(mission: Dict) -> bool:
            now = time.time()
            return True if mission['Activation'] < now < mission['Expiry'] else False

        def mission_formatter(mission: Dict) -> Dict:
            mission['Activation'] = int(mission['Activation']['$date']['$numberLong'][:-3])
            mission['Expiry'] = int(mission['Expiry']['$date']['$numberLong'][:-3])
            return mission

        def add_node_info(fisure: Dict) -> Dict:
            node = next(filter(lambda x : x['uniqueName'] == fisure['Node'], nodes), None)
            fisure['name'] = node['name']
            fisure['systemName'] = node['systemName']
            fisure['faction'] = FactionTypes.get_by_index(node['factionIndex'])
            if 'Hard' not in fisure:
                fisure['Hard'] = False
            return fisure
        
        url = 'https://content.warframe.com/dynamic/worldState.php'
        response = requests.get(url)
        response = json.loads(response.content, strict=False)
        active_missions = map(mission_formatter, response["ActiveMissions"])
        return list(map(add_node_info, filter(is_active, active_missions)))
    
    @staticmethod
    def getCustoms() -> Dict:
        endpoint = WarframeDB.get_endpoint("ExportCustoms_en")
        url = 'https://content.warframe.com/PublicExport/'
        response = requests.get(url + endpoint)
        return json.loads(response.content, strict=False)["ExportCustoms"]
    
    @staticmethod
    def getResources() -> Dict:
        endpoint = WarframeDB.get_endpoint("ExportResources_en")
        url = 'https://content.warframe.com/PublicExport/'
        response = requests.get(url + endpoint)
        return json.loads(response.content, strict=False)["ExportResources"]
    
    @staticmethod
    def getMods() -> List[Dict]:
        endpoint = WarframeDB.get_endpoint("ExportUpgrades_en")
        url = 'https://content.warframe.com/PublicExport/'
        response = requests.get(url + endpoint)
        return json.loads(response.content, strict=False)["ExportUpgrades"]
    
    @staticmethod
    def getModNames() -> List[str]:
        endpoint = WarframeDB.get_endpoint("ExportUpgrades_en")
        url = 'https://content.warframe.com/PublicExport/'
        response = requests.get(url + endpoint)
        response = json.loads(response.content, strict=False)
        return list(map(lambda a : a["name"], response["ExportUpgrades"]))
    
    
    @staticmethod
    def getModByName(name: str) -> Optional[Dict]:
        endpoint = WarframeDB.get_endpoint("ExportUpgrades_en")
        url = 'https://content.warframe.com/PublicExport/'
        response = requests.get(url + endpoint)
        response = json.loads(response.content, strict=False)
        return next(filter(lambda a : a["name"] == name, response["ExportUpgrades"]), None)
    
    @staticmethod
    def getShotgunRiven() -> Dict:
        endpoint = WarframeDB.get_endpoint("ExportUpgrades_en")
        url = 'https://content.warframe.com/PublicExport/'
        response = requests.get(url + endpoint)
        response = json.loads(response.content, strict=False)
        response = next(filter(lambda x : x["uniqueName"] == "/Lotus/Upgrades/Mods/Randomized/LotusShotgunRandomModRare", response["ExportUpgrades"]))["upgradeEntries"]
        aux = {}
        for x in response:
            aux[x["tag"]] = x["upgradeValues"][0]
        return aux
    
    @staticmethod
    def getRifleRiven() -> Dict:
        endpoint = WarframeDB.get_endpoint("ExportUpgrades_en")
        url = 'https://content.warframe.com/PublicExport/'
        response = requests.get(url + endpoint)
        response = json.loads(response.content, strict=False)
        response = next(filter(lambda x : x["uniqueName"] == "/Lotus/Upgrades/Mods/Randomized/LotusRifleRandomModRare", response["ExportUpgrades"]))["upgradeEntries"]
        aux = {}
        for x in response:
            aux[x["tag"]] = x["upgradeValues"][0]
        return aux
    
    @staticmethod
    def getPistolRiven() -> Dict:
        endpoint = WarframeDB.get_endpoint("ExportUpgrades_en")
        url = 'https://content.warframe.com/PublicExport/'
        response = requests.get(url + endpoint)
        response = json.loads(response.content, strict=False)
        response = next(filter(lambda x : x["uniqueName"] == "/Lotus/Upgrades/Mods/Randomized/LotusPistolRandomModRare", response["ExportUpgrades"]))["upgradeEntries"]
        aux = {}
        for x in response:
            aux[x["tag"]] = x["upgradeValues"][0]
        return aux
    
    @staticmethod
    def getMeleeRiven() -> Dict:
        endpoint = WarframeDB.get_endpoint("ExportUpgrades_en")
        url = 'https://content.warframe.com/PublicExport/'
        response = requests.get(url + endpoint)
        response = json.loads(response.content, strict=False)
        response = next(filter(lambda x : x["uniqueName"] == "/Lotus/Upgrades/Mods/Randomized/PlayerMeleeWeaponRandomModRare", response["ExportUpgrades"]))["upgradeEntries"]
        aux = {}
        for x in response:
            aux[x["tag"]] = x["upgradeValues"][0]
        return aux
    
    @staticmethod
    def getArchGunRiven() -> Dict:
        endpoint = WarframeDB.get_endpoint("ExportUpgrades_en")
        url = 'https://content.warframe.com/PublicExport/'
        response = requests.get(url + endpoint)
        response = json.loads(response.content, strict=False)
        response = next(filter(lambda x : x["uniqueName"] == "/Lotus/Upgrades/Mods/Randomized/LotusArchgunRandomModRare", response["ExportUpgrades"]))["upgradeEntries"]
        aux = {}
        for x in response:
            aux[x["tag"]] = x["upgradeValues"][0]
        return aux
    
    @staticmethod
    def getBaro() -> Dict:
        url = 'https://content.warframe.com/dynamic/worldState.php'
        response = requests.get(url)
        response = json.loads(response.content, strict=False)
        return response["VoidTraders"][0]
    
    @staticmethod
    def getRecipes() -> Dict:
        endpoint = WarframeDB.get_endpoint("ExportRecipes_en")
        url = 'https://content.warframe.com/PublicExport/'
        response = requests.get(url + endpoint)
        response = json.loads(response.content, strict=False)
        return response["ExportRecipes"]
    
    @staticmethod
    def getRecipe(internal: str, name: str) -> Tuple[Counter, Image.Image]:
        recipes = Warframe.getRecipes()
        tree, image = Warframe.__getRecipeRec(internal, name, 1, recipes, requests.Session())
        
        buf = io.BytesIO()
        image.save(buf, format='PNG', save_all=True)
        buf.seek(0)
        return tree, buf
    
    @staticmethod
    def __getRecipeRec(internal: str, name: str, count:int, recipes: List[Dict], session: requests.Session) -> Tuple[Counter, Image.Image]:
        craft = next(filter(lambda a : a["resultType"] == internal, recipes), None)
        text = f"{name} ({count})" if count > 1 else name
        if craft is None:
            return (Counter({name : count}), Warframe.__put_text(Image.open(Warframe.getImage(internal, session)).convert("RGBA"), text))
        
        ingredients = Counter({name + " Blueprint" : count})
        images = [Warframe.__put_text(Image.open(Warframe.getImage(craft["uniqueName"], session)).convert("RGBA"), name + " Blueprint")]
        for item in craft['ingredients']:
            name_item = WarframeDB.get_name(item['ItemType'])
            item_craft, image = Warframe.__getRecipeRec(item['ItemType'], name_item, item["ItemCount"], recipes, session)
            if item_craft:
                ingredients = ingredients + item_craft
            images.append(image)
        combined_image = Warframe.__append_images(images)
        image = Warframe.__put_text(Image.open(Warframe.getImage(internal, session)).convert("RGBA"), text)
        final_image = Warframe.__append_images([image, combined_image], direction="vertical")
        return (ingredients, final_image)
    
    @staticmethod
    def __append_images(images, direction='horizontal'):
        widths, heights = zip(*(i.size for i in images))

        if direction=='horizontal':
            new_width = sum(widths)
            new_height = max(heights)
        else:
            new_width = max(widths)
            new_height = sum(heights)

        new_im = Image.new('RGBA', (new_width, new_height), color=None)


        offset = 0
        for im in images:
            if direction=='horizontal':
                draw = ImageDraw.Draw(im)
                draw.line(((im.size[0]/2, 0), (im.size[0]/2, 45)), fill=(225,225,225,225), width=5)
                if offset == 0:
                    draw.line(((im.size[0]/2, 0), (im.size[0], 0)), fill=(225,225,225,225), width=8)
                elif offset + im.size[0] == new_im.size[0]:
                    draw.line(((0, 0), (im.size[0]/2, 0)), fill=(225,225,225,225), width=8)
                else:
                    draw.line(((0, 0), (im.size[0], 0)), fill=(225,225,225,225), width=8)
                new_im.paste(im, (offset, 0))
                offset += im.size[0]
            else:
                if offset == 0:
                    draw = ImageDraw.Draw(im)
                    draw.line(((im.size[0]/2, im.size[1]), (im.size[0]/2, im.size[1] - 30)), fill=(225,225,225,225), width=5)
                x = int((new_width - im.size[0])/2)
                new_im.paste(im, (x, offset))
                offset += im.size[1]
        
        return new_im

    @staticmethod
    def __put_text(image, message):
        W, H = image.size
        draw = ImageDraw.Draw(image)
        _, _, w, h = draw.textbbox((0, 0), message, font_size=35)
        draw.text(((W-w)/2, H-h-45), message, font_size=35)
        return image
    
    @staticmethod
    def getCetusTimeCycle() -> int:
        url = 'https://content.warframe.com/dynamic/worldState.php'
        response = requests.get(url)
        response = json.loads(response.content, strict=False)
        return int(next(filter(lambda x : x["Tag"] == "CetusSyndicate", response["SyndicateMissions"]), None)['Expiry']['$date']['$numberLong'][:-3])