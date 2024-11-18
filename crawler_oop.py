import json
import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
from collections import deque
import hashlib


class WebCrawler:
    VALID_GET_RESPONSE = 200

    def __init__(
        self,
        root_url,
        parent_folder,
        save_path="crawled",
        max_pages=100,
        page_marker="site",
        pagenames_to_exclude=None,
        fresh_download: bool = False,
    ):
        self.root_url = root_url
        self.parent_folder = parent_folder
        self.save_path = save_path
        self.max_pages = max_pages
        self.page_marker = page_marker
        self.pagenames_to_exclude = pagenames_to_exclude if pagenames_to_exclude else []
        self.visited_urls = set()
        self.json_files = []
        self.fresh_download = fresh_download

    def soup_page(self, url: str) -> BeautifulSoup:
        response = requests.get(url)
        if response.status_code == self.VALID_GET_RESPONSE:
            return BeautifulSoup(response.text, "html.parser")
        else:
            return BeautifulSoup("")

    def get_links(self, soup: BeautifulSoup) -> None:
        return [
            a["href"]
            for a in soup.find_all("a", href=True)
            if self.parent_folder in a["href"]
        ]

    def generate_filename_from_url(self, url: str) -> str:
        return f"{self.page_marker}_{hashlib.sha1(url.encode('UTF8')).hexdigest()}"

    def download_page(self, soup: BeautifulSoup, url: str, file_path: str) -> None:
        paragraphs_list = [p.get_text() for p in soup.find_all("p")]
        page_title = [t.get_text() for t in soup.find_all("title")]
        if paragraphs_list:
            site_data = {"title": page_title, "url": url, "content": paragraphs_list}

            self.write_json_from_data(site_data, file_path)
            print(f"JSON file {file_path} created from url {url}")

    @staticmethod
    def write_json_from_data(data: dict, file_path: str, indent_size: int = 4) -> None:
        with open(file_path, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=indent_size)

    def download_all_pages(self) -> None:
        stack = deque([self.root_url])

        while stack and len(self.json_files) < self.max_pages:
            url = stack.pop()

            if url in self.visited_urls:
                continue
            self.visited_urls.add(url)

            filename = self.generate_filename_from_url(url)
            self.json_files.append(filename)

            file_path = os.path.join(self.save_path, filename + ".json")
            file_links_path = os.path.join(self.save_path, filename + "_links.json")
            if self.fresh_download or (
                not os.path.exists(file_path) and not os.path.exists(file_links_path)
            ):
                soup = self.soup_page(url)
                self.download_page(soup, url, file_path)

                links = self.get_links(soup, url)
                self.write_json_from_data(links, file_links_path)
            else:
                print(f"File {file_path} related to url {url} already available!\n")
                with open(file_links_path, "r") as f:
                    links = json.load(f)

            pages_not_allowed = set(self.pagenames_to_exclude)
            for link in links:
                if set(link.split("/")).intersection(pages_not_allowed):
                    continue

                full_link = urljoin(url, link)
                if full_link not in self.visited_urls and "http" in full_link:
                    stack.append(full_link)

    def most_common_sentences_in_file(
        self,
        json_file_path: str,
        already_common_words: list[str] = None,
        frequency_threshold: int = 1,
    ) -> list[str]:
        if already_common_words is None:
            already_common_words = set()

        with open(json_file_path, "r") as f:
            data = json.load(f)

        if isinstance(data, list):
            content_list = [c.get("content", "") for c in data]
            content = []
            for content_page in content_list:
                content.extend(content_page)
        else:
            content = data.get("content", "")

        frequencies = {}
        if content:
            for sentence in content:
                frequencies[sentence] = frequencies.get(sentence, 0) + 1

        for sentence, freq in frequencies.items():
            if freq > frequency_threshold:
                already_common_words.add(sentence)
        return already_common_words

    def list_json_files_in_folder(
        self, json_files_folder: str, json_files_to_exclude: str | list[str]
    ) -> list[str]:
        if json_files_to_exclude is None:
            json_files_to_exclude = []

        files_to_exclude = set(json_files_to_exclude)
        file_list = [
            os.path.join(json_files_folder, file)
            for file in os.listdir(json_files_folder)
            if file.endswith(".json")
            and file not in files_to_exclude
            and self.page_marker in file
            and not "_links.json" in file
        ]
        return file_list

    def clean_json_file(
        self,
        json_file_path: str,
        most_common_rows: set[str] = set(),
        overwrite: bool = True,
    ):
        if most_common_rows is None:
            most_common_rows = set()

        with open(json_file_path, "r") as f:
            data = json.load(f)

        if isinstance(data, list):
            for i, page in enumerate(data):
                indexes_to_remove = {
                    j
                    for j, row in enumerate(page.get("content", ""))
                    if row in most_common_rows
                }
                data[i]["content"][:] = [
                    c
                    for k, c in enumerate(data[i]["content"])
                    if k not in indexes_to_remove
                ]
        else:
            indexes_to_remove = {
                i
                for i, row in enumerate(data.get("content", ""))
                if row in most_common_rows
            }
            data["content"][:] = [
                c for k, c in enumerate(data["content"]) if k not in indexes_to_remove
            ]

        json_cleaned_file_path = (
            json_file_path
            if overwrite
            else json_file_path.replace(".json", "_cleaned.json")
        )
        self.write_json_from_data(data, json_cleaned_file_path)
        return json_cleaned_file_path

    def clean_json_files(
        self,
        json_files_folder: str,
        files_to_exclude: str | list[str],
        overwrite: bool = True,
    ) -> list[str]:
        file_list = self.list_json_files_in_folder(json_files_folder, files_to_exclude)

        most_common_rows = set()
        for file in file_list:
            most_common_rows = self.most_common_sentences_in_file(
                file, most_common_rows
            )

        cleaned_files = []
        for file in file_list:
            json_cleaned_file_path = self.clean_json_file(
                file, most_common_rows, overwrite
            )
            cleaned_files.append(json_cleaned_file_path)
        return cleaned_files

    def merge_json_files(
        self, json_files_folder: str, target_file: str = "_merged.json"
    ) -> str:
        file_list = self.list_json_files_in_folder(json_files_folder, [target_file])
        if file_list:
            result_file_content = []
            for file in file_list:
                with open(file, "r") as f:
                    json_data = json.load(f)
                    result_file_content.append(json_data)

            result_file_path = os.path.join(json_files_folder, target_file)
            self.write_json_from_data(result_file_content, result_file_path)
            return result_file_path
        return ""

    def json_to_txt(self, json_file_path: str, target_name: str = "") -> str:
        if target_name == "":
            target_name = os.path.basename(json_file_path).replace(".json", ".txt")
        elif not target_name.endswith(".txt"):
            target_name = target_name + "_merged.txt"

        with open(json_file_path, "r") as f:
            data = json.load(f)

        result_file_path = os.path.join(self.save_path, target_name)
        with open(result_file_path, "w") as f:
            for num_page, webpage in enumerate(data):
                page_title = webpage.get("title", "")
                page_url = webpage.get("url", "")
                f.write(
                    f'The page with name "{page_title[0]}" and URL "{page_url}" has the following content:\n'
                )

                page_content = webpage.get("content", "")
                for row in page_content:
                    f.write(f"{row} \n")

                f.write(
                    f'The page with name "{page_title[0]}" and URL "{page_url}" ends here.\n\n'
                )

        return result_file_path

    def text_from_file(self, file_path: str) -> str | list[str]:
        with open(file_path, "r", encoding="utf-8") as f:
            text_string = f.read()
            f.seek(0)
            text_list = f.readlines()
        return text_string, text_list

    def get_text_from_webpages(self) -> str:
        os.makedirs(self.save_path, exist_ok=True)

        self.download_all_pages()

        merged_json_name = self.page_marker + "_merged.json"
        json_files_clean = self.clean_json_files(self.save_path, [merged_json_name])
        merged_json_path = self.merge_json_files(self.save_path, merged_json_name)

        most_common_words_merged_json = self.most_common_sentences_in_file(
            merged_json_path, frequency_threshold=(len(json_files_clean) - 1) // 2 + 1
        )
        merged_json_path = self.clean_json_file(
            merged_json_path, most_common_words_merged_json
        )

        plain_text_file = self.json_to_txt(merged_json_path)
        plain_text, text_string = self.text_from_file(plain_text_file)
        return plain_text


if __name__ == "__main__":
    parent_folder = "/products-and-solutions/"
    initial_url = "https://www.hitachienergy.com/products-and-solutions/"
    save_folder = "companies_info"
    num_pages_to_download = 10
    dummy_page_name = "TEST"
    pages_to_exclude = ["contact-us"]
    crawler = WebCrawler(
        root_url=initial_url,
        parent_folder=parent_folder,
        save_path=save_folder,
        max_pages=num_pages_to_download,
        page_marker=dummy_page_name,
        pagenames_to_exclude=pages_to_exclude,
    )
    crawler.get_text_from_webpages()
