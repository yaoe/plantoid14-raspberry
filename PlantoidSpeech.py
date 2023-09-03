#!/usr/bin/env python3

# NOTE: this example requires PyAudio because it uses the Microphone class

import speech_recognition as sr

import pyaudio
import wave
import audioop
from collections import deque

from playsound import playsound

from dotenv import load_dotenv

import openai
import requests

import random
import os
import time

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 512
RECORD_SECONDS = 2 #seconds to listen for environmental noise
AUDIO_FILE = "/tmp/temp_reco.wav"
device_index = 6

#define the silence threshold
# THRESHOLD = 250     # Raspberry uses 150
SILENCE_LIMIT = 4   # seconds of silence will stop the recording

TIMEOUT = 15


# Load environment variables from .env file
load_dotenv()
openai.api_key = os.environ.get("OPENAI")
eleven_labs_api_key = os.environ.get("ELEVEN")


headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": eleven_labs_api_key
}

url = "https://api.elevenlabs.io/v1/text-to-speech/o7lPjDgzlF8ZloHzVPeK"


def default_prompt_config():
    return {
        "model": "gpt-4",
        "temperature": 0.5,
        "max_tokens": 128,
        "logit_bias": {
            198: -100  # prevent newline
        }
    }



def GPTmagic(prompt): 

    # Prepare the GPT magic

    configs = default_prompt_config()

    # Generate the response from the GPT model
    response = openai.ChatCompletion.create(messages=[{"role": "user", "content": prompt}], **configs)

    messages = response.choices[0].message.content
    print(messages); 
    return messages;


def GPT3magic(prompt):
    # The GPT-3.5 model ID you want to use
    model_id = "text-davinci-003"

    # The maximum number of tokens to generate in the response
    max_tokens = 1024

    # Generate the response from the GPT-3.5 model
    response = openai.Completion.create(
        engine=model_id,
        prompt=prompt,
        max_tokens=max_tokens
    )

    return response




def speaktext(text):
    # Request TTS from remote API
    response = requests.post(url, json={"text": text, "voice_settings": {"stability": 0, "similarity_boost": 0}}, headers=headers)

    if response.status_code == 200:
        # Save remote TTS output to a local audio file with an epoch timestamp
        filename = f"/tmp/tonyspeak.mp3"
        with open(filename, "wb") as f:
            f.write(response.content)
        
        # playsound(filename)
        return filename	
    else:
        print("Error: " + str(response.status_code))



def adjSoundEnv(stream): ## important in order to adjust the THRESHOLD based on environmental noise
    
    data = []
    noisy = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        noisy.append(abs(audioop.avg(data, 2)))
 
    current_noise =  sum(noisy) / len(noisy)
    print("current noise = " + str(current_noise))

    return current_noise




def listenSpeech(): # @@@ remember to add acknowledgements afterwards

    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
		        # input_device_index = device_index,
                frames_per_buffer=CHUNK)

    noisy = adjSoundEnv(stream)

    THRESHOLD = 0

    ## range should be:  if noisy is 10 = 50; if noisy = 100 = 250;
    if(noisy < 10): THRESHOLD = 50
    if(noisy > 10 and noisy < 20): THRESHOLD = 100
    if(noisy > 20 and noisy < 30): THRESHOLD = 140
    if(noisy > 30 and noisy < 40): THRESHOLD = 160
    if(noisy > 40 and noisy < 50): THRESHOLD = 170
    if(noisy > 50 and noisy < 60): THRESHOLD = 200
    if(noisy > 60 and noisy < 70): THRESHOLD = 300
    if(noisy > 70): THRESHOLD = 350



    samples = []

    chunks_per_second = RATE / CHUNK

    silence_buffer = deque(maxlen=int(SILENCE_LIMIT * chunks_per_second))
    samples_buffer = deque(maxlen=int(SILENCE_LIMIT * RATE))

    started = False

    ### this is for a fixed amount of recording seconds
    #    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    #        data = stream.read(CHUNK)
    #        samples.append(data)

    ### this is for continuous recording, until silence is reached

    run = 1

    timing = None

    while(run):
        data = stream.read(CHUNK)
        silence_buffer.append(abs(audioop.avg(data, 2)))

        samples_buffer.extend(data)

        if (True in [x > THRESHOLD for x in silence_buffer]):
            if(not started):
                print ("recording started")
                started = True
                samples_buffer.clear()
                timing = time.time()

            samples.append(data)

            # check for timeout
            if(time.time() - timing > TIMEOUT):
                print("stopping recording because of timeout @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                stream.stop_stream()

                recwavfile(samples, audio)

                #reset all vars
                started = False
                silence_buffer.clear()
                samples = []

                run = 0


        elif(started == True):   ### there was a long enough silence
            print ("recording stopped")
            stream.stop_stream()
            
            recwavfile(samples, audio)

            #reset all vars
            started = False
            silence_buffer.clear()
            samples = []

            run = 0

    stream.close()
    audio.terminate()

    return AUDIO_FILE


def recwavfile(data, audio):

    wf = wave.open(AUDIO_FILE, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(data))
    wf.close()


def recoSpeech(filename):
    
    print("trying to recognize from ... " + filename)

    with sr.AudioFile(filename) as source:

        r = sr.Recognizer()
        r.energy_threshold = 50
        r.dynamic_energy_threshold = False

        audio = r.record(source)
        usertext = "";
        
        try:
            usertext = r.recognize_google(audio)

        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")

        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))


        return usertext
    
