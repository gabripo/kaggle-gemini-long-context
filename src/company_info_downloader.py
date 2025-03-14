import json
import os
from src.crawler import get_text_from_webpages
from src.crawler_oop import WebCrawler


def download_info_companies(
    companiesWebsites: str, numPagesToDownload: int = 10, method="OOP"
) -> dict[str, str]:
    saveFolder = os.path.join(os.path.dirname(__file__), "companies_info")
    companiesInfoText = {}
    for companyName, companyWebInfo in companiesWebsites.items():
        print(f"Downloading webpages for company named {companyName}")
        companyWebsite = companyWebInfo[0]
        companyParentFolder = companyWebInfo[1]

        if method == "functional":
            companyInfoText = get_text_from_webpages(
                root=companyWebsite,
                parentFolder=companyParentFolder,
                savePath=saveFolder,
                numPages=numPagesToDownload,
                pageMarker=companyName,
                pagenamesToExclude=["contact-us"],
                baseurlsToExclude=["qnx", "blackberry"],
            )
        elif method == "OOP":
            crawler = WebCrawler(
                root=companyWebsite,
                parent_folder=companyParentFolder,
                save_path=saveFolder,
                max_pages=numPagesToDownload,
                page_marker=companyName,
                pagenames_to_exclude=["contact-us"],
                baseurls_to_exclude=["qnx", "blackberry"],
            )
            crawler.get_text_from_webpages()
            companyInfoText = crawler.text_from_file
        else:
            print(
                f"Unrecognized crawling method {method} ! Returning empty string for {companyName}"
            )
            companiesInfoText = ""

        companiesInfoText[companyName] = companyInfoText

    return companiesInfoText


def read_companies_info(jsonFilePath: str) -> dict:
    """
    function to load a json file - to be copied onto Kaggle, reference the correct .json file containing the companies info
    """
    with open(jsonFilePath, "r") as f:
        data = json.load(f)
    return data
