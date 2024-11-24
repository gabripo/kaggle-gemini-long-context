import os
import requests

GITHUB_API_URL = "https://api.github.com/repos"


def files_info_from_github_repo_folder(
    username: str = "gabripo",
    repo: str = "kaggle-gemini-long-context",
    folderName: str = "",
):
    url = f"{GITHUB_API_URL}/{username}/{repo}/contents/{folderName}"
    headers = {"Accept": "application/vnd.github.v3+json"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Ensure we notice bad responses

    return response.json()


def download_file_from_url(fileUrl, savePath):
    response = requests.get(fileUrl)
    response.raise_for_status()

    with open(savePath, "wb") as file:
        file.write(response.content)


def download_files_from_github_repo(
    userName: str = "gabripo",
    repo: str = "kaggle-gemini-long-context",
    folderName: str = "",
    saveFolder: str = "downloaded",
    extension: str = "pdf",
):
    os.makedirs(saveFolder, exist_ok=True)

    filesInfo = files_info_from_github_repo_folder(userName, repo, folderName)
    for fileInfo in filesInfo:
        if fileInfo["type"] == "file":
            fileName = fileInfo["name"]
            if fileName.endswith(f".{extension}"):
                print(f"Downloading {fileName}...")
                fileUrl = fileInfo["download_url"]
                savePath = os.path.join(saveFolder, fileName)
                download_file_from_url(fileUrl, savePath)
                print(f"{savePath} downloaded successfully.")

    print("All files downloaded.")


if __name__ == "__main__":
    download_files_from_github_repo(folderName="tenders", saveFolder="download")
    download_files_from_github_repo(
        folderName="", saveFolder="download", extension="json"
    )
