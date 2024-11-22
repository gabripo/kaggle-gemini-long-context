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


def download_file_from_github(fileUrl, savePath):
    response = requests.get(fileUrl)
    response.raise_for_status()

    with open(savePath, "wb") as file:
        file.write(response.content)


def download_folder_from_github_repo(
    userName: str = "gabripo",
    repo: str = "kaggle-gemini-long-context",
    folderName: str = "",
    saveFolder: str = "downloaded",
):
    os.makedirs(saveFolder, exist_ok=True)

    filesInfo = files_info_from_github_repo_folder(userName, repo, folderName)
    for fileInfo in filesInfo:
        if fileInfo["type"] == "file":
            fileUrl = fileInfo["download_url"]
            fileName = fileInfo["name"]
            savePath = os.path.join(saveFolder, fileName)

            print(f"Downloading {fileName}...")
            download_file_from_github(fileUrl, savePath)
            print(f"{savePath} downloaded successfully.")

    print("All files downloaded.")


if __name__ == "__main__":
    download_folder_from_github_repo(folderName="tenders", saveFolder="download")
