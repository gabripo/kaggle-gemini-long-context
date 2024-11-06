import json
import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin

VALID_GET_RESPONSE = 200


def soup_page(url: str) -> BeautifulSoup:
    """
    Function to make a HTTP request by a given url
    """
    response = requests.get(url)
    if response.status_code == VALID_GET_RESPONSE:
        soup = BeautifulSoup(response.text, "html.parser")
    else:
        soup = BeautifulSoup("")
    return soup


def get_links(soup: BeautifulSoup, url: str, parentFolder: str) -> list:
    """
    Function to get all links from a page
    """
    links = [
        a["href"] for a in soup.find_all("a", href=True) if parentFolder in a["href"]
    ]
    return links


def download_page(soup: BeautifulSoup, url: str, savePath: str) -> str:
    """
    Function to download a page
    """
    paragraphs = soup.find_all("p")
    if paragraphs:
        paragraphsList = [p.get_text() for p in paragraphs]
        siteData = {"url": url, "content": paragraphsList}

        urlPath = url.replace("https://", "").replace("http://", "").replace("/", "_")
        filePath = os.path.join(savePath, urlPath + ".json")
        write_json_from_site_data(siteData, filePath)
        return filePath
    else:
        return ""


def write_json_from_site_data(siteData: dict, filePath: str) -> None:
    """
    Function to write a json file containing data from a website
    """
    with open(filePath, "w") as f:
        json.dump(siteData, f, ensure_ascii=False, indent=4)
    return


def download_all_pages(url: str, parentFolder: str, savePath: str, visited=None):
    """
    Recursive function to download pages and subpages
    """
    if visited is None:
        visited = set()
    if url in visited:
        return
    visited.add(url)

    soup = soup_page(url)
    jsonFileFromSite = download_page(soup, url, savePath)
    print(f"JSON file {jsonFileFromSite} created from url {url}")

    links = get_links(soup, url, parentFolder)
    for link in links:
        full_link = urljoin(url, link)
        if full_link not in visited and "http" in full_link:
            download_all_pages(full_link, parent_folder, savePath, visited)
            # TODO make it iterative (DFS)


def crawling_hard(root: str, parentFolder: str, savePath: str = "crawled") -> None:
    os.makedirs(savePath, exist_ok=True)

    download_all_pages(root, parent_folder, savePath)
    return


parent_folder = "/products-and-solutions/"
initial_url = "https://www.hitachienergy.com/products-and-solutions/"
crawling_hard(initial_url, parent_folder)
