import configparser
import json


def getconfigdict(path):
    '''Reads a config.ini file located and parses all data in it'''

    config = configparser.ConfigParser()
    config.read(path)

    data = {}
    for section, items in config._sections.items():
        for key, item in items.items():
            data[key] = json.loads(item)

    return data


def sim_setup(code, config, decoder, size, measurex=0, measurez=0, f2d=0, f3d=0, **kwargs):
    '''
    Initilizes the graph and decoder type based on the lattice structure.
    '''

    print(f"{'_'*75}\n")
    print(f"OpenSurfaceSim\n2020 Mark Shui Hu\nwww.github.com/watermarkhu/OpenSurfaceSim")

    if type(decoder) == str:
        try:
            decoders = __import__("simulator.decoder", fromlist=[decoder])
            decoder = getattr(decoders, decoder)
        except:
            print("Decoder type invlid")
    try:
        decoder = getattr(decoder, code)(**config, **kwargs)
    except:
        print("Graph type not defined in decoder class")

    print(f"{'_'*75}\n\nDecoder type: " + decoder.name)

    if (not f3d and measurex == 0 and measurez == 0) or f2d:
        from simulator.graph import graph_2D as go
        print(f"Graph type: 2D {code}\n{'_'*75}\n")
    else:
        from simulator.graph import graph_3D as go
        print(f"Graph type: 3D {code}\n{'_'*75}\n")
    graph = getattr(go, code)(size, decoder, **config, **kwargs)

    return graph


def default_config(**kwargs):
    '''
    stores all settings of the decoder
    '''
    config = dict(
        seeds=[],
        fbloom=0.5,
        dg_connections=0,
        directed_graph=0,
        print_steps=0,
        plot2D=0,
        plot3D=0,
        plotUF=0,

        plot_find=0,
        plot_bucket=0,
        plot_cluster=0,
        plot_cut=0,
        plot_peel=0,
        plot_node=0,
    )

    for key, value in kwargs.items():
        if key in config:
            config[key] = value

    return config


def writeplotconfig():
    config = configparser.ConfigParser()
    config['Scale'] = {'plot_size' : '10',
                       'linewidth' : '1.5',
                       'scatter_size' : '30',
                       'qubitsize' : '0.1',
                       'z_distance' : '8',
                       'picksize' : '5'}
    config['Colors'] = {'cw' : '[1, 1, 1]',
                        'cl' : '[0.8, 0.8, 0.8]',
                        'cq' : '[0.7, 0.7, 0.7]',
                        'cx' : '[0.9, 0.3, 0.3]',
                        'cz' : '[0.5, 0.5, 0.9]',
                        'cy' : '[0.9, 0.9, 0.5]',
                        'cx2' : '[0.9, 0.7, 0.3]',
                        'cz2' : '[0.3, 0.9, 0.3]',
                        'cx3' : '[0.5, 0.1, 0.1]',
                        'cz3' : '[0.1, 0.1, 0.5]',
                        'alpha' : '0.35'}
    config["Linestyles"] = {'lsx' : '":"',
                            'lsy' : '"--"',
                            'uflsx' : '"-"',
                            'uflsy' : '"--"'}
    with open('simulator/plot.ini', 'w') as configfile:
        config.write(configfile)
