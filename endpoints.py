import requests

def get_endpoints():
    response = requests.get('http://content.warframe.com/PublicExport/index_en.txt.lzma')
    data = response.content
    with open("index_en.txt.lzma", "wb") as f:
        f.write(data)
    import subprocess
    index = subprocess.getoutput("xz --format=lzma -d index_en.txt.lzma -c; rm index_en.txt.lzma")


    endpoints = {}
    
    for line in index.splitlines():
        endpoints[line.split('.')[0]] = 'Manifest/' + line

    return endpoints

if __name__ == "__main__":
    import json
    endpoints = get_endpoints()
    print(json.dumps(endpoints, indent=2))
    for endpoint in endpoints:
        with open(f"{endpoint}.json", "wb") as f:
            f.write(requests.get(f'http://content.warframe.com/PublicExport/{endpoints[endpoint]}').content)