from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By

from auto_resume.page.element import Element
from auto_resume.page.page import Page


class Authenticator(Page):

    global_me = Element.one((By.CLASS_NAME, 'global-nav__me'))
    username_field = Element.one((By.ID, "username"))
    password_field = Element.one((By.ID, "password"))
    submit_button = Element.one((By.XPATH, '//button[@type="submit"]'))
    
    def __init__(self, driver=None, config=None):
        self.driver = driver
        self.config = config

    @property
    def email(self):
        return self.config.secrets.email

    @property
    def password(self):
        return self.config.secrets.password

    def start(self):
        """Start the Chrome browser and attempt to log in to LinkedIn."""
        print("Starting Chrome browser to log in to LinkedIn.")
        self.driver.get('https://www.linkedin.com')

        self.await_pageload()
        
        if not self.is_logged_in():
            print('not logged in')
            self.handle_login()
        else:
            print('logged in')
        

    def handle_login(self):
        """Handle the LinkedIn login process."""
        print("Navigating to the LinkedIn login page...")
        self.driver.get("https://www.linkedin.com/login")
        try:
            print('handling Login')
            self.enter_credentials()
            self.submit_login_form()
        except NoSuchElementException:
            print("Could not log in to LinkedIn. Please check your credentials.")

    def enter_credentials(self):
        """Enter the user's email and password into the login form."""
        try:
            print('Enter Credentials.')
            self.username_field().send_keys(self.email)
            self.password_field().send_keys(self.password)
            
        except TimeoutException:
            print("Login form not found. Aborting login.")

    def submit_login_form(self):
        """Submit the LinkedIn login form."""
        try:
            print('Submit Login Form')
            self.submit_button().click()
        except NoSuchElementException:
            print("Login button not found. Please verify the page structure.")

    def is_logged_in(self):
        """Check if the user is already logged in to LinkedIn."""
        try:
            self.wait_for(self.global_me.present())
            
            return True
        except TimeoutException:
            print('timed out waiting for login')
            return False

