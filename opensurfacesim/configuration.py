from collections import defaultdict
import configparser
import ast
import os
from typing import Optional
from pathlib import Path

    
class AttributeDict(defaultdict):
    def __init__(self):
        super(AttributeDict, self).__init__(AttributeDict)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value


def write_config(config_dict: dict, path: str):
    """Writes a configuration file to the path.

    Parameters
    ----------
    config_dict : dict
        Dictionary of configuration parameters. Can be nested.
    path : str
        Path to the file. Must include the desired extension.
    """
    config = configparser.ConfigParser()

    for key, value in config_dict.items():
        if type(value) == dict:
            config[key] = value
        else:
            config["main"][key] = value

    with open(path, "w") as configfile:
        config.write(configfile)


def read_config(path: Path, config_dict: Optional[dict] = None) -> dict:
    """Reads an INI formatted configuration file and parses it to a nested dict

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
    """
    if config_dict is None:
        config_dict = defaultdict(dict)

    config = configparser.ConfigParser()
    config.read(path)

    for section_name, section in config._sections.items():
        section_config = config_dict if section_name == "main" else config_dict[section_name]
        for key, item in section.items():
            try: 
                section_config[key] = ast.literal_eval(item)
            except:
                section_config[key] = item
    return config_dict


def init_config(ini_file, write: bool = False, **kwargs):
    """Reads the default and the user defined INI file.

    First, the INI file stored in file directory is read and parsed. If there exists another INI file in the working directory, the attributes defined there are read, parsed and overwrites and default values.

    Parameters
    ----------
    write : bool
        Writes the default configuration to the working direction of the user.

    See Also
    --------
    write_config
    read_config
    """
    config_dict = read_config(ini_file)
    config_path = Path.cwd() / ini_file.name
    if write:
        write_config(config_dict, config_path)
    if os.path.exists(config_path):
        read_config(config_path, config_dict)
    return config_dict



def flatten_dict(nested_dict: dict, flat_dict: dict = {}, key_prefix: str = "") -> dict:
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


def get_attributes(rc_dict: dict, attribute_names: dict, **kwargs) -> dict:
    """Gets a list of attributes stored in some object.

    For most attributes from `attribute_names`, this function tries to find the attribute with the same name as the value from the dictionary. If the attribute value begins with `"~"` however, the literal value after `"~"` is taken as the attribute value. A nested dictionary for `attribute_names` is also allowed. 

    Parameters
    ----------
    obj : object
        Object to extract the attributes from.
    attribute_names : dict of str
        A dictionary with strings names of attributes to extract from `obj`.
    name : str, optional
        Optional name hint for error report.

    Returns
    -------
    dict
        Parsed attribute dictionary.

    Examples
    --------
    Get attribute `attr_name` from object and parse `literal_attr` as string. 

        >>> get_attributes(obj, {"obj_attr": "attr_name", "literal_attr": "~red"})
        {"obj_attr": obj.attr_name, "literal_attr": "red"}
    
    Parsed nested dict of attribute names.

        >>> get_attributes(obj {
                "nested_attributes": {
                    "obj_attr": "attr_name",
                }
                "unnested_attribute": "unnested_name"
            })
        {"nested_attributes": {"obj_attr": obj.attr_name}, "unnested_attribute": obj.unnested_name}
    """
    attributes = {}
    for key, attr in attribute_names.items():
        if type(attr) == dict:      # Get nested dictionaries
            attributes[key] = get_attributes(rc_dict, attr)
        elif type(attr) == str:     # Parse if attribute is string
            if attr[0] == "~":      # Save literal string value
                attributes[key] = attr[1:]
            else:                   # Get attribute from obj
                try:
                    attributes[key] = rc_dict[attr]
                except:
                    attributes[key] = attr
        else:
            attributes[key] = attr
    return attributes
