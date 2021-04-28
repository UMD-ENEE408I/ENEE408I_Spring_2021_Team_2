from robot_chat_client import RobotChatClient
import time
from gtts import gTTS
from playsound import playsound
import os
import speech_recognition as sr
import pyaudio



name = ""

def speak(statement):
    gts = gTTS(text=statement,lang='en')
    gts.save("audio.mp3")
    playsound("audio.mp3")
    os.remove("audio.mp3")

def test_callback(message_dict):
    global name 
    print('Received dictionary {}'.format(message_dict))
    # print('The message is type {}'.format(message_dict['type']))

    # respond to different types of messages from the server

    # start type message is sent when lobby size is met - user is prompted for name
    if message_dict['type'] == 'start':
        name = input("What is your name? ")
        print('Sending your name to the server')
        client.send({'type': 'name',
                    'value': name})

    # control type message is sent to prompt one user for the point value for the next question
    if message_dict['type'] == 'control':
        if message_dict['value'] == name:
            points = input("What points? (100, 200, 300) ")
            client.send({'type': 'points',
                    'value': points})

    # question is sent to each player, everyone must respond yes/no to continue
    if message_dict['type'] == 'question':
        q_info = message_dict['q_info']
        # print(message_dict['q_info'])
        state_category = "The category is " + q_info["category"].lower() + "."
        speak(state_category)
        state_value = "The question is worth " + q_info["value"] + " points."
        speak(state_value)
        state_question = q_info['question']
        speak(state_question)
        # print(state_question)
        # wait for buzz or pass
        speak("buzz or pass.")
        with sr.Microphone(device_index=mic_device_index) as source:
            print("Say something!")
            audio = r.listen(source)
            
        buzz_bool = ( r.recognize_google(audio).lower() == 'buzz')
        client.send({'type': 'buzz',
                    'value': buzz_bool,
                    'name': name})

    # player that buzzed first is prompted for answer
    if message_dict['type'] == 'prompt':
        if message_dict['value'] == name:
            print("You buzzed first")
            ans = input("What is your answer? ")
            client.send({'type': 'answer',
                        'value': ans,
                        'name': name})
    
    # this is the one I couldnt get to work yet (line 98 in server)
    if message_dict['type'] == 'score':
        for key, value in message_dict.items():
            if key != 'type':
                print(key, "has", value, "points")

# Run this script directly to invoke this test sequence
if __name__ == '__main__':
    print('Creating RobotChatClient object')
    global r
    global p
    global mic_device_index
    r = sr.Recognizer()
    p = pyaudio.PyAudio()
    for ii in range(p.get_device_count()):
        if "USB PnP Sound Device" in p.get_device_info_by_index(ii).get("name") :
            mic_device_index = ii
            break

    client = RobotChatClient('ws://localhost:5001', callback=test_callback)
    # obtain audio from the microphone
    
    time.sleep(0.5)
    

    # print('Waiting for ctrl+c')