import configparser
import json
import os


def readconfig(path):
    '''Reads a config.ini file located and parses all data in it'''

    config = configparser.ConfigParser()
    config.read(path)

    data = {}
    for section, items in config._sections.items():
        for key, item in items.items():
            data[key] = json.loads(item)

    return data


def writeconfig(path, configdict, sectionname=None):
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
                config["section"] = sectionconfig
                change = True
    else:
        if sectionname not in config:
            config["sectionname"] = configdict
            change = True

    if change:
        with open(path, 'w') as configfile:
            config.write(configfile)


def decoderconfig(decoder, path="simulator/decoder/decoder.ini"):
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


def sim_setup(code, config, decoder, size, measurex=0, measurez=0, f2d=0, f3d=0, info=True, **kwargs):
    '''
    Initilizes the graph and decoder type based on the lattice structure.
    '''

    if type(decoder) == str:
        decoders = __import__("simulator.decoder", fromlist=[decoder])
        try:
            decoder = getattr(decoders, decoder)
        except:
            print("Error: Decoder type invalid, loading MWPM decoder")
            decoder = getattr(decoders, 'mwpm')
            
    try:
        decoderobject = getattr(decoder, code)(**config, **kwargs)
    except:
        print("Error: Graph type not defined in decoder class")

    if (not f3d and measurex == 0 and measurez == 0) or f2d:
        from simulator.graph import graph_2D as go
    else:
        from simulator.graph import graph_3D as go
        gtype
    graph = getattr(go, code)(size, decoderobject, **config, **kwargs)

    if info:
        print(f"{'_'*75}\n")
        print(f"OpenSurfaceSim\n2020 Mark Shui Hu\nhttps://github.com/watermarkhu/OpenSurfaceSim")
        print(f"{'_'*75}\n\nDecoder type: " + decoderobject.name)
        print(f"Graph type: {graph.name} {code}\n{'_'*75}\n")

    return graph


def default_config(**kwargs):
    '''
    stores all settings of the decoder
    '''
    config = dict(
        seeds=[],
        print_steps=0,
        plot2D=0,
        plot3D=0,
        plotUF=0,
        step_find=0,
        step_bucket=0,
        step_cluster=0,
        step_cut=0,
        step_peel=0,
        step_node=0,
    )
    for key, value in kwargs.items():
        if key in config:
            config[key] = value

    return config
