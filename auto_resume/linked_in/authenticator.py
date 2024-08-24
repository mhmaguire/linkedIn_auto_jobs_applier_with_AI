from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By

from auto_resume.page.element import Element
from auto_resume.page.page import Page


class SignInPage(Page):
    url = 'https://www.linkedin.com'
    global_me = Element.one((By.CLASS_NAME, 'global-nav__me'))
    username_field = Element.one((By.ID, "username"))
    password_field = Element.one((By.ID, "password"))
    submit_button = Element.one((By.XPATH, '//button[@type="submit"]'))

    def is_logged_in(self):
        """Check if the user is already logged in to LinkedIn."""
        try:
            self.wait_for(self.global_me.present())
            
            return True
        except TimeoutException:
            print('timed out waiting for login')
            return False

    def handle_login(self, credentials):
        """Handle the LinkedIn login process."""
        print("Navigating to the LinkedIn login page...")
        
        try:
            print('handling Login')
            self.enter_credentials(credentials)
            self.submit_login_form()
        except NoSuchElementException:
            print("Could not log in to LinkedIn. Please check your credentials.")

    def enter_credentials(self, credentials):
        """Enter the user's email and password into the login form."""
        try:
            print('Enter Credentials.')
            self.username_field().send_keys(credentials.email)
            self.password_field().send_keys(credentials.password)
            
        except TimeoutException:
            print("Login form not found. Aborting login.")

    def submit_login_form(self):
        """Submit the LinkedIn login form."""
        try:
            print('Submit Login Form')
            self.submit_button().click()
        except NoSuchElementException:
            print("Login button not found. Please verify the page structure.")



class Authenticator(Page):
    
    def __init__(self, config=None):
        self.config = config

    def start(self, driver):
        """Attempt to log in to LinkedIn."""
        driver.get('https://www.linkedin.com/login')

        sign_in_page = SignInPage(driver)
        sign_in_page.await_pageload()
        sign_in_page.handle_login(self.config.secrets)
        
        if sign_in_page.is_logged_in():
            print('not logged in')
        else:
            print('logged in')
        

    



