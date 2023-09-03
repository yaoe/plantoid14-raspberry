import playsound
import threading
import os
import time

import plantoids.Plantony as Plantony
import lib.plantoid.serial as PlantoidSerial
import lib.plantoid.speech as PlantoidSpeech

def PlantonyWelcome():
    PlantoidSerial.sendToArduino("speaking")
    playsound(Plantony.introduction)
    
    audiofile = PlantoidSpeech.speaktext(Plantony.opening)
    print("welcome plantony... opening = " + audiofile)
 
    playsound(audiofile)

def PlantonyQuit():
    PlantoidSerial.sendToArduino("speaking")
    playsound(PlantoidSpeech.speaktext(Plantony.closing)) 
    playsound(Plantony.outroduction)
    PlantoidSerial.sendToArduino("asleep")

def PlantonyListen():
    PlantoidSerial.sendToArduino("listening")
    audiofile = PlantoidSpeech.listenSpeech(); 
    playsound(Plantony.acknowledge())
    print("Plantony listen is returning the audiofile as:  " + audiofile)
    return audiofile

def PlantonyRespond(audio):
    PlantoidSerial.sendToArduino("thinking")

    print("Plantony respond is receiving the audiofile as : " + audio)

    #===== play some background noise while we wait..
    stop_event = threading.Event()
    sound_thread = threading.Thread(target=ambient_background, args=("/home/pi/PLLantoid/v6/media/metalsound.mp3", stop_event))
    sound_thread.daemon = True
    sound_thread.start()
    
    usertext = PlantoidSpeech.recoSpeech(audio)
    print("I heard... " + usertext)
    if(not usertext): usertext = "Hmmmmm..."

    Plantony.turnsAppend(Plantony.USER, usertext)
    new_prompt = Plantony.updateprompt()
    print("new prompt = " + new_prompt)

    msg = PlantoidSpeech.GPTmagic(new_prompt, call_type='chat_completion')
    Plantony.turnsAppend(Plantony.AGENT, msg)

    file = PlantoidSpeech.speaktext(msg)

    stop_event.set() # stop the background noise

    PlantoidSerial.sendToArduino("speaking")
    playsound(file)



def PlantonyWeaving():
    PlantoidSerial.sendToArduino("speaking")
    playsound(Plantony.reflection)



def PlantonyOracle(network, audio, web3obj, tID, amount):
    PlantoidSerial.sendToArduino("thinking")

    path = web3obj.path


     #===== play some background noise while we wait..
    stop_event = threading.Event()
    sound_thread = threading.Thread(target=ambient_background, args=("/home/pi/PLLantoid/v6/media/metalsound.mp3", stop_event))
    sound_thread.daemon = True
    sound_thread.start()


    generated_transcript = PlantoidSpeech.recoSpeech(audio)
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

    selected_words_string = Plantony.selected_words_string
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
    audiofile = PlantoidSpeech.speaktext(sermon_text)
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
    oracle_thread = threading.Thread(target=read_oracle, args=(audiofile,)) #, stop_event))
    # sound_thread.daemon = True
    oracle_thread.start()

def ambient_background(music, stop_event):
    while not stop_event.is_set():
        playsound(music)


def read_oracle(filename):
    PlantoidSerial.sendToArduino("speaking");
    playsound(filename)
    time.sleep(1)
    cleanse = '/home/pi/PLLantoid/v6/media/cleanse.mp3'
    playsound(cleanse)
    playsound(cleanse)