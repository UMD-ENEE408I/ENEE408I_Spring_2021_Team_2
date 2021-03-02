# Python program to demonstrate 
# Conversion of JSON data to 
# dictionary 
  
  
# importing the module 
# next: stringUPPER everything
# different way to loop
import json 
import random
import string


# Opening JSON file 
with open('JEOPARDY_QUESTIONS1.json') as json_file: 
    data = json.load(json_file) 
    total = 0
    if input() == "next question":
        i = random.randint(0, 215000)
        print('\nCategory is " ' + data[i]['category'] + ' "\n')
        print('For ' + data[i]['value'] + '\n')
        print(data[i]['question'] + '\n')
        correct_answer = data[i]['answer']
        correct_answer = correct_answer.replace("\\", "")
        correct_answer = correct_answer.replace("the", "")

        if correct_answer in input():
            question_value = (data[i]['value'])
            nodollarsign_value = question_value.replace("$", "")
            new_total = int(nodollarsign_value)
            total = total + new_total
            print('\nCorrect!\n')
        else:
            question_value = (data[i]['value'])
            nodollarsign_value = question_value.replace("$", "")
            new_total = int(nodollarsign_value)
            total = total - new_total
            print('\nIncorrect. Correct Answer: What is ' + data[i]['answer'] + '?\n')

    elif input() == "check winnings":
        print('\n$' + str(total) + '\n')
    elif input() == "quit":
        print('Game Over. Thanks for playing!')
        exit() 