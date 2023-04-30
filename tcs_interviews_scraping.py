import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

class Glassdoor():
    
    def __init__(self, credentials):
        '''
        Provide dictionary with email and password.
        
        '''
        self.driver = webdriver.Chrome("chromedriver")
        self.driver.maximize_window()
        self.driver.implicitly_wait(5)
        self.delay = 10
        
        self.username = credentials['email']
        self.password = credentials['password']

    def get_driver(self):
        return self.driver

    def clickToContinueWithEmail(self):
        try:
            next = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, 'email-button')))
            print('Clicked on Continue With Email \n')
            next.click()
            return True
        except TimeoutException as e:
            print('No continue button on the page')
            return False
        except Exception as e:
            print('some error occurred:')
            print(e)
            return False
    
    def clickSignIn(self):
        all_buttons = self.driver.find_elements(By.XPATH, '//button')
        signin_button = None
        for button in all_buttons:
            for span in self.getInnerElements(button, 'span'):
                if 'Sign In' in self.getInnerHTML(span):
                    signin_button = button
        WebDriverWait(self.driver, 50).until(EC.element_to_be_clickable(signin_button))
        signin_button.click()

    def getInnerHTML(self, element):
        try:
            return element.get_attribute('innerHTML')
        except Exception:
            return 'no-element'

    def getTagName(self, element):
        try:
            return element.tag_name
        except Exception:
            return 'no-element'

    def getInnerElements(self, element, tagName):
        try:
            return element.find_elements(By.TAG_NAME, tagName)
        except:
            return []

    def fillUserName(self):
        self.driver.find_element(By.CSS_SELECTOR,'input[id="inlineUserEmail"]')\
        .send_keys(self.username)
        
    def fillPassword(self):
        self.driver.find_element(By.CSS_SELECTOR,'input[id="inlineUserPassword"]')\
        .send_keys(self.password)
            
    def print_element(self, element):
        print(element.get_attribute('innerHTML'))

    def driver_close(self):
        self.driver.close()
        
    def maximize_window(self):
        self.maximize_window()
        
    def glassdoorLogInPageURL(self):
        self.driver.get('https://www.glassdoor.com/index.htm')
        
    def get_sleep(self,sleep_time):
        time.sleep(sleep_time)
        
    def takeMeToURL(self,url):
        self.driver.get(url)
        
    def clickNextButton(self):
        #wait until the next button appears                                                                        
        next_button = WebDriverWait(self.driver, self.delay).until\
                            (EC.element_to_be_clickable((By.CSS_SELECTOR, \
                             'button[aria-label="Next"]')))

        #click the next button and wait 
        self.driver.execute_script("arguments[0].click();", next_button)

        
    def logIn(self):
        '''
        Log-in will take place here.
        '''
        print('Log-In process started. \n')
        self.glassdoorLogInPageURL()
        self.fillUserName()
        self.clickToContinueWithEmail()
        self.fillPassword()
        self.clickSignIn()
        self.get_sleep(10)
        print('Log-In process completed. \n')
      
    
    def get_info_from_page(self, fw):

        """
        Extracts all the interview posts from the current page and writes to the specified writer
        """
        
        #get all interview divs in the current page
        interviews= self.driver.find_elements(by=By.CSS_SELECTOR,value='[data-brandviews*="MODULE:n=ei-interviews-interview:eid="]')
        
        for interview in interviews: # for each inteview in div
            
            date,text,offer_tag,exp_tag,level_tag='NA','NA','NA','NA','NA'

            try: # try to get the date of the inteview
                dt=interview.find_element(by=By.CSS_SELECTOR,\
                          value='p[class="mt-0 mb-xxsm d-flex justify-content-between css-13r90be e1lscvyf1"]')
                date=dt.text
                

            except NoSuchElementException as e: # date could not be found
                print('could not extract date')

            try: #try to get the review(text) of the inteview
                txt=interview.find_element(by=By.CSS_SELECTOR,\
                                           value='[class*=" css-w00cnv mt-xsm mb-std"]')
                text=txt.text
                
                

            except NoSuchElementException as e: # headline or link could not be found
                print('could not extract text')


            try: # try to get the offer (accepted, declined, no offer)

                #get the tags
                tags=interview.find_elements(by=By.CSS_SELECTOR,\
                                               value='[class*="d-block d-sm-inline-block"]')
                cnt = 1
                
                for tag in tags:
                    
                    if cnt==1:
                        #get the date string
                        offer_tag=tag.text


                    if cnt==2:
                        #get the date string
                        exp_tag=tag.text
                        
                    if cnt==3:
                        #get the date string
                        level_tag=tag.text

                    cnt += 1

            except NoSuchElementException as e:
                print('could not extract tags')


            #write a new row for this interview
            row_data = {"date": date,"text": text,\
                        "offer_tag": offer_tag,"exp_tag": exp_tag,\
                        "level_tag": level_tag}
            
            json.dump(row_data, fw, indent=1)
            fw.write(',\n')



    def get_all_interviews(self, 
                            delay:int = 10 # number of seconds to wait 
                        ):
        '''
        This function takes to next page till available.

        '''
        #create a new josn writer for the interview posts
        fw=open('tcs_interviews.json','w')
        
        fw.write('[') # write the opening bracket of the JSON array

        tcs_url= 'https://www.glassdoor.com/Interview/Tata-Consultancy-Services-Interview-Questions-E13461.htm'# create the url

        print('Now, Going to TCS Interviews url.. \n')
        
        self.takeMeToURL(tcs_url) # visit the interview page
        
        page_cnt=1 # keep track of page count
        
        print('Scraping information.....')

        while True: # keep going until there are no more pages

            print('page',page_cnt) # print current page count
            
            flag = True #setting flag for refresh

            #extract and write the interview posts from the current page
            self.get_info_from_page(fw)

            try:
                self.clickNextButton() #Click on next button
                self.get_sleep(delay) #wait for sec

            except TimeoutException as e:
                
                if flag == True:
                    print(f'Refreshing Page: {page_cnt}')
                    self.driver.refresh() #Refreshing current page
                    self.get_sleep(20) #try after some secs
                    flag = False
                    
                    try:
                        self.clickNextButton() #click on next button after refresh
                        self.get_sleep(delay) #wait for sec
                        
                    except TimeoutException as e:

                        print("No more pages.")

                        # Remove the extra comma and newline character
                        fw.seek(0, 2)              # seek to end of file; f.seek(0, os.SEEK_END) is legal
                        fw.seek(fw.tell() - 3, 0)  # seek to the second last char of file; f.seek(f.tell()-2, os.SEEK_SET) is legal
                        fw.truncate()

                        # write the clsoing bracket of the JSON array
                        fw.write(']') 

                        break  

            
            page_cnt+=1 # increment
            
        fw.close()

        
if __name__ == "__main__":

  credentials = { 'email': 'your.email.associated.with.glassdoor@domain',  'password': 'PasswordForYourGlassdoorAccount' }

  # Creating Glassdoor object 
  g = Glassdoor(credentials)

  #Log-in to glassdoor
  g.logIn()

  #Sleep for a while 
  g.get_sleep(10)

  #Get interview posts
  g.get_all_interviews()

  #Close the driver
  g.driver_close()
