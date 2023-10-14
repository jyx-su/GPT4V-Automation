# GPT4V-Automation

## Getting json file for login status

1. Create a new conda environment, and `pip install pytest-playwright; playwright install`
2. Modify the saving path at Line 11 of get_login_status.py
3. Estimate how much time you need for the following steps, modify the delay at Line 10
4. Run `python3 get_login_status.py`
5. Login to ChatGPT using the poped window
6. Remember to turn off chat history by clicking the three dots next to your username (bottom left)
7. Click "Settings & Beta", then "Data controls", toggle off "Chat history & training"
8. Verify "New Chat" button has changed to "Clear Chat"

## Preparing the dataframe for data loading
1. Prepare a csv file for data loading.
2. Examples of columns to be included: img_filenames, case_id, answer options.

## Modifying the prompt template in the code
