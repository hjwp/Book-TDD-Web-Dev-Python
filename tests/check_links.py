from lxml import html
import requests

with open('book.html') as f:
    node = html.fromstring(f.read())

all_hrefs = [e.get('href') for e in node.cssselect('a')]
urls = [l for l in all_hrefs if l and l.startswith('h')]

for l in urls:
    try:
        response = requests.get(l)
        if response.status_code != 200:
            print(l)
        else:
            print('.', end="", flush=True)
    except requests.RequestException:
        print(l)

