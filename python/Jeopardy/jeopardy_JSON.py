# Python program to demonstrate 
# Conversion of JSON data to 
# dictionary 
  
  
# importing the module 
import json 
import random
  
# Opening JSON file 
with open('JEOPARDY_QUESTIONS1.json') as json_file: 
    data = json.load(json_file) 
  
    # for reading nested data [0] represents 
    # the index value of the list 
    i = random.randint(0, 215000)
    print(' Category is " ' + data[i]['category'] + ' "\n')
    print(data[i]['question'] + '\n')
    print('What is  ' + data[i]['answer'] + '?\n')
    print(data[i]['value'] + '\n')