#!/usr/bin/env python

# coming over here to find I like nbody nested (my most recent iteration) the most
# SRN filled 6, don't even remember how I made it, we're just here
# The nearest neighbours thing didn't help with clustering whatsoever but it does look perrrty tho
# Glad I can have the history where I deleted that all then ;)


coordinates_file = '../nbody_SRN_filled.npy'

folder = '../nbody_nested_test/'

plotly_colours = {"background": "#00001a",
                  "sea": "#1375fd", "air": "#738080",
                  "land": "#bb8534", "mountains": "#738080",
                  "temperate forest": "#68a704", "rainforest": "#67e139",
                  "savannah": "#b3b05c", "desert": "#eac833",
                  "steppe": "#5e3e30", "chaparral": "#bb8534",
                  "tundra": "#d6f3fe", "tiaga": "#5a713b",
                  "faywild": "#35ff8f", "shadowfell": "#101820",
                  "astral": "#8276e6", "ethereal": "#d63d75",
                  "elemental fire": "#b90c14", "elemental water": "#270098",
                  "elemental air": "#a0c7c7", "elemental earth": "#40312a",
                  "Hades": "#b100c4", "Gehenna": "#b100c4", "Hell": "#b100c4", "Acheron": "#b100c4",
                  "Limbo": "#b100c4", "Pandemonium": "#b100c4", "The Abyss": "#b100c4", "Carceri": "#b100c4",
                  "Mechanus": "#b100c4", "Arcadia": "#b100c4", "Mount Celestia": "#b100c4", "Bytopia": "#b100c4",
                  "Elysium": "#b100c4", "The Beastlands": "#b100c4", "Arborea": "#b100c4", "Ysgard": "#b100c4"}

link_types = {"types": ["land", "sea", "air", "astral"],
              "bins": [0.5, 1, 2, 6]}

planet_seeds = {"reserved": {"n_biomes": [11, 2.5],
                             "temperature": [17.5, 20]},
                "random_and_normal": {"biome": False,
                                      "inner_filter": "False",
                                      "outer_filter": "False"},
                }

type_logic = {"biome": {"biome": [[0.21, 0.7],
                                  ["dry", "medium", "wet"]]
                        },
              "temperature": {"biome": {"dry": [[10, 16],
                                                ["tundra", "steppe", "desert"]],
                                        "medium": [[8, 22, 26],
                                                   ["tiaga", "temperate forest", "chaparral", "savannah"]],
                                        "wet": [[20],
                                                ["temperate forest", "rainforest"]]}
                              },
              "inner_filter": {"biome": {"chaparral": [[0.01, 0.06],
                                                       ["elemental fire", "faywild", "chaparral"]],
                                         "desert": [[0.05, 0.09],
                                                    ["elemental fire", "elemental earth", "desert"]],
                                         "rainforest": [[0.05, 0.1, 0.11],
                                                        ["faywild", "elemental water", "elemental fire", "rainforest"]],
                                         "savannah": [[0.06],
                                                      ["faywild", "savannah"]],
                                         "steppe": [[0.01, 0.16, 0.21],
                                                    ["shadowfell", "elemental air", "elemental earth", "steppe"]],
                                         "temperate forest": [[0.05, 0.075, 0.08, 0.085, 0.09, 0.095],
                                                              ["faywild", "shadowfell",
                                                               "elemental earth", "elemental water",
                                                               "elemental air", "elemental fire",
                                                               "temperate forest"]],
                                         "tiaga": [[0.02],
                                                   ["faywild", "tiaga"]],
                                         "tundra": [[0.02],
                                                    ["elemental water", "tundra"]]
                                         }
                               },
              "outer_filter": {"biome": [[0.0002, 0.0004, 0.0006, 0.0008,
                                          0.0010, 0.0012, 0.0014, 0.0016,
                                          0.0018, 0.002, 0.0022, 0.0024,
                                          0.0026, 0.0028, 0.0030, 0.0032,
                                          0.0056, 0.0080],
                                         ["Hades", "Gehenna", "Hell", "Acheron",
                                          "Limbo", "Pandemonium", "The Abyss", "Carceri",
                                          "Mechanus", "Arcadia", "Mount Celestia", "Bytopia",
                                          "Elysium", "The Beastlands", "Arborea", "Ysgard",
                                          "astral", "ethereal"]]
                               },
              }

link_tags = {"biome": {"Hades": "Hades Influenced", "Gehenna": "Gehenna Influenced",
                       "Acheron": "Acheron influenced", "Hell": "Hell influenced",
                       "Limbo": "Limbo influenced", "Pandemonium": "Pandemonium influenced",
                       "The Abyss": "Influenced by The Abyss", "Carceri": "Carceri influenced",
                       "Mechanus": "Mechanus influenced", "Arcadia": "Arcadia influenced",
                       "Mount Celestia": "Influenced by Mount Celestia", "Bytopia": "Bytopia influenced",
                       "Elysium": "Elysium influenced", "The Beastlands": "Influenced by The Beastlands",
                       "Arborea": "Arborea influenced", "Ysgard": "Ysgard influenced",
                       "astral": "astrally enhansed", "ethreal": "ethreally enhansed",
                       "elemental fire": "fire touched", "elemental water": "water touched",
                       "elemental earth": "earth touched", "elemental air": "air touched"}
             }

network_tags = {"biome": {"Hades": {"land": "The River Styx",
                                    "sea": "The River Styx"},
                          "astral": {"land": "astral cliff",
                                     "sea": "astral waterfall"},
                          "ethereal": {"land": "ethereal cliff",
                                       "sea": "ethereal waterfall"}
                          }
                }

cleanup = {"temperature": [80, -40],
           'biome': 'mode',
           "inner_filter": "delete",
           "outer_filter": "delete"}

# TODO: Think about UI
# from aberrant_technologies.interface import AstralSynthesis, AstralInterpreter

# Mental assimilation complete, welcome back feeble tourist

# generator = AstralSynthesis('folder')
# saves or loads bunch of bullshit into the folder
# configuration must contain x to proceed
# generator.configuration
# generator.generate.instances()
# generator.generate.geography()

# map = AstralInterpreter('folder')
# map.search.attribute.value(max distance, max to return)
# map.search.network.attribute.value(network size min, network size max, max distance, max to return)
# map.submap(seed, distance, size, pretty plots, mode, filename)
# map.network(network id, pretty plots, mode, filename)
# map.path(from, to)

# Actually how about, it's always a 3d plot, it just depends what you're putting on that 3d plot.
# search? well don't just gimmie as a list, show me where you all are!
# submap is just a type of search.
# first step is to encode my plotting thing into dash
# I do think you should be able to run it through importing it though. It's just how you do a python script


class Setup:
    def __init__(self):
        self.coordinates_file = coordinates_file
        self.folder = folder
        self.plotly_colours = plotly_colours
        self.link_types = link_types
        self.planet_seeds = planet_seeds
        self.type_logic = type_logic
        self.link_tags = link_tags
        self.network_tags = network_tags
        self.cleanup = cleanup
        self.biomes = list(plotly_colours.keys())[5:]
        self.tags = list(link_tags['biome'].values())
        for i in network_tags['biome']:
            self.tags.extend(network_tags['biome'][i].values())


default = Setup()

