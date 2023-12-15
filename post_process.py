import os
import glob
import numpy as np
import pandas as pd
from IPython import embed
import re
from src import dataset 

def read_file(file_name):
    print(f'Reading {file_name}..')
    with open(file_name, 'r') as f:
        lines = f.readlines()
    return lines

def find_start_index(lines):
    # Define a regular expression pattern to match the start_index
    pattern = r'(\d+) to '
    found = False
    for line in lines:
        if 'args' in line:
            print(f'Skipping checked args line, as it is not up-to-date')
            continue
        # Use re.search() to find the match
        match = re.search(pattern, line)

        # Check if a match was found
        if match:
            start_index = int(match.group(1))  # Convert the matched group to an integer
            print(f"Start Index: {start_index}")
            found = True
    if not found:
        print("No match found")
        start_index = None
    return start_index

def extract_answers(lines):
    answer_indices = []
    answer_index = 0
    #return matching_lines 
    # Regular expression pattern to match the desired lines
    # and capture the answer choice
    pattern = re.compile(r'([A-Z]):') # answer|choice|
    error_pattern = re.compile(r'current at index = (\d+)\n')
    no_letter_pattern = re.compile(r'^\["[^"]+"\]$')
    previous_error_index = None
    matching_info = []

    for line in lines:
        if "metadata" in line:
            continue
        match = pattern.search(line)
        if match:
            # Extract the choice
            choice = match.group(1)
            if choice is None:
                print(match)
            answer_indices.append(answer_index)
            answer_index += 1
            matching_info.append((line, choice))
        else:
            # for some error lines we need to skip and update the answer index to
            # ensure alignment of preds and correct answers
            e_match = error_pattern.search(line)
            if e_match:
                error_index = int(e_match.group(1))
                if previous_error_index is None:
                    previous_error_index = error_index
                else:
                    if previous_error_index != error_index:
                        diff = error_index - previous_error_index
                        previous_error_index  = error_index
                        if diff != 1:
                            print(f'{diff=}')
                        answer_index += 1 # there was an error with a question, so move the index
            elif no_letter_pattern.match(line): 
                print(line)
                answer_index += 1 # no useful answer here
                matching_info.append((line, None))

    return matching_info, answer_indices

def main():
    input_files = glob.glob('logs/log*.txt')
    df = dataset.load_vusmle()
   
    df['predicted_answers'] = None

    for fname in input_files:
        if fname == 'logs/log_1-3.txt':
            continue # old formatting, manually update this 

        lines = read_file(fname)
        start_index = find_start_index(lines)
        answers, answer_indices = extract_answers(lines)


        # SANITY CHECK TO ENSURE THAT GPT answers and DF indices are aligned:
        for answer, index in zip(answers, answer_indices):
            full_answer, letter = answer
            if letter is not None:
                column = f'Choice_{letter}'
                df_index = start_index+index 
                if df_index >= 618: 
                    continue

                df_option = df[column][df_index]
                print(f'{df_option=}')
                print(f'prediction={full_answer}')
        if input('Enter OK to use these preds\n') == 'OK':            
        
            # update predictions in df: 
            for answer, index in zip(answers, answer_indices):
                full_answer, letter = answer
                if letter is not None:
                    column = f'Choice_{letter}'
                    df_index = start_index+index 
                    if df_index >= 618: 
                        continue

                    df_option = df[column][df_index]
                df['predicted_answers'][df_index] = letter

    
    embed()


if __name__ == "__main__":

    main()


