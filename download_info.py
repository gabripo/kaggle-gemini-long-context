import json
from crawler import get_text_from_webpages, write_json_from_data
import os

companiesWebsites = {
    "SIEMENS": [
        "https://www.siemens-energy.com/us/en/home/products-services.html",
        "/products-services/",
    ],
    "HITACHI": [
        "https://www.hitachienergy.com/products-and-solutions/",
        "/products-and-solutions/",
    ],
}


def download_info_companies(
    companiesWebsites: str, numPagesToDownload: int = 10
) -> dict[str, str]:
    saveFolder = os.path.join(os.path.dirname(__file__), "companies_info")
    companiesInfoText = {}
    for companyName, companyWebInfo in companiesWebsites.items():
        print(f"Downloading webpages for company named {companyName}")
        companyWebsite = companyWebInfo[0]
        companyParentFolder = companyWebInfo[1]

        companyInfoText = get_text_from_webpages(
            root=companyWebsite,
            parentFolder=companyParentFolder,
            savePath=saveFolder,
            numPages=numPagesToDownload,
            pageMarker=companyName,
        )

        companiesInfoText[companyName] = companyInfoText

    return companiesInfoText


def read_companies_info(jsonFilePath: str) -> dict:
    """
    function to load a json file - to be copied onto Kaggle, reference the correct .json file containing the companies info
    """
    with open(jsonFilePath, "r") as f:
        data = json.load(f)
    return data


if __name__ == "__main__":
    infoDict = download_info_companies(companiesWebsites=companiesWebsites)

    resultFileName = "companies_info.json"
    write_json_from_data(infoDict, resultFileName)

    data = read_companies_info(
        resultFileName
    )  # testing the function, returning nothing
