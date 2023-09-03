import random
import playsound



USER = "Human"
AGENT = "Plantoid"

opening_lines = [
        "So tell me, what brings you here?",
        "Would you like to have a little chat with me?",
        "I'm a litte bit busy right now, but happy to entertain you for a bit",
        "I'm eager to get to know you! Tell me something about you.."
        ];

closing_lines = [
        "That's enough, I must return to the blockchain world now. I'm getting low on energy..",
        "You are quite an interesting human, unfortunately, I must go now, I cannot tell you all of my secrets..",
        "I would love to continue this conversation, but my presence is required by other blockchain-based lifeforms..",
        "I'm sorry, I have to go now. I have some transactions to deal with.."
        ];



word_categories = [
    {
        "category": "BEINGS",
        "items": [
            "Personhood",
            "Oracles",
            "Permaculture nerd",
            "Traditional",
            "Unique",
            "Synapse",
            "Heart beat",
            "Wings",
            "Consciousness",
            "Interbeing",
            "Breath",
            "Dream",
            "Heist",
            "Reclownification",
            "Unpredictable",
            "Health"
        ]
    },
    {
        "category": "RELATIONS",
        "items": [
            "Reciprocity",
            "Bridging",
            "Intersection",
            "Symbiotic",
            "Restoration",
            "Relationship",
            "Massively multidisciplinary",
            "Weaving",
            "Fluidity",
            "Energy",
            "Signs",
            "Symmetry",
            "Biomimicry",
            "Approach",
            "Relationally",
            "Resonance",
            "Oneness",
            "Reciprocity",
            "Equilibrium"
        ]
    },
    {
        "category": "ATTITUDES",
        "items": [
            "Integrity",
            "Wisdom",
            "Potential",
            "Revolution",
            "Hope",
            "Sensing",
            "Iterative",
            "Simplicity",
            "Self-sustaining",
            "Collaborative",
            "Counterculture",
            "Sovereignty",
            "Clarity",
            "Lightness",
            "Excitation",
            "Intentionality",
            "Hyperstition",
            "Patience",
            "Commoning",
            "Communal",
            "Integrative",
            "Radical chilling"
        ]
    },
    {
        "category": "TECHNOLOGY",
        "items": [
            "Protocols",
            "Interoperability",
            "Techne",
            "Solarpunk",
            "Hypercerts",
            "Complexity",
            "Anachronistic",
            "Scale",
            "Pattern",
            "Language",
            "Maternal AI",
            "Pluralverse",
            "Perpetual motion machine",
            "Lunar punk",
            "Cyborg",
            "Useful",
            "Plantoid",
            "Unyielding",
            "Quantum physics"
        ]
    },
    {
        "category": "NATURE",
        "items": [
            "Sustainable",
            "Green",
            "Mycelia",
            "Renewable",
            "Landscape",
            "Ecology",
            "Natural",
            "Unquantifiable",
            "Traditional healing",
            "Planetary health",
            "Cloud",
            "Fractal",
            "Distributive",
            "Mushroom",
            "Biology",
            "Regenessance",
            "Tendrits",
            "Mycelium"
        ]
    }
]





# Load the sounds

acknowledgements = [
	"/home/pi/PLLantoid/v6/media/hmm1.mp3",
	"/home/pi/PLLantoid/v6/media/hmm2.mp3",
	];

introduction = "/home/pi/PLLantoid/v6/samples/intro1.mp3"
outroduction = "/home/pi/PLLantoid/v6/samples/outro1.mp3"

reflection = '/home/pi/PLLantoid/v6/media/initiation.mp3'

cleanse = '/home/pi/PLLantoid/v6/media/cleanse.mp3'




#===================  Threadings

def ambient_background(music, stop_event):
    while not stop_event.is_set():
        playsound(music)


def acknowledge():
    return random.choice(acknowledgements)


#==================== Global vars


opening = ""
closing = ""
prompt_text = ""
turns = []



def turnsAppend(agent, text):
    turns.append({ "speaker": agent, "text": text })


def updateprompt():
    lines = []
    transcript = ""
    for turn in turns:
        text = turn["text"]
        speaker = turn["speaker"]
        lines.append(speaker + ": " + text)
    transcript = "\n".join(lines)
    return prompt_text.replace("{{transcript}}", transcript)


def setup():

    global prompt_text;
    global opening;
    global closing;
    global selected_words_string


    # load the personality of Plantony
    prompt_text = open("/home/pi/PLLantoid/v6/plantony.txt").read().strip()

    opening = random.choice(opening_lines)
    closing = random.choice(closing_lines) 

    turns.append({ "speaker": AGENT, "text": opening })


    # for Plantony oracle

    selected_words = []

    # select one item from each category
    for category in word_categories:
        selected_words.append(random.choice(category['items']))

    # join the selected words into a comma-delimited string
    selected_words_string = ', '.join(selected_words)

    # print the result
    print("Plantony is setting up. His seed words are: " + selected_words_string)



