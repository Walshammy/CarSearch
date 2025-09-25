from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def test_trademe():
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("Chrome driver initialized")
        
        # Navigate to Toyota 86 page
        url = 'https://www.trademe.co.nz/a/motors/cars/toyota/86'
        driver.get(url)
        print(f"Navigated to: {url}")
        
        # Wait for page to load
        time.sleep(5)
        
        # Get page title
        title = driver.title
        print(f"Page title: {title}")
        
        # Check what elements are actually on the page
        print("\n=== Checking for various elements ===")
        
        # Try different selectors
        selectors_to_try = [
            'div',
            'article',
            '[class*="listing"]',
            '[class*="card"]',
            '[class*="item"]',
            '[data-testid]',
            'h1, h2, h3',
            'a[href*="/motors/"]',
            '.search-result',
            '.listing-card'
        ]
        
        for selector in selectors_to_try:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"{selector}: {len(elements)} elements found")
                
                # Show first few elements if any found
                if elements and len(elements) > 0:
                    for i, elem in enumerate(elements[:3]):
                        try:
                            text = elem.text.strip()[:100] if elem.text else "No text"
                            tag = elem.tag_name
                            classes = elem.get_attribute('class') or "No classes"
                            print(f"  {i+1}. <{tag}> class='{classes}' text='{text}...'")
                        except:
                            print(f"  {i+1}. <element> (couldn't get details)")
            except Exception as e:
                print(f"{selector}: Error - {e}")
        
        # Get page source length
        page_source = driver.page_source
        print(f"\nPage source length: {len(page_source)} characters")
        
        # Save page source for inspection
        with open('page_source.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("Page source saved to page_source.html")
        
        driver.quit()
        print("Test completed successfully")
        
    except Exception as e:
        print(f"Error: {e}")
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    test_trademe()
