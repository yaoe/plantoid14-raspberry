import lib.plantoid.serial_listen as serial_listen
import lib.plantoid.speech as speech
import lib.plantoid.web3 as web3
# from lib.plantoid.core import *

from plantoids.plantoid import Plantony

from utils.util import load_config, str_to_bool

from dotenv import load_dotenv

import regex_spm
import time
import os

def invoke_plantony(plantony: Plantony, max_rounds=4):

    print('plantony initiating...')
    plantony.welcome()

    print('Iterating on Plantony n of rounds:', len(plantony.rounds), 'max rounds:', max_rounds)

    while(len(plantony.rounds) < max_rounds):

        # create the round
        plantony.create_round()

        print('plantony rounds...')
        print(len(plantony.rounds))

        print('plantony listening...')
        audiofile = plantony.listen()

        print('plantony responding...')
        plantony.respond(audiofile)

    # TODO: sub function without speech
    print('plantony listening...')
    plantony.listen()

    print('plantony terminating...')
    plantony.terminate()

    # print('debug: plantony rounds...')
    # print(plantony.rounds)

    plantony.reset_rounds()
    plantony.reset_prompt()
    # awake = 0

def mock_arduino_event_listen(ser, plantony, max_rounds=4):

    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                if line == "button_pressed":
                    print("Button was pressed, Invoking Plantony!")

                    plantony.trigger('Touched', plantony, max_rounds=max_rounds)

    except KeyboardInterrupt:
        print("Program stopped by the user.")
        ser.close()

def main():

    # load config
    config = load_config('./configuration.toml')

    cfg = config['general']

    use_blockchain = str_to_bool(cfg['ENABLE_BLOCKCHAIN'])
    use_arduino = str_to_bool(cfg['ENABLE_ARDUINO'])
    PORT = cfg['SERIAL_PORT_OUTPUT']
    max_rounds = cfg['max_rounds']

    # setup serial
    ser = serial_listen.setup_serial(PORT=PORT)

    # instantiate plantony
    plantony = Plantony()

    # setup plantony
    plantony.setup()

    # add listener
    plantony.add_listener('Touched', invoke_plantony)

    # check for keyboard press
    mock_arduino_event_listen(ser, plantony, max_rounds=max_rounds)
    # serial_listen.listen_for_keyboard_press(ser)



    # trigger plantony
    # NOTE: this is a mocked event
    # plantony.trigger('Touched', plantony, max_rounds=max_rounds)

    # invoke plantony
    # invoke_plantony(plantony, max_rounds=max_rounds)

    # if use_blockchain and use_arduino: 

    #     serial_setup.setupSerial(serialPortName=serial_port_name)

    #     serial_setup.sendToArduino("thinking")

    #     goerli, mainnet = web3.setup_web3_provider()

    #     web3.process_previous_tx(mainnet)
    #     web3.process_previous_tx(goerli)

    #     serial_setup.sendToArduino("asleep")


    # while True:

    #     # check for a message from Arduino
    #     if use_arduino:
            
    #         arduinoReply = serial_setup.recvLikeArduino()
        
    #         if not (arduinoReply == 'XXX'):
    #             print("received... " + arduinoReply);

    #             match regex_spm.fullmatch_in(arduinoReply):
                
    #                 case r"Touched" as m:

    #                     if awake == 1:
    #                         awake = 0
    #                         serial_setup.sendToArduino("asleep")
                    
    #                     else:
    #                         awake = 1
    #                         serial_setup.sendToArduino("awake")

    #                         invoke_plantony(plantony, max_rounds=max_rounds)
    #                         awake = 0

            
    #     else:

    #         print('skipping arduino usage')
    #         invoke_plantony(plantony, max_rounds=max_rounds)

    #     # check for a message from the blockchain
    #     if use_blockchain:

    #         # check for a new Deposit event
    #         for network in (mainnet, goerli):

    #             mylist  = web3.checkforDeposits(network) ### this returns the token ID and the amount of wei that plantoid has been fed with

    #             if(mylist != None):  # Plantoid has been fed
                
    #                 (tID, amount) = mylist

    #                 print("got amount " + str(amount) + " for id = " + tID);

    #                 plantony.weaving()
                
    #                 audiofile = plantony.listen()
                
    #                 plantony.oracle(network, audiofile, network, tID, amount)

    #                 serial_setup.sendToArduino("thinking")
                
    #                 web3.create_metadata(network, tID)

    #                 serial_setup.sendToArduino("asleep")


                
if __name__ == "__main__":

    # seed = sys.argv[1]
    # path = "/home/pi/PLLantoid/v6/GOERLI/"

    # Execute main function
    main()




