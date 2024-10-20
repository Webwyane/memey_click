from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

# Setup Selenium WebDriver (download ChromeDriver and provide its path)
driver = webdriver.Chrome(executable_path='path/to/chromedriver')

# Function to login to Swiggy and scrape the cart
def scrape_swiggy_cart():
    driver.get("https://www.swiggy.com")
    
    # Add login automation steps here if necessary

    # Navigate to cart page
    driver.get("https://www.swiggy.com/cart")
    time.sleep(5)  # Wait for the cart page to load
    
    # Scrape cart details
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    cart_items = []
    for item in soup.find_all('div', class_='cart-item-class'):  # Update the class for cart item
        product_name = item.find('span', class_='product-name-class').text  # Update with the correct class
        price = item.find('span', class_='price-class').text
        quantity = item.find('span', class_='quantity-class').text
        cart_items.append({
            'product': product_name,
            'price': price,
            'quantity': quantity
        })
    
    return cart_items

# Function to transfer cart items and handle missing items
def add_to_zepto_cart(cart_items):
    driver.get("https://www.zepto.com")
    
    # Add login automation steps here
    
    missing_items = []  # To track missing items
    
    for item in cart_items:
        search_box = driver.find_element(By.NAME, 'search-input')  # Update with the correct input locator
        search_box.clear()
        search_box.send_keys(item['product'])
        search_box.submit()
        time.sleep(3)
        
        # Try finding the add to cart button
        try:
            add_button = driver.find_element(By.CLASS_NAME, 'add-to-cart-button-class')  # Update with the correct class
            add_button.click()
            time.sleep(2)
        except Exception as e:
            # Item not found, add to missing items list
            missing_items.append(item)
    
    return missing_items

# Function to handle missing items
def handle_missing_items(missing_items):
    for item in missing_items:
        print(f"Item '{item['product']}' is not available on the site.")
        choice = input(f"Would you like to (r)eplace it or (s)kip it? (r/s): ").lower()
        
        if choice == 'r':
            new_item = input(f"Enter a replacement for '{item['product']}': ")
            # Attempt to add the new item
            search_box = driver.find_element(By.NAME, 'search-input')  # Update with the correct input locator
            search_box.clear()
            search_box.send_keys(new_item)
            search_box.submit()
            time.sleep(3)
            
            try:
                add_button = driver.find_element(By.CLASS_NAME, 'add-to-cart-button-class')  # Update with the correct class
                add_button.click()
                time.sleep(2)
                print(f"'{new_item}' was added to the cart.")
            except Exception as e:
                print(f"'{new_item}' could not be found either.")
        else:
            print(f"'{item['product']}' was skipped.")
    
    print("All items processed.")

# Main script execution
if __name__ == "__main__":
    cart_data = scrape_swiggy_cart()
    print("Scraped Cart Data:", cart_data)
    
    missing_items = add_to_zepto_cart(cart_data)
    
    if missing_items:
        print("Some items were not found. Handling missing items...")
        handle_missing_items(missing_items)
    
    # Close the browser after execution
    driver.quit()
