import json

with open('python/Jeopardy/JEOPARDY_QUESTIONS1.json', 'r') as original_json:
    original_dict = json.load(original_json)

game_dict = {}
q_number = 0
for key in original_dict:
    # exclude questions with pictures, urls, etc...
    if key['category'] is None or key['value'] is None or key['question'] is None:
        valid_question = False
    elif 'http' in key['question']:
        valid_question = False
    elif '<' in key['question']:
        valid_question = False
    elif '/' in key['question']:
        valid_question = False
    elif 'seen here' in key['question']:
        valid_question = False
    else: 
        # modify the points value, omit $ and ,
        # remove_from_value = ["$", ","]
        key["value"] = key["value"].replace("$", "") 
        # modify the answer, omit certain words/characters
        key["answer"] = key["answer"].lower()
        remove_from_answer = ['\\', " the ",')', '(', ' a ']
        for char in remove_from_answer:
            key["answer"] = key["answer"].replace(char, "") 
        key["answer"] = key["answer"].strip()
        # append the question to the dictionary
        game_dict[q_number] = key
        q_number = q_number + 1
        

with open('python/sockets/jp_questions.json', "w") as game_json:
    json.dump(game_dict, game_json)
