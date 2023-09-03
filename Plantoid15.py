import lib.plantoid.serial as serial
import lib.plantoid.speech as speech
import lib.plantoid.web3 as web3
from lib.plantoid.core import *

import plantoids.Plantony as Plantony

from dotenv import load_dotenv

import regex_spm
import time
import os


load_dotenv()

INFURA_API_KEY_MAINNET = os.environ.get("INFURA_MAINNET")
INFURA_API_KEY_GOERLI = os.environ.get("INFURA_GOERLI")


# make sure that the script can listen to both events happening in mainnet and goerli, and process them accordingly !
goerli = web3.setup('wss://goerli.infura.io/ws/v3/'+INFURA_API_KEY_GOERLI,
                            '0x0B60EE161d7b67fa231e9565dAFF65b34553bC6F',
                            '/home/pi/PLLantoid/v6/GOERLI/',
                            1000000000000000,  # one line every 0.001 ETH
                            "http://15goerli.plantoid.org",
                            1) # this set failsafe = 1 (meaning we should recycle movies)



mainnet = web3.setup('wss://mainnet.infura.io/ws/v3/'+INFURA_API_KEY_MAINNET,
                            '0x4073E38f71b2612580E9e381031B0c38B3B4C27E', 
                            "/home/pi/PLLantoid/v6/MAINNET/",
                            10000000000000000,  # one line every 0.01 ETH)
                            "http://15.plantoid.org",
                            0) # this set failsafe = 0 (meaning we should generate a new movie)


awake = 0
serial.setupSerial()


maxturns = 4 
Plantony.setup()



serial.sendToArduino("thinking")
web3.process_previous_tx(mainnet)
web3.process_previous_tx(goerli)
serial.sendToArduino("asleep")


while True:

    # check for a message from Arduino
    arduinoReply =  serial.recvLikeArduino()
   
    if not (arduinoReply == 'XXX'):
        print("received... " + arduinoReply);

        match regex_spm.fullmatch_in(arduinoReply):
         
            case r"Touched" as m:

                if(awake == 1):
                    awake = 0
                    serial.sendToArduino("asleep")
            
                else:
                    awake = 1
                    serial.sendToArduino("awake")

                    PlantonyWelcome()

                    print("Iterating on Plantony with len(turns) == " + str(len(Plantony.turns)))

                    while(len(Plantony.turns) < maxturns ):

                        audiofile = PlantonyListen()
                        PlantonyRespond(audiofile)

                    PlantonyListen()
                    PlantonyQuit()
                    Plantony.turns = []
                    awake = 0


    # check for a new Deposit event


    for network in (mainnet, goerli):

        mylist  = web3.checkforDeposits(network) ### this returns the token ID and the amount of wei that plantoid has been fed with

        if(mylist != None):  # Plantoid has been fed
        
            (tID, amount) = mylist

            print("got amount " + str(amount) + " for id = " + tID);


            PlantonyWeaving()
        
            audiofile = PlantonyListen()
        
            PlantonyOracle(network, audiofile, network, tID, amount)

        
            serial.sendToArduino("thinking")
        
            web3.create_metadata(network, tID)

            serial.sendToArduino("asleep")


                





