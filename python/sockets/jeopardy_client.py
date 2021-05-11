from robot_chat_client import RobotChatClient
import time
from gtts import gTTS
from playsound import playsound
import os
import speech_recognition as sr
import pyaudio
from PingThread import PingThread
from threading import Thread
import json

name = ""

def speak(statement):
    gts = gTTS(text=statement,lang='en')
    gts.save("audio.mp3")
    playsound("audio.mp3")
    os.remove("audio.mp3")
    print(statement)

def get_audio(default="unknown"):
    global r
    global mic_device_index

    with sr.Microphone(device_index=mic_device_index) as source:
        audio = r.listen(source)
        try:
            string = r.recognize_google(audio)
        except:
            speak("I didn't understand that, could you repeat?")
            audio = r.listen(source)
            try:
                string = r.recognize_google(audio)
            except:
                speak("I didn't understand that again, giving default value")
                return default

    return string

def get_response(response_list=[]):
    response = ""
    if response_list != []:
        string = get_audio(default=response_list[0])
        if string not in response_list:
            string = response_list[0]
    else:
        string = get_audio()
    return string.lower()

def test_callback(message_dict):
    global name
    global r
    global mic_device_index
    print('Received dictionary {}'.format(message_dict))
    # print('The message is type {}'.format(message_dict['type']))

    # respond to different types of messages from the server

    # start type message is sent when lobby size is met - user is prompted for name
    if message_dict['type'] == 'start':
        speak("what is your name?")
        name = get_response()
        # name = input("What is your name? ")
        print('Sending your name to the server, ' + name)
        client.send({'type': 'name',
                    'value': name})
        pingThread.set_name(name)
        pingThread.start()

    # control type message is sent to prompt one user for the point value for the next question
    if message_dict['type'] == 'control':
        print(message_dict)
        # give the previous answer if it is supplied (not the first question)
        if  message_dict["prev answer"] != {}:
            ans_dict = message_dict["prev answer"]
            prev_ans_str = "The previous answer was " + ans_dict["answer"] + ". " + ans_dict["answered_by"] + " got this correct. "
        else: 
            prev_ans_str = ""
        control_str = message_dict['control info']['value'] + " is selecting a point value."
        speak(prev_ans_str + control_str)

        if message_dict['control info']['value'] == name:
            speak("Select a point value.")
            response_list = ['100', '200', '300', '400', '500']
            points = get_response(response_list=response_list)
            # points = input("What points? (100, 200, 300) ")
            client.send({'type': 'points',
                    'value': points})

    # question is sent to each player, everyone must respond yes/no to continue
    if message_dict['type'] == 'question':
        q_info = message_dict['q_info']
        if q_info['daily_double'] == "true":
            speak("This question is the daily double!")
        state_round = "round number " + str(q_info['round_number'])
        state_category = "The category is " + q_info["category"].lower() + "."
        state_value = "The question is worth " + q_info["value"] + " points."
        state_question = q_info['question']
        speak(state_round)
        speak(state_category)
        speak(state_value)
        speak(state_question)
        
        # wait for buzz or pass
        speak("buzz or pass.")
        response_list =  ['pass', 'buzz']
        buzz = get_response(response_list=response_list)
        buzz_bool = ( buzz == 'buzz')

        # audio = input()
        # buzz_bool = (audio.lower() == 'buzz')
        client.send({'type': 'buzz',
                    'value': buzz_bool,
                    'name': name})

    # player that buzzed first is prompted for answer
    if message_dict['type'] == 'prompt':
        if message_dict['value'] == name:
            speak("You buzzed first, what is your answer?")
            ans = get_response()
            # ans = input()
            client.send({'type': 'answer',
                        'value': ans,
                        'name': name})
    
    # this is the one I couldnt get to work yet (line 98 in server)
    if message_dict['type'] == 'score':
        for key, value in message_dict.items():
            if key != 'type':
                print(key, "has", value, "points")

    # if server tells us the game is over
    if message_dict['type'] == 'game over':
        ans_dict = message_dict["final_answer"]
        prev_ans_str = "The previous answer was " + ans_dict["answer"] + ". " + ans_dict["answered_by"] + " got this correct. "
        speak(prev_ans_str)
        speak("GAMEOVER")
        standings = {k: v for k, v in sorted(message_dict['scores'].items(), key=lambda item: item[1])}
        scores_string = "The final scores are... "
        for player in standings:
            scores_string = scores_string + player + " with " + str(standings[player]) + " points. "
        speak(scores_string)

        with open("jeopardy_high_scores.json", 'w+') as f_high_scores:
            if os.path.getsize("jeopardy_high_scores.json") != 0:
                high_score_dict = json.load(f_high_scores)
            else:
                high_score_dict = {}
            for player in message_dict['scores']:
                high_score_dict[message_dict['scores'][player]] = player
                json.dump(high_score_dict, f_high_scores)



# Run this script directly to invoke this test sequence
if __name__ == '__main__':
    print('Creating RobotChatClient object')
    r = sr.Recognizer()
    p = pyaudio.PyAudio()
    for ii in range(p.get_device_count()):
        if "USB PnP Sound Device" in p.get_device_info_by_index(ii).get("name") :
            mic_device_index = ii
            break

    server_ip = "ws://3.128.26.29:5001"
    # server_ip = 'ws://localhost:5001'
    client = RobotChatClient(server_ip, callback=test_callback)
    pingThread = PingThread(client)


    
    

    # print('Waiting for ctrl+c')