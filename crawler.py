import json
import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
from collections import deque
import hashlib

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


def generate_filename_from_url(url: str, pageMarker: str) -> str:
    return f"{pageMarker}_{hashlib.sha1(url.encode('UTF8')).hexdigest()}"


def download_page(soup: BeautifulSoup, url: str, filePath: str) -> None:
    """
    Function to download a page
    """
    paragraphsList = [p.get_text() for p in soup.find_all("p")]
    pageTitle = [t.get_text() for t in soup.find_all("title")]
    if paragraphsList:
        siteData = {"title": pageTitle, "url": url, "content": paragraphsList}

        write_json_from_data(siteData, filePath)
        print(f"JSON file {filePath} created from url {url}")


def write_json_from_data(data: dict, filePath: str, indentSize: int = 4) -> None:
    """
    Function to write a json file with its data
    """
    with open(filePath, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=indentSize)
    return


def download_all_pages(
    rootUrl: str,
    parentFolder: str,
    savePath: str,
    maxPages: int = 100,
    pageMarker: str = "site",
    pagenamesToExclude: list[str] = [],
    freshDownload: bool = False,
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

        filename = generate_filename_from_url(url, pageMarker)
        jsonFiles.append(filename)

        filePath = os.path.join(savePath, filename + ".json")
        fileLinksPath = os.path.join(savePath, filename + "_links.json")
        if freshDownload or (
            not os.path.exists(filePath) and not os.path.exists(fileLinksPath)
        ):
            soup = soup_page(url)
            download_page(soup, url, filePath)

            links = get_links(soup, url, parentFolder)
            write_json_from_data(links, fileLinksPath)
        else:
            print(f"File {filePath} related to url {url} already available!\n")
            with open(fileLinksPath, "r") as f:
                links = json.load(f)

        pagesNotAllowed = set(pagenamesToExclude)
        for link in links:
            if set(link.split("/")).intersection(pagesNotAllowed):
                continue

            fullLink = urljoin(url, link)
            if fullLink not in visitedUrls and "http" in fullLink:
                stack.append(fullLink)

    return jsonFiles


def most_common_sentences_in_file(
    jsonFilePath: str, alreadyCommonWords: set = set(), frequencyThreshold: int = 1
) -> list[str]:
    with open(jsonFilePath, "r") as f:
        data = json.load(f)

    if type(data) == list:
        contentList = [c.get("content", "") for c in data]
        content = []
        for contentPage in contentList:
            content.extend(contentPage)
    else:
        content = data.get("content", "")

    frequencies = {}
    if content:
        for sentence in content:
            frequencies[sentence] = frequencies.get(sentence, 0) + 1

    for sentence, freq in frequencies.items():
        if freq > frequencyThreshold:
            alreadyCommonWords.add(sentence)
    return alreadyCommonWords


def list_json_files_in_folder(
    jsonFilesFolder: str, jsonFilesToExclude: str | list[str], pageMarker="site"
) -> list[str]:
    if type(jsonFilesToExclude) == str:
        jsonFilesToExclude = [jsonFilesToExclude]

    filesToExclude = set(jsonFilesToExclude)
    fileList = [
        os.path.join(jsonFilesFolder, file)
        for file in os.listdir(jsonFilesFolder)
        if file.endswith(".json")
        and file not in filesToExclude
        and pageMarker in file
        and not "_links.json" in file
    ]
    return fileList


def clean_json_file(
    jsonFilePath: str, mostCommonRows: set[str] = set(), overwrite: bool = True
) -> str:
    with open(jsonFilePath, "r") as f:
        data = json.load(f)

    if type(data) == list:
        for i, page in enumerate(data):
            indexesToRemove = set()
            for j, row in enumerate(page.get("content", "")):
                if row in mostCommonRows:
                    indexesToRemove.add(j)

            data[i]["content"][:] = [
                c for k, c in enumerate(data[i]["content"]) if not k in indexesToRemove
            ]
    else:
        indexesToRemove = set()
        for i, row in enumerate(data.get("content", "")):
            if row in mostCommonRows:
                indexesToRemove.add(i)

        data["content"][:] = [
            c for k, c in enumerate(data["content"]) if k not in indexesToRemove
        ]

    if overwrite:
        jsonCleanedFilePath = jsonFilePath
    else:
        jsonCleanedFilePath = jsonFilePath.replace(".json", "_cleaned.json")

    write_json_from_data(data, jsonCleanedFilePath)
    return jsonCleanedFilePath


def clean_json_files(
    jsonFilesFolder: str,
    filesToExclude: str | list[str],
    pageMarker="site",
    overwrite: bool = True,
) -> list[str]:
    """
    Function to remove unneded text from a json file containing web page content
    """
    fileList = list_json_files_in_folder(jsonFilesFolder, filesToExclude, pageMarker)

    mostCommonRows = set()  # it is possible to define custom common words here
    for file in fileList:
        mostCommonRows = most_common_sentences_in_file(file, mostCommonRows)

    cleanedFiles = []
    for file in fileList:
        jsonCleanedFilePath = clean_json_file(file, mostCommonRows, overwrite)
        cleanedFiles.append(jsonCleanedFilePath)
    return cleanedFiles


def merge_json_files(
    jsonFilesFolder: str,
    targetFile: str = "_merged.json",
    pageMarker="site",
    jsonFiles: list[str] = [],
) -> str:
    """
    Function to merge multiple json files into a single one
    """
    fileList = list_json_files_in_folder(jsonFilesFolder, targetFile, pageMarker)
    jsonFilesAllowed = set(jsonFiles)
    if fileList:
        resultFileContent = []
        for file in fileList:
            if file in jsonFilesAllowed:
                with open(file, "r") as f:
                    jsonData = json.load(f)
                    resultFileContent.append(jsonData)

        resultFilePath = os.path.join(jsonFilesFolder, targetFile)
        write_json_from_data(resultFileContent, resultFilePath)
        return resultFilePath
    return ""


def json_to_txt(savePath: str, jsonFilePath: str, targetName: str = "") -> str:
    if targetName == "":
        targetName = os.path.basename(jsonFilePath).replace(".json", ".txt")
    elif not ".txt" in targetName:
        targetName = targetName + "_merged.txt"

    with open(jsonFilePath, "r") as f:
        data = json.load(f)

    resultFilePath = os.path.join(savePath, targetName)
    with open(resultFilePath, "w") as f:
        for numPage, webpage in enumerate(data):
            pageTitle = webpage.get("title", "")
            pageUrl = webpage.get("url", "")
            f.write(
                f'The page with name "{pageTitle[0]}" and URL "{pageUrl}" has the following content:\n'
            )

            pageContent = webpage.get("content", "")
            for row in pageContent:
                f.write(f"{row} \n")

            f.write(
                f'The page with name "{pageTitle[0]}" and URL "{pageUrl}" ends here.\n\n'
            )

    return resultFilePath


def text_from_file(filePath: str) -> str | list[str]:
    with open(filePath, "r", encoding="utf-8") as f:
        textString = f.read()
        f.seek(0)
        textList = f.readlines()
    return textString, textList


def get_text_from_webpages(
    root: str,
    parentFolder: str,
    savePath: str = "crawled",
    numPages: int = 5,
    pageMarker: str = "site",
    pagenamesToExclude: list[str] = [],
    freshDownload: bool = False,
) -> str:
    os.makedirs(savePath, exist_ok=True)

    jsonFiles = download_all_pages(
        root,
        parentFolder,
        savePath,
        numPages,
        pageMarker,
        pagenamesToExclude,
        freshDownload,
    )

    mergedJsonName = pageMarker + "_merged.json"
    jsonFilesClean = clean_json_files(savePath, mergedJsonName, pageMarker)
    mergedJsonPath = merge_json_files(savePath, mergedJsonName, pageMarker, jsonFiles)

    mostCommonWordsMergedJson = most_common_sentences_in_file(
        mergedJsonPath, frequencyThreshold=(len(jsonFilesClean) - 1) // 2 + 1
    )
    mergedJsonPath = clean_json_file(mergedJsonPath, mostCommonWordsMergedJson)

    plainTextFile = json_to_txt(savePath, mergedJsonPath)
    plainText, textString = text_from_file(plainTextFile)
    return plainText


if __name__ == "__main__":
    parent_folder = "/products-and-solutions/"
    initial_url = "https://www.hitachienergy.com/products-and-solutions/"
    save_folder = "crawled"
    num_pages_to_download = 5
    parsedText = get_text_from_webpages(
        initial_url, parent_folder, save_folder, num_pages_to_download
    )
    print(parsedText)
