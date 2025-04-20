import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
import urllib.request
import ssl
import random
import os

# Get Chrome paths from environment or use defaults
CHROME_PATH = os.getenv('CHROME_PATH', '/usr/bin/google-chrome')
CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH', '/usr/bin/chromedriver')

# Standard viewport sizes for randomization
VIEWPORT_SIZES = [
    (1920, 1080),
    (1440, 900),
    (1366, 768),
    (1280, 800),
]

# Common user agent strings
USER_AGENTS = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.7049.96 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.7049.96 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.7049.96 Edge/135.0.7049.96',
]

# Proxy settings
PROXY = "http://brd-customer-hl_edbe428d-zone-residential_proxy1:56g4ze3s28m3@brd.superproxy.io:33335"


def get_random_user_agent() -> str:
    """Return a random User-Agent string."""
    return random.choice(USER_AGENTS)

def setup_webdriver():
    """Configure and initialize undetected Chrome WebDriver with anti-detection measures."""
    # Initialize undetected Chrome options
    options = uc.ChromeOptions()
    
    # Headless mode configuration
    options.add_argument("--headless=new")
    options.add_argument("--remote-debugging-port=9222")
    
    # Container-specific Chrome flags
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Set random viewport size
    viewport = random.choice(VIEWPORT_SIZES)
    options.add_argument(f"--window-size={viewport[0]},{viewport[1]}")
    
    # Set random user agent
    options.add_argument(f'user-agent={get_random_user_agent()}')
    
    # Enable cookies and storage
    options.add_argument('--enable-cookies')
    options.add_argument('--enable-local-storage')
    
    # -------- proxy flag --------
    options.add_argument(f"--proxy-server={PROXY}")

    
    # Add common Chrome preferences
    prefs = {
        'profile.default_content_setting_values.notifications': 2,
        'profile.default_content_settings.popups': 0,
        'profile.default_content_setting_values.automatic_downloads': 1,
        'profile.default_content_setting_values.plugins': 1,
        'profile.cookie_controls_mode': 0,
        'profile.block_third_party_cookies': False
    }
    options.add_experimental_option('prefs', prefs)
    
    # Initialize undetected Chrome driver
    driver = uc.Chrome(options=options)
    
    # Set viewport size
    driver.set_window_size(viewport[0], viewport[1])
    
    # Execute CDP commands to modify browser fingerprint
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": get_random_user_agent(),
        "platform": random.choice(["Windows", "Macintosh", "Linux"]),
    })
    
    # Set implicit wait time
    driver.implicitly_wait(random.uniform(8, 12))
    
    return driver