
from collections import defaultdict as ddict
import configparser
import ast
import os


def write_config(config_dict: dict, path:str) -> None:
    '''Writes a configuration file to the path.

    Parameters
    ----------
    config_dict : dict
        Dictionary of configuration parameters. Can be nested.
    path : str
        Path to the file. Must include the desired extension. 
    '''
    config = configparser.ConfigParser()

    for key, value in config_dict.items():
        if type(value) == dict:
            config[key] = value
        else:
            config["main"][key] = value

    with open(path, 'w') as configfile:
        config.write(configfile)


def read_config(path: str, config_dict: dict = ddict(dict)) -> dict:
    '''Reads an INI formatted configuration file and parses it to a nested dict
    
    Each category in the INI file will be parsed as a separate nested dictionary. A default `config_dict` can be provided with default values for the parameters. Parameters under the "main" section will be parsed in the main dictionary. All data types will be converted by `ast.literal_eval()`.

    Parameters
    ----------
    path : str
        Path to the file. Must include the desired extension. 
    config_dict : dict, optional
        Nested dictionary of default parameters

    Returns
    -------
    dict
        Parsed dictionary.

    Examples
    --------
    Let us look at the following example INI file.

        [main]
        param1 = hello

        [section]
        param2 = world
        param3 = 0.1

    This file will be parsed as follows

        >>> read_config("config.ini")
        {
            "param1": "hello",
            "section": {
                "param2": "world",
                "param3": 0.1
            }
        }
    '''

    config = configparser.ConfigParser()
    config.read(path)

    for section_name, section in config._sections.items():
        section_config = config_dict if section_name == "main" else config_dict[section_name]
        for key, item in section.items():
            section_config[key] = ast.literal_eval(item)

    return config_dict


def flatten_dict(nested_dict: dict, flat_dict : dict = {}, key_prefix: str = "") -> dict:
    """Flattens al nested dictionaries in `nested_dict` to a single dictionary

    Parameters
    ----------
    nested_dict : dict
        Dictionary to flatten.

    Returns
    -------
    dict
        Flat dictionary with no nested dictionaries.
    """
    for key, value in nested_dict.items():
        if type(value) == dict:
            flatten_dict(value, flat_dict, key_prefix + key + "_")
        else:
            flat_dict[key_prefix + key] = value
    return flat_dict
