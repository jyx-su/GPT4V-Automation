#Modify Line 8-13, 24, 72-75
import pandas as pd
from playwright.sync_api import Playwright, sync_playwright
import pickle
from datetime import datetime, timedelta
import re, time, os
import argparse

from src import dataset 

def validate_inputs(data_df, args):
    # sanity check:
    n = len(data_df)
    chunk_index = args.chunk_index
    if chunk_index > 0:
        n_prev_completed_chunks = len(range(chunk_index))
        n_prev_completed_problems = n_prev_completed_chunks * args.chunk_size
        if n_prev_completed_problems >= n:
            raise ValueError(f'chunk_index {chunk_index} is too large, there are only {n} problems in the dataset')
        print(f'Checked args: processing problems {n_prev_completed_problems} to {n_prev_completed_problems+args.chunk_size} of {n}')
    else:
        n_problems_to_process = min(len(data_df), args.chunk_size) 
        print(f'Checked args: processing problems 0 to {n_problems_to_process} of {n}')

parser = argparse.ArgumentParser()

parser.add_argument('--chunk_index', type=int, default=0, help='which chunk of the dataset to process')
parser.add_argument('--chunk_size', type=int, default=25, help='number of problems to process in a given program execution')
parser.add_argument('--debug', default=0, help='debug mode, only on 3 samples')

args = parser.parse_args()


#data_df = pd.read_csv('/path/to/dataframe (csv file)', index_col=0)
data_df = dataset.load_vusmle()

#tup = data_df.iloc[0]
#from IPython import embed; embed(); sys.exit()

#Some pre-processing like generate image paths, filter cases etc.
data_df = data_df[data_df['img_filenames'] != '']

validate_inputs(data_df, args)

if args.debug:
    # subset data for testing:
    data_df = data_df[:3]
else:
    # select current indices based on chunk index and size:
    start_index = args.chunk_index * args.chunk_size
    end_index = start_index + args.chunk_size

    # overwrite for quick hack:
    start_index = 3 #275
    end_index = 50 #None
    data_df = data_df[start_index:end_index]
    print(f'>>> Processing problems {start_index} to {end_index}')


imgpath_prefix = 'data/visual_usmle'
data_df['imgpath'] = imgpath_prefix + data_df['img_filenames'] #The column 'imgpath' will be used to upload images

#Sanity check to ensure all image paths are valid
for i in range(len(data_df)):
    if not os.path.isfile(str(data_df.iloc[i]['imgpath'])):
        print(f'Invalid imgpath at iloc of {i}, imgpath = {data_df.iloc[i]["imgpath"]}')
print(data_df.head())

#Configurations
model = "GPT-4" #Or "GPT-3.5"
no_history = True #True for no history
login_json_path = "state.json" #should be a json file containing login status
disable_image = False
exp_prefix = 'multi'
start_idx = 0


def single_chat(page, tup):
    if no_history:
        try:
            page.get_by_role("button", name="Okay, let’s go").click(timeout=5000)
        except:
            pass
        page.locator("a").filter(has_text=re.compile(r"^Clear chat$")).click()
    else:
        page.locator("a").filter(has_text=re.compile(r"^New Chat$")).click()
    page.get_by_role("button", name=model).click()
    if not no_history:
        page.get_by_role("menuitemradio", name="Default").click()

    filename = tup['imgpath']

    def single_turn(filename, prompt, disable_image = disable_image):
        if no_history: #Close the explanation for attach images
            try:
                page.get_by_role("dialog").get_by_role("button").click(timeout=1000)
            except:
                pass

        if filename != '' and not disable_image:
            with page.expect_file_chooser(timeout=5000) as fc_info:
                page.get_by_label("Attach files").click()
            file_chooser = fc_info.value
            file_chooser.set_files(filename)
        
        page.get_by_placeholder("Send a message").click()
        page.get_by_placeholder("Send a message").fill(prompt)
        page.get_by_test_id("send-button").click()
        page.wait_for_timeout(1000)
        result = page.locator('xpath=//*[@id="__next"]/div[1]/div[2]/main/div[1]/div[2]/form/div/div[1]/div/div[2]/div/button').inner_text()
        
        while result == 'Stop generating':
            page.wait_for_timeout(1000)
            result = page.locator('xpath=//*[@id="__next"]/div[1]/div[2]/main/div[1]/div[2]/form/div/div[1]/div/div[2]/div/button').inner_text()
        if result == 'Regenerate':
            pass#print('Done')
        else:
            print(f'ERROR: {result}')

    # subset choices that are not None:
    choice_keys = [key for key in tup.keys() if key.startswith('Choice_')]
    choice_prompt = []
    for key in choice_keys:
        if tup[key]:
            s = key.split('_')[-1] + ': ' + tup[key]
            choice_prompt.append(s)
    choice_prompt = ', '.join(choice_prompt)

    single_turn(filename, f"""You are an AI doctor trained in general medicine. You are given a medical question and an image as context, together with a list of possible answer choices. Only one of the choices is correct. Select the correct choice, and give the answer as a short response. Do not explain.
    Question: {tup['question']}
    Choices: {choice_prompt} 
    """)

    response = []
    for i in page.locator('.markdown').all():
        response.append(i.inner_text())
    print(response)
    return response


def run(playwright: Playwright) -> None:
    browser = playwright.firefox.launch(headless=False, timeout=0) #headless=True 
    context = browser.new_context(storage_state=login_json_path)
    page = context.new_page()
    page.goto("https://chat.openai.com/")
    print(f'{str(datetime.now())} Loaded ChatGPT')
    results = {'metadata': {'model': model, 'imgpath_prefix': imgpath_prefix, 'no_history': no_history, 'login_json_path': login_json_path, 'disable_image': disable_image, 'start_idx': start_idx, 'exp_prefix': exp_prefix}}

    last_save = -1
    for i in range(start_idx, len(data_df)):
        tup = data_df.iloc[i]
        for re_try in range(3): #Max retry is 3 times
            try:
                results[tup['imgpath']] = single_chat(page, tup)
            except Exception:
                page_str = str(page.content())
                start_index = page_str.find("You've reached the current usage cap for GPT-4.")
                if start_index != -1:
                    message_str = page_str[start_index:min(len(page_str), start_index+150)]
                    pattern = r'\b\d{1,2}:\d{2}\s?[APap][Mm]\b'
                    matches = re.findall(pattern, message_str)
                    if len(matches) != 1:
                        print(f'Sorry multiple times found. Unexpected! {matches}')
                    
                    print(f'Usage limit reached, current at index = {i} Resume at {matches[0]}. Details: {message_str}')
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
                    print(f'Now sleep for {seconds_until_target + 121} seconds')
                    with open(f'hitlimitsave_{exp_prefix}_{str(datetime.now())}.pkl', 'wb') as f:
                        pickle.dump(results, f)
                    time.sleep(seconds_until_target + 121)
                    print(f"{str(datetime.now())} Let's continue")
                else: #Unexpected error (server error, image upload error etc.), save the results and a screenshot
                    page.screenshot(path=f'ERROR_{exp_prefix}_{str(datetime.now())}.png')
                    if len(results) > last_save: #Don't save if no new result
                        with open(f'response_ERROR_{str(datetime.now())}.pkl', 'wb') as f:
                            pickle.dump(results, f)
                        last_save = len(results)

                page.goto("https://chat.openai.com/")
                print(f"{str(datetime.now())} Loaded ChatGPT, current at index = {i}")
                continue
            break #Success, break out of the retry loop
        time.sleep(0.5)


    print(results)
    with open(f'response_{exp_prefix}_{str(datetime.now())}.pkl', 'wb') as f:
        pickle.dump(results, f)
    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
