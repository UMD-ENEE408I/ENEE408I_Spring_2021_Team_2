import json 
import random
import string

from datetime import date

today = date.today()


# Opening JSON file 
with open('JEOPARDY_QUESTIONS1.json') as json_file: 
    data = json.load(json_file) 
    total = 0
    j = 0
    k = 0
    found = 0
    has_high_score = False
    num_correct = 0
    num_incorrect = 0
    questions_total = 0
    questions_in_round = 0
    percent_correct = 0.0
    wager = 0
    is_over = False
    is_able_to_play_FINALJEOP = True
    print("Say 'new' to begin new game.\n")
    while is_over == False:
        selection = input()
        if selection == "new":
            print('\nWelcome to Jeopardy!\n')
            print('Enter your name below:\n')
            player_name = input()
            print("\nI'm glad you could join us today, " + player_name + "!\n")
            print("Remember, you can type PASS to pass your question response.\n")
            print("Say 'next' to go to your first question: \n")
            total = 0
        elif selection == "next":
            valid_question = False
            while valid_question == False:
                i = random.randint(0, 215000)
                if data[i]['category'] is None or data[i]['value'] is None or data[i]['question'] is None:
                    valid_question = False
                elif 'http' in data[i]['question']:
                    valid_question = False
                elif '<' in data[i]['question']:
                    valid_question = False
                elif '/' in data[i]['question']:
                    valid_question = False
                elif 'seen here' in data[i]['question']:
                    valid_question = False
                else: 
                    valid_question = True
            
            print('\nCategory is " ' + data[i]['category'] + ' "\n')
            print('For ' + data[i]['value'] + '\n')
            print(data[i]['question'] + '\n')
            correct_answer = data[i]['answer']
            correct_answer_UPPER = correct_answer.upper()
            correct_answer = correct_answer.replace("\\", "")
            correct_answer = correct_answer.replace("the", "")
            questions_in_round += 1
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
                num_correct += 1

            elif response == "PASS":
                print('\n'+ player_name + ' has passed. Correct Answer: What is ' + data[i]['answer'] + '?\n')
                print(player_name + ' will stay at $' + str(total) + '.\n')

            else:
                question_value = (data[i]['value'])
                remove_chars = ["$", ","]
                for character in remove_chars:
                    question_value = question_value.replace(character, "")
                new_total = int(question_value)
                total = total - new_total
                print('\nIncorrect. Correct Answer: What is ' + data[i]['answer'] + '?\n')
                num_incorrect += 1

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
            #Negative amounts of money in Final Jeopardy?
            if total <= 0:
                is_able_to_play_FINALJEOP = False
                print('')
            else:
                print("\nWelcome to Final Jeopardy, " + player_name + "!\n")
                valid_question = False
                while valid_question == False:
                    i = random.randint(0, 215000)
                    if data[i]['category'] is None or data[i]['value'] is None or data[i]['question'] is None:
                        valid_question = False
                    elif 'http' in data[i]['question']:
                        valid_question = False
                    elif '<' in data[i]['question']:
                        valid_question = False
                    elif '/' in data[i]['question']:
                        valid_question = False
                    elif 'seen here' in data[i]['question']:
                        valid_question = False
                    else:
                        question_value = (data[i]['value'])
                        remove_chars = ["$", ","]
                        for character in remove_chars:
                            question_value = question_value.replace(character, "")
                        question_value = int(question_value)
                        if question_value < 2001:
                            valid_question = False
                        else: 
                            valid_question = True
                        

                print('The Final Jeopardy Category is " ' + data[i]['category'] + ' "\n')
                print('You have $' + str(total) + '. Wager any integer value between 0 and ' + str(total) + ' below:\n')
                valid_wager = False
                while valid_wager == False:
                    wager = input()
                    wager = int(wager)
                    if wager >= 0 and wager <= total:
                        valid_wager = True
                    else:
                        print('\nInvalid Wager. You have $' + str(total) + '. Wager any integer value between 0 and ' + str(total) + ' below:\n')

                print('\nFor $' + str(wager) + ':\n')
                print(data[i]['question'] + '\n')
                correct_answer = data[i]['answer']
                correct_answer_UPPER = correct_answer.upper()
                correct_answer = correct_answer.replace("\\", "")
                correct_answer = correct_answer.replace("the", "")
                response = input()
                response = response.upper()

                if response in correct_answer_UPPER and len(response) >= 2:
                    total = total + wager
                    print('\nCorrect!\n')
                    num_correct += 1
                else:
                    total = total - wager
                    print('\nIncorrect. Correct Answer: What is ' + data[i]['answer'] + '?\n')
                    num_incorrect += 1

            print('Game Over.\n')
            print(player_name + ', you have won $' + str(total) + '!\n')
            print('Thanks for playing, ' + player_name + '!\n')
            is_over = True
            questions_total = num_incorrect + num_correct #doesnt include passed questions
            percent_correct = round(((num_correct)/(num_correct + num_incorrect)*100), 2)
            with open('jeopardy_stats.JSON') as stats_file: 
                stats = json.load(stats_file)
                last_player_recorded = len(stats["player"])
                while j < last_player_recorded:
                    if player_name.upper() == stats["player"][j]["name"]:
                        found = 1
                        stats["player"][j]["all_time_winnings"] = stats["player"][j]["all_time_winnings"] + total
                        stats["player"][j]["correct_questions"] = stats["player"][j]["correct_questions"] + num_correct
                        stats["player"][j]["incorrect_questions"] = stats["player"][j]["incorrect_questions"] + num_incorrect
                        stats["player"][j]["total_questions"] = stats["player"][j]["total_questions"] + questions_total
                        stats["player"][j]["percent_correct"] = round((stats["player"][j]["correct_questions"] / stats["player"][j]["total_questions"] * 100), 2)
                    j += 1
                if found == 0:
                    stats["player"].append({
                        'name': player_name.upper(),
                        'all_time_winnings': int(total),
                        'correct_questions': int(num_correct),
                        'incorrect_questions': int(num_incorrect),
                        'total_questions': int(questions_total),
                        'percent_correct': float(percent_correct),
                    })

                if total > stats["High Scores"][0]["high_score"] or total > stats["High Scores"][1]["high_score"] or total > stats["High Scores"][2]["high_score"] or total > stats["High Scores"][3]["high_score"] or total > stats["High Scores"][4]["high_score"]:
                    get_date = today.strftime("%B %d, %Y")
                    stats["High Scores"].append({
                        'name': player_name.upper(),
                        'high_score': int(total),
                        'num_correct_round': int(num_correct),
                        'questions_in_round': int(num_correct+num_incorrect),
                        'high_score_date': get_date
                    })
                    stats["High Scores"] = sorted(stats["High Scores"], key=lambda k: k['high_score'], reverse=True)
                    del stats["High Scores"][5]

                    print("**********NEW HIGH SCORE**********\n")
                    print(stats["High Scores"][0]["name"] + "\t$" + str(stats["High Scores"][0]["high_score"]) + "\ton " + stats["High Scores"][0]["high_score_date"] + " (" + str(stats["High Scores"][0]["num_correct_round"]) + "/" + str(stats["High Scores"][0]["questions_in_round"]) + " questions)")
                    print(stats["High Scores"][1]["name"] + "\t$" + str(stats["High Scores"][1]["high_score"]) + "\ton " + stats["High Scores"][1]["high_score_date"] + " (" + str(stats["High Scores"][1]["num_correct_round"]) + "/" + str(stats["High Scores"][1]["questions_in_round"]) + " questions)")
                    print(stats["High Scores"][2]["name"] + "\t$" + str(stats["High Scores"][2]["high_score"]) + "\ton " + stats["High Scores"][2]["high_score_date"] + " (" + str(stats["High Scores"][2]["num_correct_round"]) + "/" + str(stats["High Scores"][2]["questions_in_round"]) + " questions)")
                    print(stats["High Scores"][3]["name"] + "\t$" + str(stats["High Scores"][3]["high_score"]) + "\ton " + stats["High Scores"][3]["high_score_date"] + " (" + str(stats["High Scores"][3]["num_correct_round"]) + "/" + str(stats["High Scores"][3]["questions_in_round"]) + " questions)")
                    print(stats["High Scores"][4]["name"] + "\t$" + str(stats["High Scores"][4]["high_score"]) + "\ton " + stats["High Scores"][4]["high_score_date"] + " (" + str(stats["High Scores"][4]["num_correct_round"]) + "/" + str(stats["High Scores"][4]["questions_in_round"]) + " questions)\n")
                
                with open('jeopardy_stats.JSON', 'w') as stats_file:
                    json.dump(stats, stats_file, indent=2)
            exit() 
        else:
            print('\nInvalid command.\n')
            print('Options:\n')
            print("     say 'new' for new game\n")
            print("     say 'next' for next question\n")
            print("     say 'winnings' to check your winnings\n")
            print("     say 'quit' to end game\n")