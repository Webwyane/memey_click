import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
}

url = "https://cafeaudiobooks.com/brandon-sanderson-warbreaker-book-2/"
soup = BeautifulSoup(requests.get(url).content, "html.parser")

for u in soup.select("[data-url]"):
    u = u["data-url"]
    print("Downloading {}".format(u))
    with open(u.split("/")[-1], "wb") as f_out:
        f_out.write(requests.get(u, headers=headers).content)