import requests
from bs4 import BeautifulSoup

def check_code_status(code):
    url = "https://www.brawlhalla.com/redeem/"
    payload = {'code': code}

    # Send a request to the redemption page
    response = requests.post(url, data=payload)

    # Check if the request was successful
    if response.status_code != 200:
        return "Error: Unable to access the redemption page."

    # Parse the response content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Check for specific elements or text that indicate the code status
    if "redeemed" in soup.text.lower():
        return "The code has already been redeemed."
    elif "invalid" in soup.text.lower():
        return "The code is invalid."
    elif "success" in soup.text.lower():
        return "The code is valid and has not been redeemed."
    else:
        return "Unable to determine the status of the code."

# Example usage
redeem_code = "YOUR_REDEEM_CODE_HERE"
status = check_code_status(redeem_code)
print(status)
