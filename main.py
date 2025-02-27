from src.company_info_downloader import download_info_companies, read_companies_info
from src.crawler import write_json_from_data


companiesWebsites = {
    "DUAGON": [
        "https://www.duagon.com/products/",
        "/products/",
    ],
}

if __name__ == "__main__":
    infoDict = download_info_companies(
        companiesWebsites=companiesWebsites, numPagesToDownload=500, method="functional"
    )

    resultFileName = "companies_info.json"
    write_json_from_data(infoDict, resultFileName)

    data = read_companies_info(
        resultFileName
    )  # testing the function, returning nothing
