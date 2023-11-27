import pandas as pd
from playwright.sync_api import Playwright, sync_playwright
import pickle
from datetime import datetime, timedelta
import traceback
import re
import os
import time

def get_playwright(playwright: Playwright, headless, login_json_path) -> None:
    browser = playwright.firefox.launch(headless=headless, timeout=0)
    context = browser.new_context(storage_state=login_json_path)
    page = context.new_page()
    page.goto("https://chat.openai.com/?model=gpt-4")
    #page.pause()
    print(f'{str(datetime.now())} Loaded ChatGPT')
    return page, context, browser


class GPT():
    def __init__(self, model, state_json_file, headless = False, no_history=True):
        self.model = model
        self.no_history = no_history
        self.playwright = sync_playwright().start()
        self.login_json_path = state_json_file
        self.page, self.context, self.broswer = get_playwright(self.playwright, headless, state_json_file)
        self.need_fresh = False

    def refresh_page(self):
        self.context = self.browser.new_context(storage_state=self.login_json_path)
        self.page = self.context.new_page()
        self.page.goto("https://chat.openai.com/?model=gpt-4")
        #page.pause()
        print(f'{str(datetime.now())} Loaded ChatGPT')


    def finish(self):
        self.context.close()
        self.browser.close()


    def get_response(self, prompt, filename=None):
        page = self.page
        
        try:
            if self.no_history:
                try:
                    page.get_by_role("link", name="Clear chat").click(timeout=5000)
                except:
                    pass
            else:
                page.locator("a").filter(has_text=re.compile(r"^New Chat$")).click()
            
            if filename is not None:
                with page.expect_file_chooser(timeout=5000) as fc_info:
                    page.get_by_label("Attach files").click()
                file_chooser = fc_info.value
                file_chooser.set_files(filename)
            
            page.get_by_placeholder("Message ChatGPT…").click()
            page.get_by_placeholder("Message ChatGPT…").fill(prompt)
            page.get_by_test_id("send-button").click()
            page.wait_for_timeout(1000)
            def check_finish_generation():
                if page.get_by_label('Stop generating').count()>0:
                    return False
                return True
            
            count = 0
            while not check_finish_generation():
                count += 1
                page.wait_for_timeout(2000)
                if count == 30: #Waited 1 min
                    raise Exception('Generation timeout')
            response = []
            for i in page.locator('.markdown').all():
                response.append(i.inner_text())
            print(response)
            return response[0]
        except Exception as e:
            traceback.print_exc()#file=sys.stdout)
            if page.get_by_text('Regenerate').count()>0: #Generation error
                return self.get_response(prompt, filename)
            breakpoint()
            return None
            page_str = str(self.page.content())
            start_index = page_str.find("You've reached the current usage cap for GPT-4.")
            if start_index == -1:
                self.page.screenshot(path=f'ERROR_{str(datetime.now())}.png')
            else:
                logic_for_timeout(page_str)
    



def logic_for_timeout(page_str):
    start_index = page_str.find("You've reached the current usage cap for GPT-4.")
    message_str = page_str[start_index:min(len(page_str), start_index+150)]
    pattern = r'\b\d{1,2}:\d{2}\s?[APap][Mm]\b'
    matches = re.findall(pattern, message_str)
    if len(matches) != 1:
        print(f'Sorry multiple times found. Unexpected! {matches}')
    
    print(f'Usage limit reached. Resume at {matches[0]}. Details: {message_str}')
    target_time_str = matches[0]
    target_time = datetime.strptime(target_time_str, "%I:%M %p")

    # Get the current date and time
    current_datetime = datetime.now()

    # Combine the current date with the target time
    target_datetime = current_datetime.replace(hour=target_time.hour, minute=target_time.minute, second=0)

    # Check if the target time is in the past for today
    if target_datetime < current_datetime:
        # If it's in the past, add one day to target_datetime
        target_datetime += timedelta(days=1)

    # Calculate the time difference (timedelta)
    time_difference = target_datetime - current_datetime

    # Calculate the number of seconds until the target time
    seconds_until_target = time_difference.total_seconds()
    print(f'Now sleep for {seconds_until_target + 121} seconds index')
    time.sleep(seconds_until_target + 121)
