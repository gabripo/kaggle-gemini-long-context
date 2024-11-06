import json
import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
from collections import deque

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


def download_all_pages(
    rootUrl: str, parentFolder: str, savePath: str, maxPages: int = 100
) -> list[str]:
    """
    Recursive function to download pages and subpages
    """
    visitedUrls = set()
    stack = deque([rootUrl])

    jsonFiles = []
    while stack and len(jsonFiles) < maxPages:
        url = stack.pop()

        if url in visitedUrls:
            continue
        visitedUrls.add(url)

        soup = soup_page(url)
        jsonFileFromSite = download_page(soup, url, savePath)
        print(f"JSON file {jsonFileFromSite} created from url {url}")
        jsonFiles.append(jsonFileFromSite)

        links = get_links(soup, url, parentFolder)
        for link in links:
            fullLink = urljoin(url, link)
            if fullLink not in visitedUrls and "http" in fullLink:
                stack.append(fullLink)

    return jsonFiles


def clean_json_files(jsonFilesFolder: str, overwrite: bool = True) -> str:
    """
    Function to remove unneded text from a json file containing web page content
    """
    pass


def merge_json_files(jsonFilesFolder: str, targetFile: str = "_merged.json") -> str:
    """
    Function to merge multiple json files into a single one
    """
    fileList = [
        os.path.join(jsonFilesFolder, file)
        for file in os.listdir(jsonFilesFolder)
        if file.endswith(".json") and file != targetFile
    ]
    if fileList:
        resultFileContent = []
        for file in fileList:
            with open(file, "r") as f:
                jsonData = json.load(f)
                resultFileContent.append(jsonData)

        resultFilePath = os.path.join(jsonFilesFolder, targetFile)
        with open(resultFilePath, "w") as f:
            json.dump(resultFileContent, f, indent=2)
        return resultFilePath
    return ""


def crawling_hard(root: str, parentFolder: str, savePath: str = "crawled") -> None:
    os.makedirs(savePath, exist_ok=True)

    jsonFiles = download_all_pages(root, parentFolder, savePath, 10)

    clean_json_files(savePath)

    mergedJsonName = "_merged.json"
    mergedJsonPath = merge_json_files(savePath, mergedJsonName)
    return


parent_folder = "/products-and-solutions/"
initial_url = "https://www.hitachienergy.com/products-and-solutions/"
save_folder = "crawled"
crawling_hard(initial_url, parent_folder, save_folder)
