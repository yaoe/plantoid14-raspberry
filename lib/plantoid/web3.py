from web3 import Web3
import subprocess
import os
import time
from pathlib import Path
import json
from dotenv import load_dotenv
from pinata import Pinata

import lib.plantoid.eden as eden

class Web3Object:
    infura_websock = None
    w3 = None
    plantoid_contract = None
    event_listener = None
    path = None
    min_amount = None
    failsafe = None


load_dotenv()

# API_KEY = os.getenv('API_KEY')
# API_SECRET = os.getenv('API_SECRET')
# JWT = os.getenv('JWT')

PINATA_API_KEY = os.environ.get("PINATA_API_KEY")
PINATA_API_SECRET = os.environ.get("PINATA_API_SECRET")
PINATA_JWT = os.getenv('PINATA_JWT')
INFURA_API_KEY_MAINNET = os.environ.get("INFURA_MAINNET")
INFURA_API_KEY_GOERLI = os.environ.get("INFURA_GOERLI")


pinata = Pinata(PINATA_API_KEY, PINATA_API_SECRET, PINATA_JWT)

def setup(infura_websock, addr, path, feeding_amount, reclaim_url, failsafe):

    network = Web3Object();

    network.w3 = Web3(Web3.WebsocketProvider(infura_websock))
    
    print(network.w3)
    print(network.w3.is_connected())

    abifile = open(path + '/abi', 'r')
    o = abifile.read()
    abi = o.replace('\n', '')
    print(abi)
    abifile.close()

    address = Web3.to_checksum_address(addr)

    network.plantoid_contract = network.w3.eth.contract(address=address, abi=abi)
    print(network.w3.eth.get_balance(address))

    network.event_filter = network.plantoid_contract.events.Deposit.create_filter(fromBlock=1)
    print(network.event_filter)
    
    network.path = path

    network.min_amount = feeding_amount

    network.reclaim_url = reclaim_url

    network.failsafe = failsafe

    return network

    # process_previous_tx(path, event_filter)

def process_previous_tx(web3obj):

    processing = 0

    path = web3obj.path
    event_filter = web3obj.event_filter

    # if db doesn't exist, nothing has been minted yet

    if (not os.path.exists(path + 'minted.db')):
        print('processing is null')
        processing = 1

    # if db exists, skip to the lastely minted item

    else:

        with open(path + 'minted.db') as file:
            for line in file:
                pass
            last = line
            print("last line = " + last)

    # loop over all entries to process unprocessed Deposits

    for event in event_filter.get_all_entries():
            print("looping through ---: " +str(event.args.tokenId))

            if(processing == 0):
                if(str(event.args.tokenId) == last.strip()):
                    processing = 1;
                    print('processing is true\n')
                continue;

            print('handling event...\n')
            create_metadata(web3obj, str(event.args.tokenId))

    
def checkforDeposits(web3obj):

    event_filter = web3obj.event_filter

    try:
        events = event_filter.get_new_entries()

    except:
        print("failed to read new entries()\n")
        # TODO: check if this is correct exception handling
        return None

    else:
        for event in events:
            print("new Deposit EVENT !! ")
            print("token id = " + str(event.args.tokenId))
            print("amount = " + str(event.args.amount))

            return ( str(event.args.tokenId), int(event.args.amount) )  ### @@@@ need to fix this  :)
           #  return  str(event.args.tokenId) 

def create_metadata(web3obj, tID):


    path = web3obj.path

    ### Pin the Video-Sermon on IPFS

    ipfsQmp3 = ""
    movie = ""

    if os.path.exists(path + "/videos/"+tID+"_movie.mp4"):

        # the movie already exists, move directly to the metadata creation
        print("skipping the production of the movie, as it already exists...");
        movie = path + "/videos/"+tID+"_movie.mp4"


    else:

        audio = path + "/sermons/" + tID + "_sermon.mp3"
        print("creating movie for sermon file.. " + audio) 
        
        if not os.path.isfile(audio):
            print("no Sermon associated with seed: " + tID)
            return

        movie = eden.createVideoFromAudio(path, tID, web3obj.failsafe)

#    file_stats = os.stat(audio)

#    if(file_stats.st_size):
#        cmd_str = "xvfb-run /home/pi/PLLantoid/v5/processing/processing-java --sketch=/home/pi/PLLantoid/v6/voice2video --run " + audio
#        print(cmd_str)
#        err = subprocess.run(cmd_str, shell=True) # return 0 if works well
#        print(err)
#        if not err.check_returncode():
#            print("pinning the movie to ipfs")
#            audio = "/home/pi/PLLantoid/v5/voicevideo/voicefile2/processing-movie.mp4"

    if(movie):
            response = pinata.pin_file(movie)
            print(response)

            if(response and response.get('data')):
                ipfsQmp3 = response['data']['IpfsHash']
                print("reording the animation_url = " + ipfsQmp3)

    ### Create Metadata

    db = {}
    db['name'] = tID
    db['description'] = "Plantoid #15 - Seed #" + tID
    db['external_url'] = "http://plantoid.org"
    db['image'] = "https://ipfs.io/ipfs/QmRcrcn4X6QfSwFnJQ1dNHn8YgW7pbmm6BjZn7t8FW7WFV" # ipfsQpng
    if(ipfsQmp3):
        db['animation_url'] = "ipfs://" + ipfsQmp3 # ipfsQwav

    path_meta = path + "/metadata/"
    if not os.path.exists(path_meta):
        os.makedirs(path_meta)
    with open(path_meta + tID + '.json', 'w') as outfile:
        json.dump(db, outfile)

    ### record in the database that this seed has been processed

    with open(path + "minted.db", 'a') as outfile:
        outfile.write(tID + "\n")

    ### NB: The metadata file will be pinned to IPFS via the node server



def setup_web3_provider():

    # make sure that the script can listen to both events happening in mainnet and goerli, and process them accordingly !
    goerli = setup('wss://goerli.infura.io/ws/v3/'+INFURA_API_KEY_GOERLI,
                                '0x0B60EE161d7b67fa231e9565dAFF65b34553bC6F',
                                '/home/pi/PLLantoid/v6/GOERLI/',
                                1000000000000000,  # one line every 0.001 ETH
                                "http://15goerli.plantoid.org",
                                1) # this set failsafe = 1 (meaning we should recycle movies)

    # lorem ipsum
    mainnet = setup('wss://mainnet.infura.io/ws/v3/'+INFURA_API_KEY_MAINNET,
                                '0x4073E38f71b2612580E9e381031B0c38B3B4C27E', 
                                "/home/pi/PLLantoid/v6/MAINNET/",
                                10000000000000000,  # one line every 0.01 ETH)
                                "http://15.plantoid.org",
                                0) # this set failsafe = 0 (meaning we should generate a new movie)
    
    return goerli, mainnet

