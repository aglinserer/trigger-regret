import argparse
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from typing import List


URL = "https://ubuntu-archive-team.ubuntu.com/proposed-migration/{}/update_excuses.html"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("dist", type=str, help="The distribution to check for")
    parser.add_argument("pkg", type=str, help="The package name to retrigger")

    return parser.parse_args()


def fetch_page(dist) -> str:
    url = URL.format(dist)
    html_content = None

    # fetch the page
    try:
        print(f"Fetching from URL: {url}")
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        html_content = response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")

    return html_content


def parse_page(page_content: str, pkg: str) -> List[str]:
    soup = BeautifulSoup(page_content, "lxml")
    all_lis = soup.body.ul.find_all("li", recursive=False)
    print(f"Total <li> elements found: {len(all_lis)}\n")

    link_list = []

    for li in all_lis:
        a_element = li.find("a", id=pkg)
        if not a_element:
            continue

        print(a_element)
        sub_uls = list(li.find_all("li"))
        for sub in sub_uls:
            if not sub.text.startswith("autopkgtest"):
                continue
            hrefs = sub.find_all("a", style="text-decoration: none;")
            for link in hrefs:
                link_list.append(link.get("href"))
    return link_list


def send_triggers(link_list: List[str]) -> List[str]:
    # read the cookie and session
    cookie_path = Path("~/.cache/autopkgtest.cookie").expanduser()
    with open(cookie_path, encoding="utf-8") as fil:
        cookie_file = fil.readlines()

    # extract the two required fields from the cookie
    cookies = {l.split()[5]: l.split()[6] for l in cookie_file}
    # retrigger all of those
    ret = ""
    for url in link_list:
        req_ret = requests.get(url, cookies=cookies, timeout=5)
        ret += f"{req_ret.status_code} - {url}\n"
    return ret


def main(dist: str, pkg: str):
    page_content = fetch_page(dist)
    link_list = parse_page(page_content, pkg)
    # have to use lxml because the side is not fully
    # valid with missing closing tags
    print("Extracted following links:")
    print("\n".join(link_list))
    print("Starting triggering:")
    ret = send_triggers(link_list)
    print(ret)


if __name__ == "__main__":
    args = parse_args()
    main(args.dist, args.pkg)
