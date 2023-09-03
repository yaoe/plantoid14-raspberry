import toml

def load_config(config_path):

    return toml.load(config_path)

def str_to_bool(s):
    s = s.strip().lower()
    lookup = {'true': True, 'false': False}
    return lookup.get(s, "Invalid literal for boolean")