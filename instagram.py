from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

# Replace these with your Instagram credentials
INSTAGRAM_USERNAME = "YOUR_USERNMAE"
INSTAGRAM_PASSWORD = "YOUR_PASSWORD"

# Settings - FASTER VERSION
MAX_UNFOLLOWS = 1300  # Set higher than your actual count to ensure all are unfollowed
UNFOLLOWS_PER_BATCH = 15  # Increased batch size
BATCH_PAUSE = (5, 10)  # Reduced pause between batches (was 20-40)
UNFOLLOW_PAUSE = (0.5, 1.2)  # Reduced pause between unfollows (was 1-3)
LONG_BREAK_INTERVAL = 100  # Take longer breaks less frequently (was 50)
LONG_BREAK_DURATION = (30, 60)  # Shorter long breaks (was 120-240)

# Initialize WebDriver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver.maximize_window()

def login():
    """Log in to Instagram"""
    print("Opening Instagram login page...")
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(3)  # Reduced from 5

    print("Logging in...")
    username_field = driver.find_element(By.NAME, "username")
    password_field = driver.find_element(By.NAME, "password")
    username_field.send_keys(INSTAGRAM_USERNAME)
    password_field.send_keys(INSTAGRAM_PASSWORD)
    password_field.send_keys(Keys.RETURN)
    time.sleep(5)  # Reduced from 10
    
    # Handle any popups
    try:
        not_now_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Not Now')]")
        if not_now_buttons:
            not_now_buttons[0].click()
            time.sleep(1)  # Reduced from 2
    except:
        pass

def open_following_list():
    """Navigate to profile and open following list"""
    print("Navigating to profile...")
    driver.get(f"https://www.instagram.com/{INSTAGRAM_USERNAME}/")
    time.sleep(3)  # Reduced from 5
    
    print("Opening Following list...")
    try:
        following_link = driver.find_element(By.XPATH, "//a[contains(@href, '/following')]")
        following_count_text = following_link.text.split()[0].replace(',', '')
        following_count = int(following_count_text) if following_count_text.isdigit() else 0
        print(f"You are following approximately {following_count} accounts")
        following_link.click()
        time.sleep(3)  # Reduced from 5
        return following_count
    except Exception as e:
        print(f"Error opening following list: {e}")
        driver.save_screenshot("open_following_error.png")
        return 0

def find_following_buttons():
    """Find all Following buttons in the current view"""
    selectors = [
        "//button[contains(.,'Following')]",
        "//div[contains(@role,'button')][contains(.,'Following')]",
        "//div[@role='dialog']//button[contains(.,'Following')]",
        "//div[contains(@class,'_aacl')][contains(.,'Following')]"
    ]
    
    for selector in selectors:
        try:
            buttons = driver.find_elements(By.XPATH, selector)
            if buttons:
                print(f"Found {len(buttons)} 'Following' buttons")
                return buttons
        except Exception as e:
            print(f"Error with selector {selector}: {e}")
    
    print("No Following buttons found")
    driver.save_screenshot("no_buttons.png")
    return []

def unfollow_visible_users():
    """Unfollow users that are currently visible in the dialog"""
    buttons = find_following_buttons()
    unfollowed = 0
    
    for i, button in enumerate(buttons):
        try:
            # Scroll button into view - faster scroll
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'instant'})", button)
            time.sleep(0.2)  # Reduced from 0.5
            
            print(f"Clicking 'Following' button {i+1}/{len(buttons)}")
            button.click()
            time.sleep(0.5)  # Reduced from 1.0-1.5
            
            # Click the confirm button
            confirm_selectors = [
                "//button[contains(text(), 'Unfollow')]",
                "//button[contains(., 'Unfollow')]",
                "//div[@role='dialog']//div[@role='dialog']//button"
            ]
            
            confirmed = False
            for selector in confirm_selectors:
                try:
                    confirm_buttons = driver.find_elements(By.XPATH, selector)
                    if confirm_buttons:
                        confirm_buttons[0].click()
                        unfollowed += 1
                        print(f"✓ Unfollowed user {i+1}, total in this batch: {unfollowed}")
                        confirmed = True
                        break
                except Exception as e:
                    continue
            
            if not confirmed:
                print(f"⚠ Could not confirm unfollow for user {i+1}")
                # Try clicking the button again to close any dialog
                try:
                    button.click()
                except:
                    pass
            
            # Random pause between unfollows - faster
            time.sleep(random.uniform(UNFOLLOW_PAUSE[0], UNFOLLOW_PAUSE[1]))
            
        except Exception as e:
            print(f"Error unfollowing user {i+1}: {e}")
    
    return unfollowed

def main():
    try:
        login()
        total_unfollowed = 0
        following_count = open_following_list()
        consecutive_empty_batches = 0
        
        while total_unfollowed < MAX_UNFOLLOWS:
            batch_unfollowed = unfollow_visible_users()
            
            if batch_unfollowed == 0:
                consecutive_empty_batches += 1
                print(f"No users unfollowed in this batch. Empty batch count: {consecutive_empty_batches}")
                
                # If we've had too many empty batches, refresh the page completely
                if consecutive_empty_batches >= 3:
                    print("Multiple empty batches. Refreshing profile completely...")
                    consecutive_empty_batches = 0
                    following_count = open_following_list()
                else:
                    # Try scrolling down if possible
                    try:
                        dialog = driver.find_element(By.XPATH, "//div[@role='dialog']")
                        driver.execute_script("arguments[0].scrollTop += 500", dialog)
                        time.sleep(1)
                    except:
                        # If scrolling fails, refresh
                        following_count = open_following_list()
                
                # If still no following count, we're probably done
                if following_count == 0:
                    print("No more users to unfollow. Exiting.")
                    break
                
                continue
            else:
                consecutive_empty_batches = 0
            
            total_unfollowed += batch_unfollowed
            print(f"Total unfollowed so far: {total_unfollowed}")
            
            # Check if we should take a longer break (less frequent, shorter breaks)
            if total_unfollowed % LONG_BREAK_INTERVAL == 0:
                long_break = random.uniform(LONG_BREAK_DURATION[0], LONG_BREAK_DURATION[1])
                print(f"Taking a break of {long_break:.0f} seconds after {total_unfollowed} unfollows...")
                time.sleep(long_break)
            
            # Refresh the list after each batch
            if total_unfollowed < MAX_UNFOLLOWS:
                pause = random.uniform(BATCH_PAUSE[0], BATCH_PAUSE[1])
                print(f"Pausing for {pause:.0f} seconds before continuing...")
                time.sleep(pause)
                
                # Try to scroll down first before refreshing
                try:
                    dialog = driver.find_element(By.XPATH, "//div[@role='dialog']")
                    driver.execute_script("arguments[0].scrollTop += 300", dialog)
                    time.sleep(1)
                    
                    # Check if new buttons appear
                    new_buttons = find_following_buttons()
                    if not new_buttons or len(new_buttons) < 2:
                        print("Few or no buttons after scrolling. Refreshing list...")
                        following_count = open_following_list()
                except:
                    following_count = open_following_list()
                
                if following_count == 0:
                    print("All users unfollowed successfully!")
                    break
        
        print(f"Successfully unfollowed {total_unfollowed} users.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
        driver.save_screenshot("error_screenshot.png")
    
    finally:
        print("Closing the browser...")
        driver.quit()

if __name__ == "__main__":
    main()