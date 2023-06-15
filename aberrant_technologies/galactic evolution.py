import numpy as np


def iterate_nearest_neighbor(data, chunk_size=500, accept_variance=2, verbose=0):
    """This function attempts to split large star maps into manageable chunks of equal size

    A Random subsample of the data is used as a seed,
    then over/under sized chunks are adjusted by deleting themselves (too low),
    or by selecting a point within that chunk to become a new chunk center (too high).

    Parameters
    ----------
    data
        A list of 3d coordinates to be separated into chunks
    chunk_size
        The preferred number of data points for each chunk
    accept_variance
        defines maximum (x*var) and minimum (x/var) chunk size accepted
    verbose
        If this is increased, the function will print extra messages to stdout

    Returns
    -------
    tuple : tuple
        A tuple containing <br> [0] An array of coordinates which denote the logical centre of each chunk. <br>
                           [1] A nested list of datapoint coordinates, chunk indices match the index output.
    """
    from scipy.spatial import cKDTree
    import random

    index = np.array(random.choices(data, k=int(len(data)/chunk_size)))
    max_chunk_size = chunk_size + (chunk_size / accept_variance)
    min_chunk_size = chunk_size / accept_variance
    iteration = 0

    while True:
        iteration += 1

        tree = cKDTree(index)

        chunks = [list() for _ in range(len(index))]
        for p in range(len(data)):
            q = np.array(data[p])
            nearest_chunk = int(tree.query(q)[1])
            chunks[nearest_chunk].append(p)

        delete_list = []
        add_list = []
        for chunk in range(len(chunks)):
            if len(chunks[chunk]) > max_chunk_size:
                add_list.append(data[random.choice(chunks[chunk])])
            elif len(chunks[chunk]) < min_chunk_size:
                delete_list.append(chunk)
        if len(add_list) == 0 and len(delete_list) == 0:
            break
        else:
            if verbose > 0:
                print('iteration: ' + str(iteration))
            if verbose > 1:
                print('chunks added: ' + str(len(add_list)) +
                      '  --  chunks deleted: ' + str(len(delete_list)) +
                      '  --  total chunks: ' + str(len(chunks)))
            index = np.delete(index, delete_list, axis=0)
            for i in add_list:
                index = np.vstack([index, i])

    return index, chunks


def nearest_chunk(index):
    from scipy.spatial import cKDTree
    import numpy as np

    tree = cKDTree(index)
    out = np.zeros((len(index), len(index)))
    for i in range(len(index)):
        q = tree.query(index[i], k=7)
        for j in range(6):
            out[i][q[1][j+1]] = q[0][j+1]
    return out


def chunk_connections(index):
    """ This function converts chunks locations into chunk associations

    Parameters
    ----------
    index
        a list of chunk center points in x,y,z space

    Returns
    -------
    list
        sorted list of chunks by distance from chunk[0]
    """
    from scipy.spatial import cKDTree
    tree = cKDTree(index)
    return [tree.query(i, k=len(index))[1] for i in index]


def initialise_stellar_dictionary(data, index, chunks, link_types):
    """Finds nearest n nearest neighbors for each point in data and assigns some random variables to each point.
    Uses chunked data in order to reduce load on scipy.distance.cKDTree

    Parameters
    ----------
    data
        array of 3d coordinates
    index
        chunk index
    chunks
        chunked sublist of coordinates
    link_types
        config data from file, user can specify, <br>
        max neighbors - the maximum number of nearest neighbors to convert to links <br>
        min neighbors - the minimum number of nearest neighbors to convert to links <br>
        types - the types of links formed in distance order format = [type][maximum distance cutoff] <br>
        random and normal - defines new attributes which contain random.gauss (if attribute = "True")
        or random.random
    Returns
    -------
    dict
        dictionary of instances containing; <br>
        names in chunk_id-position_id format, <br>
        coordinates, <br>
        n nearest neighbors as link dictionary, <br>
        custom attributes defined by random_and_normal, <br>
        and an empty tags list.
    """
    from scipy.spatial import cKDTree
    from scipy.sparse.csgraph import minimum_spanning_tree

    sd = {}
    link_bins = link_types['bins']
    link_types = link_types['types']

    for chunk in range(len(index)):
        print(chunk)
        names = {}
        chunk_indexes = {}
        points = []
        n = 0
        for c in index[chunk][:3]:
            for p in range(len(chunks[c])):
                names[n] = '-'.join([str(c), str(p)])
                chunk_indexes[n] = [c, p]
                points.append(data[chunks[c][p]])
                n += 1

        tree = cKDTree(points)
        dm = tree.sparse_distance_matrix(tree, max_distance=6)
        sea = minimum_spanning_tree(dm)

        links = {k: [] for k in range(sea.shape[0])}
        for i in range(sea.shape[0]):
            ind = list(sea.indices[sea.indptr[i]:sea.indptr[i+1]])
            dat = list(sea.data[sea.indptr[i]:sea.indptr[i+1]])
            for j in range(len(ind)):
                links[ind[j]].append({'location': names[i],
                                      'type': link_types[np.digitize(dat[j], link_bins)],
                                      'dist': float(dat[j])})
                links[i].append({'location': names[ind[j]],
                                 'type': link_types[np.digitize(dat[j], link_bins)],
                                 'dist': float(dat[j])})

        for n in range(len(chunks[chunk])):
            sd[names[n]] = {'name': names[n],
                            'extraplanar_coords': points[n].tolist(),
                            'links': links[n],
                            'tags': [],
                            }

    return sd


def planet_generation(sd, geography):
    """Apply planets to a given dictionary of star systems.

    Parameters
    ----------
    sd
    geography

    Returns
    -------

    """
    import random
    from scipy.spatial import cKDTree
    # from scipy.spatial.distance import pdist

    for s in sd:
        n_bi = geography['reserved']['n_biomes']
        temp = geography['reserved']['temperature']

        n = max(2, int(random.gauss(*n_bi)))
        r = 100
        theta = np.random.random(n) * 2 * np.pi
        phi = np.arccos((2 * np.random.random(n)) - 1)
        rr = pow(np.random.random(n), 1 / 3) * r
        x = (rr * np.sin(phi) * np.cos(theta))
        y = (rr * np.sin(phi) * np.sin(theta))
        z = (rr * np.cos(phi))
        t = np.random.normal(*temp, n)
        c = np.swapaxes(np.array([x, y, z]), 0, 1)

        if n > 4:
            tree = cKDTree(c)
            links = [tree.query(c[j], k=4) for j in range(n)]
            tt = [np.mean(t[links[i][1]]) for i in range(n)]
        else:
            array_n = [n-1] + list(range(n)) + [0]
            links = [[[sum(pow(c[array_n[i]] - c[array_n[i + 2]], 2)) ** 0.5],
                      [array_n[i], array_n[i + 2]]] for i in range(n)]
            tt = [np.mean(t[array_n[i:i+3]]) for i in range(n)]

        sd[s]['planets'] = [{'name': s + '-' + str(i),
                             'temperature': float(tt[i]),
                             'local_coords': [float(k) for k in c[i].tolist()],
                             'links': [{'location': s + '-' + str(links[i][1][j]),
                                        'dist': float(links[i][0][j])} for j in range(1, len(links[i][0]))]} for i in range(n)]

        for p in range(len(sd[s]['planets'])):
            for r_v in geography['random_and_normal']:
                sd[s]['planets'][p][r_v] = random.gauss(*geography['random_and_normal'][r_v]) \
                    if type(geography['random_and_normal'][r_v]) == list else random.random()

    return sd


def define_random_attributes(sd, type_logic):
    """Using previously defined numbers, np.digitize, and a list of bins,
     converts dictionary values into other specified values

    Parameters
    ----------
    sd
        systems dictionary
    type_logic
        a dictionary which defines how to adjust other variables. Using number from a given attribute <br>
        To edit the value of a dictionary attribute, format = [given attribute][edit attribute][[bins], [values]] <br>
        To modulate a value, format = [given attribute][edit attribute][old value][[bins], [new value]]

    Returns
    -------
    dict
        systems dictionary
    """

    for s in sd:
        for p in range(len(sd[s]['planets'])):
            for r_var in type_logic:
                r = sd[s]['planets'][p][r_var]
                for u_var in type_logic[r_var]:
                    if type(type_logic[r_var][u_var]) is list:
                        # if it overwrites
                        bins = type_logic[r_var][u_var][0]
                        try:
                            sd[s]['planets'][p][u_var] = type_logic[r_var][u_var][1][np.digitize(r, bins)]
                        except IndexError:
                            pass
                    else:
                        # if it modifies
                        bins = type_logic[r_var][u_var][sd[s]['planets'][p][u_var]][0]
                        sd[s]['planets'][p][u_var] = \
                            type_logic[r_var][u_var][sd[s]['planets'][p][u_var]][1][np.digitize(r, bins)]

    return sd


def connection_attributes(sd, tag_logic):
    """defines how shared link types can form connection webs (e.g. land type links can form a connected continent)

    Adds two new attributes to sd;

    ['link type link'] is a unique identifier shared by all systems connected by that link type.

    ['link type tags'] is a list of tags a system has gained systems connected by that link type.

    Parameters
    ----------
    sd
        systems dictionary
    tag_logic
        A dictionary that defines for [link type][attribute][value] what tags will be included in the
        sd[system]['link type tags'] variable.

    Returns
    -------
    sd
        systems dictionary

    """
    for s in sd:
        for c_var in tag_logic:
            for p in range(len(sd[s]['planets'])):
                if sd[s]['planets'][p][c_var] in tag_logic[c_var]:
                    sd[s]['tags'].append(tag_logic[c_var][sd[s]['planets'][p][c_var]])

    return sd


def alt_connection_attributes(sd, tag_logic):
    """defines the affect a variable can have on linked systems

    Parameters
    ----------
    sd
        systems dictionary
    tag_logic
        A dictionary that defines for [attribute][value] what string will be added to all systems linked by [link type].
        <br> dict is in format dict[dict attribute][value][link type] = 'string'

    Returns
    -------
    dict
        systems dictionary
    """
    for s in sd:
        for c_var in tag_logic:
            for p in range(len(sd[s]['planets'])):
                if sd[s]['planets'][p][c_var] in tag_logic[c_var]:
                    for link in sd[s]['links']:
                        if link['type'] in tag_logic[c_var][sd[s]['planets'][p][c_var]]:
                            sd[link['location']]['tags'].append(
                                tag_logic[c_var][sd[s]['planets'][p][c_var]][link['type']])

    return sd


def cleanup_systems_dictionary(sd, clean_logic):
    """cleans up numerical attributes of systems dictionary by scaling within bounds or deleting,
    also converts dict labels to str

    Parameters
    ----------
    sd
        systems dictionary
    clean_logic
        A dictionary which defines numerical variables to scale [range,minima] or delete 'delete'

    Returns
    -------
    dict
        systems dictionary

    """
    for v in clean_logic:
        if clean_logic[v] == 'delete':
            for s in sd:
                for p in range(len(sd[s]['planets'])):
                    del(sd[s]['planets'][p][v])
        elif clean_logic[v] == 'mode':
            for s in sd:
                counts = []
                for p in range(len(sd[s]['planets'])):
                    counts.append(sd[s]['planets'][p][v])
                sd[s][v+'_mode'] = max(set(counts), key=counts.count)
        else:
            maxmin = [0, 0]
            for s in sd:
                for p in range(len(sd[s]['planets'])):
                    if sd[s]['planets'][p][v] > maxmin[0]:
                        maxmin[0] = sd[s]['planets'][p][v]
                    elif sd[s]['planets'][p][v] < maxmin[1]:
                        maxmin[1] = sd[s]['planets'][p][v]

            m = clean_logic[v][0]/(maxmin[0]-maxmin[1])
            c = (maxmin[1]*m)-clean_logic[v][1]
            for s in sd:
                for p in range(len(sd[s]['planets'])):
                    sd[s]['planets'][p][v] = (sd[s]['planets'][p][v] * m) + c

    return sd


def count_systems(sd):
    biomes = {}
    links = {}
    tags = {}
    distances = []
    nolinks = 0
    for s in sd:
        for p in range(len(sd[s]['planets'])):
            if sd[s]['planets'][p]['biome'] in biomes:
                biomes[sd[s]['planets'][p]['biome']] += 1
            else:
                biomes[sd[s]['planets'][p]['biome']] = 1
        for link in sd[s]['links']:
            if link['type'] in links:
                links[link['type']] += 1
            else:
                links[link['type']] = 1
        for t in sd[s]['tags']:
            if t in tags:
                tags[t] += 1
            else:
                tags[t] = 1
        try:
            distances.append(sd[s]['links'][0]['dist'])
        except IndexError:
            nolinks += 1
            pass

    print(nolinks)
    plotly_sorted_bar(biomes, 'Bar').write_html('biomes.html', auto_open=True)
    # plotly_sorted_bar(links, 'Bar').write_html('links.html', auto_open=True)
    # plotly_sorted_bar(tags, 'Bar').write_html('tags.html', auto_open=True)
    # plotly_sorted_bar(distances, 'Scatter', mode='lines').write_html('link_distances.html', auto_open=True)


def plotly_sorted_bar(data, func, **kwargs):
    """A shorthand method for drawing a sorted bar chart

    Parameters
    ----------
    data
        input data, can be either dict or list
    func
        desired plotly plotting function where all kwargs sent to

    Returns
    -------
    plotly.graph_objs._figure.Figure
        go.Figure object to be plotted
    """
    import plotly.graph_objects as go

    if type(data) == dict:
        data = {k: data[k] for k in sorted(data, key=data.get, reverse=True)}
        data = go.__getattr__(func)(x=list(data), y=list(data.values()), **kwargs)
    elif type(data) == list:
        data = go.__getattr__(func)(x=list(range(len(data))), y=sorted(data), **kwargs)
    else:
        print('please only use type dict or list')
        raise TypeError

    return go.Figure(data=data, layout=go.Layout(template='plotly_dark'))


def chunk_systems_dictionary(sd, chunks, folder):
    import orjson

    for chunk in range(len(chunks)):
        sc = {}
        for p in range(len(chunks[chunk])):
            sc[str(chunk)+'-'+str(p)] = sd[str(chunk)+'-'+str(p)]
        with open(folder + str(chunk) + '.json', 'wb') as f:
            f.write(orjson.dumps(sc))


def main(cfg):
    """

    Parameters
    ----------
    cfg
        Setup class object, contains all variables needed to run the script

    Returns
    -------

    """
    import orjson

    system_coordinates = np.load(cfg.coordinates_file, allow_pickle=False)

    try:
        # raise FileNotFoundError
        system_index = np.load(cfg.folder+'index.npy', allow_pickle=False)
        with open(cfg.folder+'chunks.json', 'rb') as chunk_file:
            indexed_chunks = orjson.loads(chunk_file.read())
    except FileNotFoundError:
        system_index, indexed_chunks = iterate_nearest_neighbor(system_coordinates, 600, verbose=2)
        np.save(cfg.folder+'dist_matrix.npy', nearest_chunk(system_index), allow_pickle=False)
        system_index = chunk_connections(system_index)
        np.save(cfg.folder+'index.npy', system_index, allow_pickle=False)
        with open(cfg.folder+'chunks.json', 'wb') as chunk_file:
            chunk_file.write(orjson.dumps(indexed_chunks))

    dd = initialise_stellar_dictionary(system_coordinates, system_index, indexed_chunks, cfg.link_types)
    dd = planet_generation(dd, cfg.planet_seeds)
    dd = define_random_attributes(dd, cfg.type_logic)
    dd = connection_attributes(dd, cfg.link_tags)
    dd = alt_connection_attributes(dd, cfg.network_tags)
    # TODO: mode of a category
    dd = cleanup_systems_dictionary(dd, cfg.cleanup)
    count_systems(dd)
    chunk_systems_dictionary(dd, indexed_chunks, cfg.folder)

    with open(cfg.folder+'all_systems.json', 'wb') as sf:
        sf.write(orjson.dumps(dd))


if __name__ == '__main__':
    # TODO: set config file up properly
    from aberrant_technologies.interface import default
    main(default)
