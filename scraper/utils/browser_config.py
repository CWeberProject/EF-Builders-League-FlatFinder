from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from pyvirtualdisplay import Display
import random
import atexit

# Initialize virtual display
display = None

def initialize_virtual_display():
    """Initialize virtual display using Xvfb."""
    global display
    display = Display(visible=0, size=(1920, 1080))
    display.start()
    atexit.register(lambda: display.stop() if display else None)

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

def get_random_user_agent() -> str:
    """Return a random User-Agent string."""
    return random.choice(USER_AGENTS)

def setup_webdriver() -> webdriver.Chrome:
    """Configure and initialize Chrome WebDriver with anti-detection measures in virtual display."""
    # Start virtual display before browser
    initialize_virtual_display()
    options = Options()
    
    # Set random viewport size
    viewport = random.choice(VIEWPORT_SIZES)
    options.add_argument(f"--window-size={viewport[0]},{viewport[1]}")
    
    # Set random user agent
    options.add_argument(f'user-agent={get_random_user_agent()}')
    
    # Add common browser features and anti-detection measures
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Enable cookies and storage
    options.add_argument('--enable-cookies')
    options.add_argument('--enable-local-storage')
    
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
    
    # Initialize webdriver with custom options
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
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