from bs4 import BeautifulSoup
import requests
import csv

# Fetch the page content
page_to_scrape = requests.get("https://quotes.toscrape.com")
soup = BeautifulSoup(page_to_scrape.text, "html.parser")

# Find all quotes and authors
quotes = soup.findAll("span", attrs={"class": "text"})
authors = soup.findAll("small", attrs={"class": "author"})

# Print the quotes and authors
for quote, author in zip(quotes, authors):
    print(quote.text + " - " + author.text + "\n")

try:
    # Write to a text file
    with open("quotes.txt", "w", encoding="utf-8") as file:
        for quote, author in zip(quotes, authors):
            file.write(f"{quote.text} - {author.text}\n")
    print("Quotes and authors successfully written to quotes.txt.")

    # Write to a CSV file
    with open("quotes.csv", "w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Quote", "Author"])  # Write the header
        for quote, author in zip(quotes, authors):
            writer.writerow([quote.text, author.text])
    print("Quotes and authors successfully written to quotes.csv.")

except Exception as e:
    print(f"An error occurred: {e}")
  