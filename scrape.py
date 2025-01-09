import requests
import re
import networkx as nx
import sys

class Link:
    def __init__(self, url):
        self.url = url
        self.scanned = False

    def __str__(self):
        return self.url

    def __hash__(self):
        return hash(self.url)

    def __eq__(self, other):
        return self.url == other.url

def get_links(url):
    try:
        response = requests.get(f'https://{url}', timeout=5)
    except requests.exceptions.RequestException as e:
        print("Failed to scan", url)
        return set()
    raw_links = re.findall(r'href=[\'"]?([^\'" >]+)', response.text)
    #print(raw_links)
    links = set()
    for link in raw_links:
        splink = link.split('/')
        if len(splink) < 3:
            continue
        elif splink[0][:4] != 'http':
            continue
        elif splink[2] == url:
            continue
        elif len(splink) > 3 and re.match("(next|previous)\?host", splink[3]):
            try:
                links.add(requests.get(link, allow_redirects=True).url.split('/')[2])
            except requests.exceptions.RequestException as e:
                pass
        elif any([re.search(b, splink[2]) for b in blacklist]):
            continue
        links.add(splink[2])
    return links

with open('blacklist.txt', 'r') as f:
    blacklist = f.read().splitlines()

if __name__ == '__main__':
    #print(get_links('grace.pink'))
    if not len(sys.argv) == 2:
        print("Usage: python scrape.py <iterations>")
        sys.exit(1)
    DG = nx.DiGraph()
    queue = [Link('grace.pink')]
    for i in range(int(sys.argv[1])):
        link = queue.pop(0)
        print("Scanning:", link.url)
        if not link.scanned:
            link.scanned = True
            DG.add_node(link)
            try:
                links = get_links(link.url)
            except:
                print("Failed to scan", link.url)
                continue
            for l in links:
                if DG.has_node(Link(l)):
                    DG.add_edge(link, Link(l))
                else:
                    queue.append(Link(l))
                    DG.add_edge(link, Link(l))
    print("Nodes:")
    [print(str(n)) for n in DG.nodes]
    
    nx.write_graphml(DG, 'graph.graphml')

