'''
2020 Mark Shui Hu

www.github.com/watermarkhu/OpenSurfaceSim
_____________________________________________

Contains methods of the simulation configuration
'''
import configparser
import json
import os
from .info.benchmark import BenchMarker
from .info.printing import print_setup
from types import ModuleType


def read_config(path):
    '''Reads a config.ini file located and parses all data in it'''

    config = configparser.ConfigParser()
    config.read(path)

    data = {}
    for section, items in config._sections.items():
        for key, item in items.items():
            data[key] = json.loads(item)

    return data


def write_config(path, configdict, sectionname=None):
    '''
    writes a config.ini file to the path
    If no sectionname is provided, the configdict must be a dict of dicts as 
        {section1: {key: value},
        section2: {key: value}}
    If a section name is provided, the configdict is a dict of configuations
    '''
    config = configparser.ConfigParser()

    if os.path.exists(path):
        config.read(path)

    change = False

    if sectionname is None:
        for section, sectionconfig in configdict.items():
            if section not in config:
                config[section] = sectionconfig
                change = True
    else:
        if sectionname not in config:
            config[sectionname] = configdict
            change = True

    if change:
        with open(path, 'w') as configfile:
            config.write(configfile)


def decoderconfig(decoder, path="opensurfacesim/decoder/decoder.ini"):
    '''
    Loads or writes the configuration variables of a decoder to a single decoder.ini file. 
    The standard configurations must be stored at decoder.config and is a dictionary
    If decoder.ini has no section on the current decoder, it is added to the configuration file. If the section already exists, its configuration is loaded. 
    '''
    config = configparser.ConfigParser()

    if os.path.exists(path):
        config.read(path)

    if decoder.name in config:
        data = {}
        for key, item in config[decoder.name].items():
            data[key] = json.loads(item)
    else:
        config[decoder.name] = decoder.config
        with open(path, 'w') as configfile:
            config.write(configfile)
        data = decoder.config


    for key, value in data.items():
        setattr(decoder, key, value)


def setup_decoder(code, decode_module, size,
                  perfect_measurements=True,
                  benchmark=False,
                  info=True,
                  **kwargs):
    '''
    Initilizes the graph and decoder type based on the lattice structure.
    '''  
    bmarker = BenchMarker() if benchmark else None
    kwargs["benchmarker"] = bmarker

    # Get graph object
    if perfect_measurements:
        from .code import graph_2D as go
    else:
        from .code import graph_3D as go
    try:
        graph = getattr(go, code)(size, **kwargs)
    except:
        raise NameError("Code type not defined in graph")

    # Get decoder object
    if type(decode_module) == str:
        decode_modules = __import__("opensurfacesim.decoder", fromlist=[decode_module])
        try:
            decode_module = getattr(decode_modules, decode_module)
        except:
            raise  ModuleNotFoundError("Unknown decoder name")
    elif type(decode_module) == ModuleType:
        if decode_module.__package__ != 'simulator.decoder':
            raise TypeError("Decoder is not a simulator.decoder module")
    else:
        raise TypeError("Decoder argument must be either a decoder module or name (string) or decoder module")
    
    # Get code-specific decoder
    try:
        decoder = getattr(decode_module, code)(graph, **kwargs)
    except:
        raise NameError("Code type not defined in decoder class")

    if info:
        print_setup(graph, decoder)
        
    return decoder


# def default_config(**kwargs):
#     '''
#     stores all settings of the decoder
#     '''
#     config = dict(
#         seeds=[],
#         print_steps=0,
#         plot2D=0,
#         plot3D=0,
#         plotUF=0,
#         step_find=0,
#         step_bucket=0,
#         step_cluster=0,
#         step_cut=0,
#         step_peel=0,
#         step_node=0,
#     )
#     for key, value in kwargs.items():
#         if key in config:
#             config[key] = value

#     return config
