import os
import json
import sys
from dotenv import load_dotenv
import time
import random

import re
import openai

from mutagen.mp3 import MP3

import Eden



# Load environment variables from .env file
load_dotenv()

# Access environment variables
openai.api_key = os.environ.get("OPENAI")

model_id = "text-davinci-003"
max_tokens = 1024



def create_prompts(path, seed, n_prompt):

    str_n_prompts = str(n_prompt)
    str_n_prompts_n = str(n_prompt - 1)

    f = open(path + "/responses/" +
             seed + "_response.txt", "r")
    stri = f.read()

    prompt1 = "Can you generate a short sentence that illustrates the physical environment where the poem takes place in a very graphical manner. Starting with: A scene... "
    prompt1 = prompt1 + "Here's the poem which I'd like you to litterally illustrate: " + stri

    prompt = "I need to illustrate this poem."
    prompt = prompt + "Can you generate" + str_n_prompts_n + "sentences that reflect a different scene of the poem, presented chronologically based on the phrasing of the poem. "
    prompt = prompt + "I don't wont a summary of the plot, I want a graphical description that illustrates the statements of the poem. "
    prompt = prompt + "These descriptions will be used to generate a video illustrating the poem. "
    prompt = prompt + "Every sentence needs to be a self-contained descriptive illustration, that does not refer to the previous or following sentences. "
    prompt = prompt + "Be highly descritive, ideally with a particular style that is reminescent of solar-punk vibes. "
    prompt = prompt + "You can mention colors but only in one of these descriptions, and no reference to colors must be present in the first sentence. "
    prompt = prompt + "Draft your answer with each line starting with the number of the line, followed by a dot, a space, and then the actual description. "
    prompt = prompt + "Here's the poem which I'd like you to litterally illustrate: " + stri

    response1 = openai.Completion.create(
            engine=model_id,
            prompt=prompt1,
            max_tokens=max_tokens
    )

    response = openai.Completion.create(
        engine=model_id,
        prompt=prompt,
        max_tokens=max_tokens
    )
    
    descri1 = response1.choices[0].text
    descri = response.choices[0].text

    print(descri1)
    print(descri)


    with open(path + "/descriptions/" + seed + "_description.txt", "w") as g:
        g.write(descri1)
        g.write(descri)

    lines = re.split("\d.", descri)
    lines.insert(0, descri1)


    prompts = []

    for ln in lines:
        line = ln.strip()
        line = line.replace("\n", "")
        print("["+line+"]")

        if (line):
            # line = "Drawing by M. C. Escher with a strong solar-punk flavor representing: " + line + ". Neat lines, extreme detailed illustration, highly detailed linework, sf, intricate artwork masterpiece, ominous, intricate, epic, vibrant, ultra high quality model, solar-punk illustration"
            line = "Drawing by M. C. Escher with a strong solar-punk flavor representing: " + line
            line = line + " Hyper realistic, detailed, intricate, best quality, hyper detailed, ultra realistic, sharp focus, delicate and refined."
            prompts.append(line)

    print(prompts)
    return prompts

# prompts = [
#     "Drawing by M. C. Escher with a strong solar-punk flavor representing: Unmanned vehicles traverse a world bustling with skyscrapers and forests of metal and machine.. Neat lines, extreme detailed illustration, highly detailed linework, sf, intricate artwork masterpiece, ominous, intricate, epic, vibrant, ultra high quality model, solar-punk illustration",
#     "Drawing by M. C. Escher with a strong solar-punk flavor representing: A golden glow radiates from the skyline, casting a warm hue over a diverse yet homogenous population.. Neat lines, extreme detailed illustration, highly detailed linework, sf, intricate artwork masterpiece, ominous, intricate, epic, vibrant, ultra high quality model, solar-punk illustration",
#     "Drawing by M. C. Escher with a strong solar-punk flavor representing: Citizens, both robotic and plant-like, work together in a technosymbiotic harmony.. Neat lines, extreme detailed illustration, highly detailed linework, sf, intricate artwork masterpiece, ominous, intricate, epic, vibrant, ultra high quality model, solar-punk illustration",
#     "Drawing by M. C. Escher with a strong solar-punk flavor representing: Gigantic vines and flower-covered motorways create a unique urban gardenscape.. Neat lines, extreme detailed illustration, highly detailed linework, sf, intricate artwork masterpiece, ominous, intricate, epic, vibrant, ultra high quality model, solar-punk illustration",
#     "Drawing by M. C. Escher with a strong solar-punk flavor representing: Moving constructions, both metallic and organic, bridge the built environment and the mechanical ecosystem.. Neat lines, extreme detailed illustration, highly detailed linework, sf, intricate artwork masterpiece, ominous, intricate, epic, vibrant, ultra high quality model, solar-punk illustration",
#     "Drawing by M. C. Escher with a strong solar-punk flavor representing: A thriving metropolis is brightly illuminated by the energy generated from a vast network of plants.. Neat lines, extreme detailed illustration, highly detailed linework, sf, intricate artwork masterpiece, ominous, intricate, epic, vibrant, ultra high quality model, solar-punk illustration",
#     "Drawing by M. C. Escher with a strong solar-punk flavor representing: Futuristic skyscrapers erupt from the landscape, pulsating with light and spires of growth.. Neat lines, extreme detailed illustration, highly detailed linework, sf, intricate artwork masterpiece, ominous, intricate, epic, vibrant, ultra high quality model, solar-punk illustration",
#     "Drawing by M. C. Escher with a strong solar-punk flavor representing: An ever-changing mix of flora and fauna, rooted in ancient symbologies, reflect the balanced existence of humans and their machines.. Neat lines, extreme detailed illustration, highly detailed linework, sf, intricate artwork masterpiece, ominous, intricate, epic, vibrant, ultra high quality model, solar-punk illustration",
#     "Drawing by M. C. Escher with a strong solar-punk flavor representing: The inhabitants move freely, unencumbered by the society they have created; a connected, unified future of plantoid harmony.. Neat lines, extreme detailed illustration, highly detailed linework, sf, intricate artwork masterpiece, ominous, intricate, epic, vibrant, ultra high quality model, solar-punk illustration"
#   ]


def build_APIrequest(path, seed):


    audiof = MP3(path + "/sermons/" + seed + "_sermon.mp3")
    audiolen = audiof.info.length  # seconds of the poem length
    print("audiolen === " + str(audiolen))

    seconds_per_prompt = 3
    n_prompt = int(audiolen / seconds_per_prompt)
    print("initial n_prompts = " + str(n_prompt))

    # calculate n_film and fps in order to ensure that the movie doesn't go over 100 frames, for the sake of speed.
    n_film = 2
    fps = 10

    frames = int(audiolen * fps / (2**n_film))

    while(frames > 75 and fps > 5):
        fps = fps -1
        frames = audiolen * fps / (2**n_film)

    frames = frames + 6 # better to have a slighter longer movie than slighter shorter one :)

    print("frames = " + str(frames))
    print("fps = " + str(fps))

    # adjust the number of frames to account for rounding errors per prompts
    # frames = frames + len(prompts) # * 1 * n_film;

    # select the number of prompts based on 'audiolen' and 'fps'
    prompt_sec = 4 # if fps = 12, then we want 2 seconds per prompt
    prompt_sec = int(prompt_sec + (10 - fps)) # we decrease the seconds-per-prompt as we reduce the fps rate

    print("new prompt_factor = " + str(prompt_sec))

    n_prompt = int(audiolen / prompt_sec)
    print("new n_prompt = " + str(n_prompt))


    if(n_prompt < 2):   n_prompt = 2

    prompts = []
    while(len(prompts) < 2):
            prompts = create_prompts(path, seed, n_prompt)


    images = []
    i = 0
    while (i < len(prompts)):
        # images.append("https://minio.aws.abraham.fun/creations-stg/c25c6b80c347d214eef34d67ee9b586f8e7de90662076667563f781c504f2877.webp");
        images.append(
            "https://minio.aws.abraham.fun/creations-stg/2af20071b6342bc55ce70410cff3c4846dba9e497979ad8739668365e816e8de.jpg")
        i = i+1
    

    print("n_film ====> " + str(n_film))


    config = {"interpolation_texts": prompts,
              "interpolation_init_images": images,
              "interpolation_init_images_min_strength": 0,
              "interpolation_init_images_max_strength": 0,
              "interpolation_init_images_power": 0.5,
              "n_film": n_film,
              "latent_blending_skip_f": [0.1,0.9],
              "guidance_scale": 20,
              "width": 1024,
              "height": 1024,
              "stream": False,
              "steps": 20,
              "fps": fps,
              "n_frames": int(frames)}

    print(config)
    return config


def make_APIcall(config):

    s = time.time()
    result = Eden.run_task("real2real", config)
    e = time.time()

    if not result:
        print("Eden.run_task returned Null")
        return

    print("Processing of Interpolation took: " +
          time.strftime("%Hh%Mm%Ss", time.gmtime(e-s)))

    # print(result['output']['files'])

    j = json.dumps(result, indent=4)

    # print(j)

    with open("/tmp/sample2.json", "w") as outfile:
        outfile.write(j)

    # outputf = result['creation']['uri']
    outputf = result['output']['files'][0]

    print(outputf)
    return outputf


def get_video(path, outputf, seed):


    moviefile = "/tmp/out.mp4"

    print("**** running wget with:\nwget " + outputf)
    os.system("wget " + outputf + " -O " + moviefile)

    # m = re.search("\w+\.mp4", outputf)
    # moviefile = m.group()

    # os.system("mv " + moviefile + " "+taskId+".mp4")

    return moviefile


def make_video(path, moviefile, seed): 

    if not os.path.exists(path + "/videos"):
        # If it doesn't exist, create it
        os.makedirs(path + "/videos/")


    print("***** running ffmpeg with:\nffmpeg -i " + moviefile + " -i " + path +"/sermons/" + seed + "_sermon.mp3 " + path+"videos/" + seed + "_movie.mp4")
    os.system("ffmpeg -i " + moviefile +" -i " + path +"/sermons/" + seed + "_sermon.mp3 " + path +"videos/" + seed + "_movie.mp4")

    # os.remove(moviefile)

    return (path+ "/videos/" + seed + "_movie.mp4")



def createVideoFromAudio(path, tID, failsafe):


    outf = None;

 #   prompts = PlantoidEden.create_prompts(tID)

    config = build_APIrequest(path, tID)  # construct the API call to Eden (this includes the making of the prompts)

    if(failsafe == 0):
        outf = make_APIcall(config)           # launch the API call which will return the video generated by Eden
                                              # only if failsafe is not set (if set, it will recycle an existing movie).


    videof = None;

    if(outf):
        videof = get_video(path, outf, tID)
    else:
        print("PlantoidEden.make_APIcall return Null -- going to use a fallback video !")
        videof = fallback_video(path, tID)

    finalvideo = make_video(path, videof, tID)

    return finalvideo



def fallback_video(path, tID):

    audiof = MP3(path + "/sermons/" + tID + "_sermon.mp3")
    audiolen = int(audiof.info.length) + 1  # seconds of the poem length
    print("audiolen === " + str(audiolen))

    
    Zdir = "/home/pi/PLLantoid/v6/Zvideos/"
    Zvideos = sorted(os.listdir(Zdir))
    print(Zvideos)
    
    Zmin = int(re.search('(\d+)', Zvideos[0]).group(0))
    Zmax = int(re.search('(\d+)', Zvideos[-1]).group(0))

    print("Zmin = " + str(Zmin))
    print("Zmax = " + str(Zmax))

    if(audiolen < Zmin): audiolen = Zmin
    if(audiolen > Zmax): audiolen = Zmax

    outf = None

    for n in range(audiolen, Zmax+1):
    
        print("iterating through..." + str(n))
        Zvids = [ v for v in Zvideos if v.startswith(str(n)) ]
        if len(Zvids) > 0: 
            print(Zvids)
            outf = random.choice(Zvids)
            break;


    print("Given audiolen = " + str(audiolen))
    print("We found the Zvideo = " + outf)


    if not outf: outf = Zvideos[-1]

    return Zdir + outf


        








if __name__ == "__main__":

    seed = sys.argv[1]
    path = "/home/pi/PLLantoid/v6/GOERLI/"

#    outf = createVideoFromAudio(path, seed)


#    prompts = create_prompts(seed)
    
    config = build_APIrequest(path, seed)
    outf = make_APIcall(config)

    videof = None

    if(outf):
        videof = get_video(outf)
        print(videof)

    else:
        videof = fallback_video(path, outf)

    outf = make_video(path, videof, seed)

    print("NEW VIDEO == " + outf)

