import pandas as pd
import json
from IPython import embed

#def split_options(options: list):
#    """
#    Split options like ["A - Betablocker", "B - Calcium channel blocker", ...]
#    to 2 lists like ["A", ..], and ["Betablocker", ..]
#    The first - defines the letter chunk and all the rest (even multiple -) goes into the 
#    choice chunk.
#    """
#    letters = []
#    choices = []
#    for option in options:
#        letter, *choice = option.split('-')
#        print(choice)
#        if len(choice) > 0:
#            choice = '-'.join(choice)
#            print(choice)
#        letters.append(letter.strip())
#        choices.append(choice.strip())
#        assert (len(letter) > 0 and len(choice) >= 0)
#
def split_options(options_list):
    """
    Split options like ["A - Betablocker", "B - Calcium channel blocker", ...]
    to 2 lists like ["A", ..], and ["Betablocker", ..]
    The first - defines the letter chunk and all the rest (even multiple -) goes into the 
    choice chunk.
    """

    letters = []
    options = []

    for opt in options_list:
        parts = opt.split('-', 1)  # split by first occurrence of ' - '
        if len(parts) != 2:
            print(f"Unexpected format: {opt}")
            return None
        letters.append(parts[0].strip())
        options.append(parts[1].strip())

    return letters, options

def load_vusmle(
    path = 'data/visual_usmle/vqas.json'
    ):

    # Load the JSON data
    with open(path, 'r') as f:
        data = json.load(f)


    # Initialize a list to store reorganized problems
    problems_list = []
    all_letters = set()

    # First determine how many letters there are: 
    for i, problem in enumerate(data):
        try:
            letters, options = split_options(problem['options'])	
            all_letters.update(letters)
        except Exception as e:
            print(e)
            print(problem['options'])
            embed()

    # Now we populate a list of dictionaries, one for each problem:
    # Loop through each problem and extract the desired information
    for problem in data:
        d = {}
        d['img_filenames'] = problem['image']
        d['question'] = problem['question']

        letters, options = split_options(problem['options'])
        options_dict = {'Choice_' + letter: option for letter, option in zip(letters, options)}
        # update missing letters for df:
        for letter in all_letters:
            key = 'Choice_' + letter
            if key not in options_dict:
                options_dict[key] = None
        
        d.update(options_dict)
        d['answer'] = problem['answer']

        problems_list.append(d)

    df = pd.DataFrame(problems_list)

    # Extract correct answer letter:
    df['correct_answer'] = df['answer'].apply(lambda s: s.split(':')[0][-1])

    return df
