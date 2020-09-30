
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


def read_config(path, config_dict: dict = {}) -> dict:
    '''Reads an INI formatted configuration file and parses it to a nested dict
    
    Each category in the INI file will be parsed as a separate nested dictionary. A default `config_dict` can be provided with default values for the parameters. Parameters under the "main" section will be parsed in the main dictionary. All data types will be converted by `ast.literal_eval()`.

    Parameters
    ----------
    path : str
        Path to the file. Must include the desired extension. 
    config_dict : dict, optional
        Nested dictionary of default parameters

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


def flatten_dict(nested_dict: dict, flat_dict : dict = {}) -> dict:
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
            flatten_dict(value, flat_dict)
        else:
            flat_dict[key] = value
    return flat_dict



def plot_config(write: bool = False, **kwargs):

    config_dict = {
        "scale": {
            "figure_size": 10,
            "3d_layer_distance": 8,
        },
        "colors": {
            "background_color": (1, 1, 1),
            "edge_color": (0.8, 0.8, 0.8),
            "qubit_edge_color": (0.7, 0.7, 0.7),
            "qubit_face_color": (0.1, 0.1, 0.1),
            "x_primary_color": (0.9, 0.3, 0.3),
            "z_primary_color": (0.5, 0.5, 0.9),
            "y_primary_color": (0.9, 0.9, 0.5),
            "x_secundary_color": (0.9, 0.7, 0.3),
            "z_secundary_color": (0.3, 0.9, 0.3),
            "y_secundary_color": (0.9, 0.9, 0.5),
            "x_tertiary_color": (0.5, 0.1, 0.1),
            "z_tertiary_color": (0.1, 0.1, 0.5),
            "y_tertiary_color": (0.9, 0.9, 0.5),
            "alpha_primary": 0.35,
            "alpha_secundary": 0.5,
        }, 
        "line": {
            "lw_primary": 1.5,
            "lw_secundary": 1,
            "ls_primary": '":"',
            "ls_secundary": '"--"',
            "ls_tertiary": '"-"',
        },
        "scatter": {
            "2d_scatter_size": 0.1,
            "3d_scatter_size": 30,
        },
        "interactive": {
            "pick_radius": 5
        }
    }
    config_path = "./plot.ini"

    if write:
        write_config(config_dict, config_path)

    if os.path.exists(config_path):
        read_config(config_path, config_dict)

    return config_dict

print(plot_config(True))