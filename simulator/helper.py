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
