# Python program to demonstrate 
# Conversion of JSON data to 
# dictionary 
  
  
# importing the module 
# next: stringUPPER everything
import json 
import random
import string


# Opening JSON file 
with open('JEOPARDY_QUESTIONS1.json') as json_file: 
    data = json.load(json_file) 
    total = 0
    is_over = False
    print('Pregame Options:\n')
    print("     say 'new' for new game\n")
    print("     say 'quit' to end game\n")
    while is_over == False:
        selection = input()
        if selection == "new":
            print('\nWelcome to Jeopardy!\n')
            print('Enter your name below:\n')
            player_name = input()
            print("\nI'm glad you could join us today, " + player_name + "!\n")
            print("Say 'next' to go to your first question: ")
            total = 0
        elif selection == "next":
            i = random.randint(0, 215000)
            print('\nCategory is " ' + data[i]['category'] + ' "\n')
            print('For ' + data[i]['value'] + '\n')
            print(data[i]['question'] + '\n')
            correct_answer = data[i]['answer']
            correct_answer_UPPER = correct_answer.upper()
            correct_answer = correct_answer.replace("\\", "")
            correct_answer = correct_answer.replace("the", "")
            response = input()
            response = response.upper()

            if response in correct_answer_UPPER and len(response) >= 2:
                question_value = (data[i]['value'])
                remove_chars = ["$", ","]
                for character in remove_chars:
                    question_value = question_value.replace(character, "")
                new_total = int(question_value)
                total = total + new_total
                print('\nCorrect!\n')
            else:
                question_value = (data[i]['value'])
                remove_chars = ["$", ","]
                for character in remove_chars:
                    question_value = question_value.replace(character, "")
                new_total = int(question_value)
                total = total - new_total
                print('\nIncorrect. Correct Answer: What is ' + data[i]['answer'] + '?\n')

            print('Midgame Options:\n')
            print("     say 'new' for new game\n")
            print("     say 'next' for next question\n")
            print("     say 'winnings' to check your winnings\n")
            print("     say 'quit' to end game\n")

        elif selection == "winnings":
            print('\n$' + str(total) + '\n')
            print('Midgame Options:\n')
            print("     say 'new' for new game\n")
            print("     say 'next' for next question\n")
            print("     say 'winnings' to check your winnings\n")
            print("     say 'quit' to end game\n")
        elif selection == "quit":
            print('\nGame Over.\n')
            print(player_name + ', you have won $' + str(total) + '!\n')
            print('Thanks for playing, ' + player_name + '!')
            is_over = True
            exit() 
        else:
            print('\nInvalid command.\n')
            print('Options:\n')
            print("     say 'new' for new game\n")
            print("     say 'next' for next question\n")
            print("     say 'winnings' to check your winnings\n")
            print("     say 'quit' to end game\n")