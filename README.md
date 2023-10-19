# GPT4V-Automation

## Getting json file for login status

1. Create a new conda environment, and `pip install pytest-playwright thefuzz pandas; playwright install`
2. Modify the saving path at Line 11 of get_login_status.py
3. Estimate how much time you need for the following steps, modify the delay at Line 10
4. Run `python3 get_login_status.py`
5. Login to ChatGPT using the popped window
6. Remember to turn off chat history by clicking the three dots next to your username (bottom left)
7. Click "Settings & Beta", then "Data controls", toggle off "Chat history & training"
8. Verify "New Chat" button has changed to "Clear Chat"

## Preparing the dataframe for data loading
1. Prepare a csv file for data loading.
2. Examples of columns to be included: img_filenames, case_id, answer options.

## Modifying the configuration and prompt template in the code
1. Modify Line 8-13, 24, 72-75 in "GPT4VAutomation_cleaned.py"
2. Run `python3 GPT4VAutomation_cleaned.py`

## Analyze the collected results



### Side notes
1. If it's your first time running `GPT4VAutomation_cleaned.py` , I'll recommend you to change Line 85 to `headless=False` so that you can see it in action (to make sure it's working as expected)
2. Please ping me if you encounter any issue. I've only tested it on MacOS, and I'll appreciate if any of you using Windows can tell me whether it works or not




### V-USMLE (Michael)   

```python test.py``` 

