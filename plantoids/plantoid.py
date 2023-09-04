import random
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
        self.turns = []

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

    def append_to_turns(self, agent, text):

        self.turns.append({ "speaker": agent, "text": text })

    def update_prompt(self):

        lines = []
        transcript = ""

        for turn in self.turns:
            text = turn["text"]
            speaker = turn["speaker"]
            lines.append(speaker + ": " + text)
        transcript = "\n".join(lines)

        return self.prompt_text.replace("{{transcript}}", transcript)

    def setup(self):

        #print(os.getcwd()+"/prompt_context/plantony_context.txt")
        # load the personality of Plantony
        prompt_text = open(os.getcwd()+"/prompt_context/plantony_context.txt").read().strip()

        opening = random.choice(self.opening_lines)
        closing = random.choice(self.closing_lines) 

        self.turns.append({ "speaker": self.AGENT, "text": opening })

        # for Plantony oracle

        selected_words = []

        # select one item from each category
        for category in self.word_categories:
            selected_words.append(random.choice(category['items']))

        # join the selected words into a comma-delimited string
        selected_words_string = ', '.join(selected_words)

        # print the result
        print("Plantony is setting up. His seed words are: " + selected_words_string)

    def welcome(self):

        print('Plantony Welcome!')
        print(self.introduction)

        if self.use_arduino:
            PlantoidSerial.sendToArduino("speaking")

        playsound(self.introduction)
        
        audiofile = PlantoidSpeech.speak_text(self.opening)
        print("welcome plantony... opening = " + audiofile)
    
        playsound(audiofile)

    def terminate(self):

        if self.use_arduino:
            PlantoidSerial.sendToArduino("speaking")

        playsound(PlantoidSpeech.speak_text(self.closing)) 
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

        if self.use_arduino:
            PlantoidSerial.sendToArduino("thinking")

        print("Plantony respond is receiving the audiofile as : " + audio)

        #===== play some background noise while we wait..
        stop_event = threading.Event()
        sound_thread = threading.Thread(target=self.ambient_background, args=(os.getcwd()+"/media/metalsound.mp3", stop_event))
        sound_thread.daemon = True
        sound_thread.start()
        
        usertext = PlantoidSpeech.record_speech(audio)
        print("I heard... " + usertext)
        if(not usertext): usertext = "Hmmmmm..."

        self.append_to_turns(self.USER, usertext)
        new_prompt = self.update_prompt()
        print("new prompt = " + new_prompt)

        msg = PlantoidSpeech.GPTmagic(new_prompt, call_type='chat_completion')
        self.append_to_turns(self.AGENT, msg)

        audio_file = PlantoidSpeech.speak_text(msg)

        stop_event.set() # stop the background noise

        if self.use_arduino:
            PlantoidSerial.sendToArduino("speaking")
        playsound(audio_file)


    def weaving(self):
        
        if self.use_arduino:
            PlantoidSerial.sendToArduino("speaking")

        playsound(self.reflection)

    def PlantonyOracle(self, network, audio, web3obj, tID, amount, use_arduino=False):

        if self.use_arduino:
            PlantoidSerial.sendToArduino("thinking")

        path = web3obj.path

        #===== play some background noise while we wait..
        stop_event = threading.Event()
        sound_thread = threading.Thread(target=self.ambient_background, args=(os.getcwd()+"/media/metalsound.mp3", stop_event))
        sound_thread.daemon = True
        sound_thread.start()

        generated_transcript = PlantoidSpeech.record_speech(audio)

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
        audiofile = PlantoidSpeech.speak_text(sermon_text)
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
