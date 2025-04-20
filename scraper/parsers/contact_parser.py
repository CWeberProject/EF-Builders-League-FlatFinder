from typing import Dict, Any
import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.webdriver import WebDriver
from ..utils.logging_config import logger

class ContactParser:
    """Parser for extracting contact information from Craigslist listings."""

    def __init__(self, driver: WebDriver):
        """Initialize contact parser with WebDriver instance."""
        self.driver = driver

    def get_viewport_boundaries(self) -> Dict[str, int]:
        """Get current viewport boundaries and scroll position."""
        return {
            'width': self.driver.execute_script('return window.innerWidth;'),
            'height': self.driver.execute_script('return window.innerHeight;'),
            'scroll_x': self.driver.execute_script('return window.pageXOffset;'),
            'scroll_y': self.driver.execute_script('return window.pageYOffset;')
        }

    def get_current_mouse_position(self) -> tuple:
        """Get current mouse position with fallback to (0,0)."""
        result = self.driver.execute_script("return [window.mousex || 0, window.mousey || 0]")
        return (result[0], result[1])

    def calculate_control_point(self, start: tuple, end: tuple) -> tuple:
        """Calculate a reasonable control point for Bezier curve between start and end points."""
        # Create slight arc in movement by offsetting control point
        midpoint_x = int((start[0] + end[0]) / 2)
        midpoint_y = int((start[1] + end[1]) / 2)
        offset = random.randint(50, 100)
        
        return (int(midpoint_x + random.randint(-offset, offset)),
                int(midpoint_y + random.randint(-offset, offset)))

    def calculate_bezier_points(self, p0: tuple, p1: tuple, p2: tuple, steps: int = 20) -> list:
        """Generate points along a quadratic Bezier curve for smooth mouse movement."""
        points = []
        for i in range(steps + 1):
            t = i / steps
            # Quadratic Bezier curve formula with integer coordinates
            x = int((1-t)**2 * p0[0] + 2*(1-t)*t * p1[0] + t**2 * p2[0])
            y = int((1-t)**2 * p0[1] + 2*(1-t)*t * p1[1] + t**2 * p2[1])
            points.append((x, y))
        return points

    def is_point_safe(self, point: tuple, viewport: Dict[str, int]) -> bool:
        """Check if a point is within safe bounds of viewport."""
        margin = 50  # Safety margin in pixels
        return (margin <= point[0] <= viewport['width'] - margin and
                margin <= point[1] <= viewport['height'] - margin)

    def move_to_relative(self, point: tuple):
        """Execute a relative mouse movement to a point."""
        current = self.get_current_mouse_position()
        offset_x = int(point[0] - current[0])
        offset_y = int(point[1] - current[1])
        
        # Break down movement into smaller steps if needed
        max_step = 20
        steps_x = abs(offset_x) // max_step + 1
        steps_y = abs(offset_y) // max_step + 1
        steps = max(steps_x, steps_y)
        
        for i in range(steps):
            step_x = int(offset_x / steps)  # Ensure integer steps
            step_y = int(offset_y / steps)  # Ensure integer steps
            if step_x != 0 or step_y != 0:  # Only move if there's actual displacement
                ActionChains(self.driver).move_by_offset(step_x, step_y).perform()
                time.sleep(random.uniform(0.01, 0.02))

    def _human_like_click(self, element: WebElement):
        """Simulate very human-like clicking behavior with smooth mouse movements."""
        try:
            # Get viewport boundaries and element information
            viewport = self.get_viewport_boundaries()
            element_loc = element.location
            element_size = element.size
            
            # Ensure target is within viewport with integer coordinates
            target_x = int(min(max(element_loc['x'], 50), viewport['width'] - 50))
            target_y = int(min(max(element_loc['y'], 50), viewport['height'] - 50))
            
            # Generate smooth movement path
            start = self.get_current_mouse_position()
            control = self.calculate_control_point(start, (target_x, target_y))
            path = self.calculate_bezier_points(start, control, (target_x, target_y))
            
            # Execute movement with acceleration/deceleration
            action = ActionChains(self.driver)
            for i, point in enumerate(path):
                if self.is_point_safe(point, viewport):
                    # Gradual acceleration and deceleration
                    if i < len(path) // 3:  # Acceleration phase
                        delay = 0.03 - (0.02 * i / (len(path) // 3))
                    elif i > 2 * len(path) // 3:  # Deceleration phase
                        delay = 0.01 + (0.02 * (i - 2 * len(path) // 3) / (len(path) // 3))
                    else:  # Constant speed phase
                        delay = 0.01
                        
                    self.move_to_relative(point)
                    time.sleep(delay)
            
            # Add slight random offset for final position
            x_offset = random.randint(-element_size['width']//8, element_size['width']//8)
            y_offset = random.randint(-element_size['height']//8, element_size['height']//8)
            
            # Ensure final position is within element bounds with integer coordinates
            final_x = int(max(min(target_x + x_offset, element_loc['x'] + element_size['width']), element_loc['x']))
            final_y = int(max(min(target_y + y_offset, element_loc['y'] + element_size['height']), element_loc['y']))
            
            # Move to final position and click
            self.move_to_relative((final_x, final_y))
            action.pause(random.uniform(0.1, 0.2))
            action.click_and_hold().pause(random.uniform(0.05, 0.15)).release()
            action.perform()
            
            # Update stored mouse position
            self.driver.execute_script(
                f"window.mousex = {final_x}; window.mousey = {final_y};"
            )
            
            # Random delay after clicking
            time.sleep(random.uniform(2.0, 3.0))
            
        except Exception as e:
            logger.error(f"Error during mouse movement: {e}")
            # Fallback to direct click if smooth movement fails
            element.click()
            time.sleep(random.uniform(2.0, 3.0))

    def _natural_scroll(self, element: WebElement):
        """Perform natural scrolling to element with dynamic speed and boundary checks."""
        try:
            # Get element position and viewport info
            element_location = element.location
            viewport = self.get_viewport_boundaries()
            current_scroll = viewport['scroll_y']
            viewport_height = viewport['height']
            document_height = self.driver.execute_script("return document.documentElement.scrollHeight")
            
            # Calculate target scroll position with margin
            margin = viewport_height * 0.2  # 20% viewport margin
            target_scroll = max(0, min(
                element_location['y'] - margin,
                document_height - viewport_height
            ))
            
            # Calculate adaptive number of steps based on distance
            distance = abs(target_scroll - current_scroll)
            base_steps = 5
            additional_steps = int(distance / 200)  # Add more steps for longer distances
            steps = min(base_steps + additional_steps, 12)  # Cap at reasonable maximum
            
            # Generate smooth acceleration curve
            def ease_in_out(t):
                # Cubic easing for smoother acceleration/deceleration
                return (3 - 2 * t) * t * t
            
            # Perform smooth scrolling with dynamic speed
            for i in range(steps + 1):
                progress = i / steps
                eased_progress = ease_in_out(progress)
                
                # Calculate intermediate scroll position
                scroll_to = current_scroll + (target_scroll - current_scroll) * eased_progress
                
                # Add small random variation for natural feel
                variation = random.uniform(-5, 5)
                scroll_to = max(0, min(scroll_to + variation, document_height - viewport_height))
                
                # Execute scroll with smooth behavior
                self.driver.execute_script(
                    "window.scrollTo({top: arguments[0], behavior: 'smooth'})",
                    scroll_to
                )
                
                # Dynamic delay based on scroll phase
                if i < steps * 0.3:  # Initial acceleration
                    delay = random.uniform(0.2, 0.25)
                elif i > steps * 0.7:  # Final deceleration
                    delay = random.uniform(0.25, 0.3)
                else:  # Constant speed phase
                    delay = random.uniform(0.15, 0.2)
                
                time.sleep(delay)
            
            # Final adjustment to ensure element is visible
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                element
            )
            time.sleep(random.uniform(0.3, 0.5))
            
        except Exception as e:
            logger.error(f"Error during smooth scroll: {e}")
            # Fallback to direct scroll if smooth scroll fails
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(random.uniform(0.3, 0.5))

    def extract_contact_info(self, url: str) -> Dict[str, Any]:
        """Extract contact information using Selenium with sophisticated human-like behavior."""
        contact_info = {}
        try:
            # Add random initial page load delay
            time.sleep(random.uniform(4.0, 7.0))
            
            logger.info("Loading page URL in Selenium...")
            self.driver.get(url)
            
            # Simulate reading the page
            read_time = random.uniform(8.0, 15.0)
            logger.info(f"Simulating page reading for {read_time:.1f} seconds...")
            
            # Natural scrolling behavior while "reading"
            scroll_steps = random.randint(4, 7)
            for _ in range(scroll_steps):
                scroll_amount = random.randint(100, 300)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                time.sleep(read_time / scroll_steps)
            
            # Scroll back up slightly
            self.driver.execute_script("window.scrollBy(0, -150);")
            time.sleep(random.uniform(1.0, 2.0))
            
            # Wait for and click reply button
            wait = WebDriverWait(self.driver, 20)
            reply_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.reply-button"))
            )
            self._human_like_click(reply_button)
            
            # Extract contact info sections
            contact_info.update(self._extract_contact_name(wait))
            contact_info.update(self._extract_phone_info(wait))
            contact_info.update(self._extract_email_info(wait))
            
            logger.info("Contact info extraction completed")
            return contact_info

        except Exception as e:
            logger.error(f"Error getting contact info: {e}")
            return {}

    def _extract_contact_name(self, wait: WebDriverWait) -> Dict[str, str]:
        """Extract contact name from the listing."""
        try:
            contact_name_elem = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.reply-contact-name"))
            )
            return {'contact_name': contact_name_elem.text.replace('contact name:', '').strip()}
        except (TimeoutException, NoSuchElementException) as e:
            logger.warning(f"Could not find contact name: {str(e)}")
            return {}

    def _extract_phone_info(self, wait: WebDriverWait) -> Dict[str, str]:
        """Extract phone information (call and text numbers)."""
        phone_info = {}
        
        # Process call number
        try:
            call_xpath = "//button[contains(@class, 'reply-option-header')]//span[@class='reply-option-label' and text()='call']"
            call_button = wait.until(
                EC.presence_of_element_located((By.XPATH, call_xpath))
            ).find_element(By.XPATH, "./ancestor::button")
            
            self._natural_scroll(call_button)
            time.sleep(random.uniform(1.0, 2.0))
            self._human_like_click(call_button)
            
            call_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.reply-content-phone a[href^='tel:']"))
            )
            phone_info['call_number'] = call_element.text
            
        except Exception as e:
            logger.error(f"Error processing call section: {str(e)}")
        
        # Process text number
        try:
            text_xpath = "//button[contains(@class, 'reply-option-header')]//span[@class='reply-option-label' and text()='text']"
            text_button = wait.until(
                EC.presence_of_element_located((By.XPATH, text_xpath))
            ).find_element(By.XPATH, "./ancestor::button")
            
            self._natural_scroll(text_button)
            time.sleep(random.uniform(1.0, 2.0))
            self._human_like_click(text_button)
            
            text_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.reply-content-sms a[href^='sms:']"))
            )
            phone_info['text_number'] = text_element.text
            
        except Exception as e:
            logger.error(f"Error processing text section: {str(e)}")
        
        return phone_info

    def _extract_email_info(self, wait: WebDriverWait) -> Dict[str, str]:
        """Extract email information."""
        try:
            email_xpath = "//button[contains(@class, 'reply-option-header')]//span[@class='reply-option-label' and text()='email']"
            email_button = wait.until(
                EC.presence_of_element_located((By.XPATH, email_xpath))
            ).find_element(By.XPATH, "./ancestor::button")
            
            self._natural_scroll(email_button)
            time.sleep(random.uniform(1.0, 2.0))
            self._human_like_click(email_button)
            
            email_part = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.reply-email-localpart"))
            )
            if email_part:
                return {'email': f"{email_part.text}@hous.craigslist.org"}
            
        except Exception as e:
            logger.error(f"Error processing email section: {str(e)}")
        
        return {}