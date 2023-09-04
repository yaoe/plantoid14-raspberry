def get_text_content():

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

    return opening_lines, closing_lines, word_categories