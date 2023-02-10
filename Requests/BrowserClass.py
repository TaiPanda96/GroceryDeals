# Install 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

class Selenium:
    def __init__(self,headless = True):
        self.errorMessage = ''
        self.userAgent    = True; 
        self.headless     = headless; 

    def createBrowserInstance(self):
        # Options
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('/usr/bin/google-chrome-stable')
        if self.headless is True:
            options.add_argument('--headless')
        if self.userAgent is True:
            options.add_argument("--user-agent=Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Mobile Safari/537.36 Edge/1$")

        # Create a new instance of the Chrome driver
        try: 
            self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options);
            return self.driver
        except Exception as seleniumError:
            self.driver = None;
            self.errorMessage = seleniumError

    @staticmethod
    def initBrowser():
        # Options
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('/usr/bin/google-chrome-stable')
        options.add_argument('--headless')
        options.add_argument("--user-agent=Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Mobile Safari/537.36 Edge/1$")

        # Create a new instance of the Chrome driver
        try: 
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options);
            return driver
        except Exception as seleniumError:
            print(seleniumError)
            return None 


    @staticmethod
    def getHttpChromiumRequestStaticWrapper(request_url, waitForInstructions = {}, browser = ''):
        """"""
        soup = ''
        xpath, waitTime = waitForInstructions.get('xpath', False), waitForInstructions.get('waitTime', False)
        if any([xpath, waitTime]) is False:
            xpath, waitTime = '//*[@id="site-content"]/div/div/div[6]/div/div[2]/div[3]', 30;
        try:
            if browser is None: 
                return soup;
            browser.get(request_url);
            # wait until network is idle
            WebDriverWait(browser,waitTime).until(EC.presence_of_element_located((By.XPATH, xpath)));
            content = browser.page_source
            if content:
                try:
                    soup = BeautifulSoup(content, 'lxml');
                    return soup;
                except Exception as ScraperError:
                    return soup;
            else:
                return soup;
        except Exception as error:
            return soup;
        
    def getHttpChromiumRequestWrapper(self,request_url,waitForInstructions = {}):
        """ returns soup """
        soup = ''
        xpath, waitTime = waitForInstructions.get('xpath', False), waitForInstructions.get('waitTime', False)
        if any([xpath, waitTime]) is False:
            xpath, waitTime = '//*[@id="site-content"]/div/div/div[6]/div/div[2]/div[3]', 30;
        try: 
            browser = self.createBrowserInstance();
            if browser is None: 
                self.errorMessage = 'Unable to start browser instance'
                return soup;
            browser.get(request_url);
            # wait until network is idle
            WebDriverWait(browser,30).until(EC.presence_of_element_located((By.XPATH, xpath)));
            content = browser.page_source
            if content:
                try:
                    soup = BeautifulSoup(content, 'lxml');
                    return soup;
                except Exception as ScraperError:
                    self.errorMessage = ScraperError;
                    return soup;
            else:
                self.errorMessage = 'Unable to fetch soup string. Please check provided url';
                return soup;
        except Exception as error:
            self.errorMessage = 'Error: {}'.format(error);
            return soup;

        finally:
            if browser: 
                browser.close();
                browser.quit();


        







