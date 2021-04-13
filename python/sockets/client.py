from robot_chat_client import RobotChatClient
import time

name = ""

def test_callback(message_dict):
    global name 
    print('Received dictionary {}'.format(message_dict))
    # print('The message is type {}'.format(message_dict['type']))

    if message_dict['type'] == 'start':
        name = input("What is your name? ")
        print('Sending your name to the server')
        client.send({'type': 'name',
                    'value': name})

    if message_dict['type'] == 'control':
        if message_dict['value'] == name:
            print("I have control")
            points = input("What points? (100, 200, 300) ")
            client.send({'type': 'points',
                    'value': points})

    if message_dict['type'] == 'question':
        print(message_dict['value'])
        buzz = input("Do you wish to answer? (y/n) ")
        buzz_bool = (buzz == 'y')
        client.send({'type': 'buzz',
                    'value': buzz_bool,
                    'name': name})

    if message_dict['type'] == 'prompt':
        if message_dict['value'] == name:
            print("You buzzed first")
            ans = input("What is your answer? ")
            client.send({'type': 'answer',
                        'value': ans,
                        'name': name})
    
    if message_dict['type'] == 'score':
        for key, value in message_dict.items():
            if key != 'type':
                print(key, "has", value, "points")

# Run this script directly to invoke this test sequence
if __name__ == '__main__':
    print('Creating RobotChatClient object')
    client = RobotChatClient('ws://localhost:5001', callback=test_callback)

    time.sleep(0.5)
    

    # print('Waiting for ctrl+c')