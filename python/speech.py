#!/usr/bin/env python3

# NOTE: this example requires PyAudio because it uses the Microphone class

import speech_recognition as sr
import pyaudio
# obtain audio from the microphone
r = sr.Recognizer()
p = pyaudio.PyAudio()
for ii in range(p.get_device_count()):
    if "USB PnP Sound Device" in p.get_device_info_by_index(ii).get("name") :
        mic_device_index = ii
        break

with sr.Microphone(device_index=mic_device_index) as source:
    print("Say something!")
    audio = r.listen(source)


# recognize speech using Google Speech Recognition
try:
    # for testing purposes, we're just using the default API key
    # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
    # instead of `r.recognize_google(audio)`
    print("Google Speech Recognition thinks you said:\n" + r.recognize_google(audio))
except sr.UnknownValueError:
    print("Google Speech Recognition could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Google Speech Recognition service; {0}".format(e))
