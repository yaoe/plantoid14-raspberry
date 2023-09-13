import random
import pygame
from playsound import playsound
import os
import threading
import time

from lib.plantoid.text_content import get_text_content
import lib.plantoid.speech as PlantoidSpeech
import lib.plantoid.serial_setup as PlantoidSerial

class Plantony:

    def __init__(self):

        self.USER = "Human"
        self.AGENT = "Plantoid"

        self.use_arduino = False

        self.opening = ""
        self.closing = ""
        self.prompt_text = ""
        # TODO: figure out how to encapsulate interaction groups into a single turn without modifying the array length if not 
        # for the creation of a new cycle

        # a round will contain a series of turns
        self.rounds = [[]]

        # # a turn will contain a series of interactions
        # self.turns = []

        # load the text content
        self.opening_lines, self.closing_lines, self.word_categories = get_text_content()

        # Load the sounds
        self.acknowledgements = [
            os.getcwd()+"/media/hmm1.mp3",
            os.getcwd()+"/media/hmm2.mp3",
        ];

        self.introduction = os.getcwd()+"/samples/intro1.mp3"
        self.outroduction = os.getcwd()+"/samples/outro1.mp3"
        self.reflection = os.getcwd()+"/media/initiation.mp3"
        self.cleanse = os.getcwd()+"/media/cleanse.mp3"

    def ambient_background(self, music, stop_event):

        while not stop_event.is_set():
            playsound(music)

    def acknowledge(self):

        return random.choice(self.acknowledgements)

    def append_turn_to_round(self, agent, text):

        # self.turns.append({ "speaker": agent, "text": text })

        turn_data = { "speaker": agent, "text": text }

        self.rounds[-1].append(turn_data)

    # # NOTE: deprecated
    # def reset_turns(self):

    #     self.turns = []

    # def append_turn(self, turn): # implicitly: to latest round

    #     self.rounds[-1].append(turn)

    def create_round(self):
            
        self.rounds.append([])

    def reset_rounds(self):

        self.rounds = []

    def update_prompt(self):

        lines = []
        transcript = ""

        for turns in self.rounds:

            for turn in turns:

                text = turn["text"]
                speaker = turn["speaker"]
                lines.append(speaker + ": " + text)

        transcript = "\n".join(lines)

        return self.prompt_text.replace("{{transcript}}", transcript)

    def setup(self):

        #print(os.getcwd()+"/prompt_context/plantony_context.txt")
        # load the personality of Plantony
        self.prompt_text = open(os.getcwd()+"/prompt_context/plantony_context.txt").read().strip()

        self.opening = random.choice(self.opening_lines)
        self.closing = random.choice(self.closing_lines) 

        self.append_turn_to_round(self.AGENT, self.opening)

        # self.turns.append({ "speaker": self.AGENT, "text": self.opening })

        # for Plantony oracle
        self.selected_words = []

        # select one item from each category
        for category in self.word_categories:
            self.selected_words.append(random.choice(category['items']))

        # join the selected words into a comma-delimited string
        selected_words_string = ', '.join(self.selected_words)

        # print the result
        print("Plantony is setting up. His seed words are: " + selected_words_string)

    def welcome(self):

        print('Plantony Welcome!')
        print(self.introduction)

        if self.use_arduino:
            PlantoidSerial.sendToArduino("speaking")

        playsound(self.introduction)
        
        audiofile = PlantoidSpeech.get_text_to_speech_response(self.opening)
        print('plantony opening', self.opening)
        print("welcome plantony... opening = " + audiofile)
    
        playsound(audiofile)

    def terminate(self):

        if self.use_arduino:
            PlantoidSerial.sendToArduino("speaking")

        print('plantony closing', self.closing)
        playsound(PlantoidSpeech.get_text_to_speech_response(self.closing)) 
        playsound(self.outroduction)

        if self.use_arduino:
            PlantoidSerial.sendToArduino("asleep")

    def listen(self):

        if self.use_arduino:
            PlantoidSerial.sendToArduino("listening")

        audiofile = PlantoidSpeech.listen_for_speech()

        playsound(self.acknowledge())
        print("Plantony listen is returning the audiofile as:  " + audiofile)

        return audiofile

    def respond(self, audio):

        def prompt_agent_and_respond(audio, callback, shared_response_container):
            
            # user text received from speech recognition
            user_message = PlantoidSpeech.recognize_speech(audio)

            print("I heard... " + user_message)

            if len(user_message) == 0:
                print('no text heard, using default text')
                user_message = "Hmmmmm..."

            # append the user's turn to the latest round
            self.append_turn_to_round(self.USER, user_message)

            use_prompt = self.update_prompt()

            # print("new prompt = " + new_prompt)

            # generate the response from the GPT model
            agent_message = PlantoidSpeech.GPTmagic(use_prompt, call_type='chat_completion')

            # append the agent's turn to the latest round
            self.append_turn_to_round(self.AGENT, agent_message)

            audio_file = PlantoidSpeech.get_text_to_speech_response(agent_message, callback=callback)
            # shared_response_container["audio_file"] = audio_file
            playsound(audio_file)

            # TODO: figure out if this goes here or above
            if self.use_arduino:
                PlantoidSerial.sendToArduino("speaking")

        
        def play_background_music(filename):
            pygame.mixer.init()
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play(-1)  # Play on loop

        def stop_background_music():
            print('stop background music')
            pygame.mixer.music.stop()

        def after_elevenlabs_response():
            stop_background_music()

        if self.use_arduino:
            PlantoidSerial.sendToArduino("thinking")

        print("Plantony respond is receiving the audiofile as : " + audio)

        # create a shared response container
        shared_response_container = dict()

        # get the path to the background music
        background_music_path = os.getcwd()+"/media/ambient3.mp3"

        # play the background music
        play_background_music(background_music_path)

        # create a thread to call the API
        thread = threading.Thread(target=prompt_agent_and_respond, args=(
            audio,
            after_elevenlabs_response,
            shared_response_container,
        ))

        # start the thread
        thread.start()

        # The script will continue to run while waiting for the API response
        thread.join()  # This line ensures the script waits for the API thread to complete before proceeding
        
    def weaving(self):
        
        if self.use_arduino:
            PlantoidSerial.sendToArduino("speaking")

        playsound(self.reflection)

    def oracle(self, network, audio, web3obj, tID, amount, use_arduino=False):

        if self.use_arduino:
            PlantoidSerial.sendToArduino("thinking")

        path = web3obj.path

        #===== play some background noise while we wait..
        # NOTE: the idea is to simply be able to play this sound and terminate the associated thread once done
        # stop_event triggers before the mp3 finishes playing * this is a threading loop!
        stop_event = threading.Event()
        sound_thread = threading.Thread(target=self.ambient_background, args=(os.getcwd()+"/media/metalsound.mp3", stop_event))
        sound_thread.daemon = True
        sound_thread.start()

        generated_transcript = PlantoidSpeech.recognize_speech(audio)

        print("I heard... (oracle): " + generated_transcript)

        if(not generated_transcript): 
            generated_transcript = "I don't know what the future looks like. Describe a solarkpunk utopia where Plantoids have taken over the world."

        # save the generated transcript to a file with the seed name
        if not os.path.exists(path + "/transcripts"):
            os.makedirs(path + "/transcripts");

        filename = path + f"/transcripts/{tID}_transcript.txt"
        with open(filename, "w") as f:
            f.write(generated_transcript)

        print("transcript saved as ..... " + filename)


        # calculate the length of the poem

        n_lines = int(amount / web3obj.min_amount)  # one line every 0.01 ETH for mainnet, one line every 0.001 ETH for goerli
        
        if(n_lines > 7): n_lines = 7

        n_lines = 4

        print("generating transcript with number of lines = " + str(n_lines))

        selected_words_string = self.selected_words_string
        prompt = f"You are Plant-Tony, an enlightened being from the future. Answer the following qestion in the form of a thoughtful poem structured around {n_lines} short paragraph, each paragraph is composed of exactly 4 lines:\n\n{generated_transcript}\n\nInclude the following words in your poem: {selected_words_string}. Remember, the poem should be exactly {n_lines} paragraphs long, with 4 lines per paragraph."
        response = PlantoidSpeech.GPTmagic(prompt, call_type='completion')
        sermon_text = response.choices[0].text

        # save the generated response to a file with the seed name
        if not os.path.exists(path + "/responses"):
            os.makedirs(path + "/responses");

        filename = path + f"/responses/{tID}_response.txt"
        with open(filename, "w") as f:
            f.write(sermon_text)


        # now let's print to the LP0, with Plantoid signature

        plantoid_sig = "\n\nYou can reclaim your NFT by connecting to " + network.reclaim_url + " and pressing the Reveal button for seed #" + tID + " \n"
        os.system("cat " + filename + " > /dev/usb/lp0")
        os.system("echo '" + plantoid_sig + "' > /dev/usb/lp0")


        # now let's read it aloud
        audiofile = PlantoidSpeech.get_text_to_speech_response(sermon_text)
        stop_event.set() # stop the background noise


        # save the generated sermons to a file with the seed name
        if not os.path.exists(path + "/sermons"):
            os.makedirs(path + "/sermons");
        os.system("cp " + audiofile + " " + path + f"/sermons/{tID}_sermon.mp3")

    #    PlantoidSerial.sendToArduino("speaking");
    #    playsound(file)

    #    time.sleep(1)

    #    PlantoidSerial.sendToArduino("asleep")
    #    cleanse = '/home/pi/PLLantoid/v6/media/cleanse.mp3'
    #    playsound(cleanse)


        # stop_event = threading.Event()
        oracle_thread = threading.Thread(target=self.read_oracle, args=(audiofile,)) #, stop_event))
        # sound_thread.daemon = True
        oracle_thread.start()

    def read_oracle(self, filename):

        if self.use_arduino:
            PlantoidSerial.sendToArduino("speaking");
        
        playsound(filename)
        time.sleep(1)
        #cleanse = '/home/pi/PLLantoid/v6/media/cleanse.mp3'
        playsound(self.cleanse)
        #playsound(cleanse)
