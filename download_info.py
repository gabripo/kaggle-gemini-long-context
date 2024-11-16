from crawler import get_text_from_webpages
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


if __name__ == "__main__":
    infoDict = download_info_companies(companiesWebsites=companiesWebsites)
