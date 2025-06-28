#!python

import asyncio
import sys
from pathlib import Path

import httpx
from bs4 import BeautifulSoup


def find_links(path):
    html_content = Path(path).read_text()
    soup = BeautifulSoup(html_content, "html.parser")
    links = soup.find_all("a", href=True)
    return [
        link["href"]
        for link in links
        if link["href"].startswith("http")
        and "localhost" not in link["href"]
        and "127.0.0.1" not in link["href"]
    ]


async def check_url(url, client):
    print(f"Checking {url}")
    try:
        await client.head(url, follow_redirects=True, timeout=5)
    except httpx.RequestError as e:
        print(f"Link {url} errored {e}")
        return False
    except httpx.HTTPStatusError as e:
        print(f"Link {url} errored {e.response.status_code}")
        return False
    return True


async def main(path):
    links = find_links(path)
    async with httpx.AsyncClient() as client:
        tasks = [check_url(link, client) for link in links]
        results = await asyncio.gather(*tasks)
    success_count = sum(results)
    failure_count = len(links) - success_count
    print(
        f"Checked {len(links)} links, {success_count} succeeded, {failure_count} failed."
    )
    if failure_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "book.html"
    asyncio.run(main(path))
