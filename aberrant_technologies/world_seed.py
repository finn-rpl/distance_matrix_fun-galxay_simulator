

def nbody_srn3d():
    import numpy as np
    import nbody

    n = 1500
    p = 3
    x0 = np.random.normal(0, 20, (n, p))
    v0 = np.random.normal(0, 50, (n, p))
    q = np.random.normal(0, 0.0000001, (n,))
    r = np.random.normal(8, 2, (n,))
    m = np.random.normal(8, 1, (n,))

    m[m < 0] = np.abs(m[m < 0])
    m[m == 0] = 0.001

    r[r < 0] = np.abs(r[r < 0])
    r[r == 0] = 1E-3

    xframes = [x0]
    vframes = [v0]

    s = nbody.spheres(x0=x0, v0=v0, mass=m, charge=q, radii=r)
    for i in range(50):
        s.solve(0.02, 0.01, debug=False)
        xframes.append(s.x[-1])
        vframes.append(s.v[-1])
        s.x0 = s.x[-1]
        s.v0 = []
        for p in range(len(s.x[-1])):
            d = s.x0[p][0]**2 + s.x0[p][1]**2 + s.x0[p][2]**2
            v = s.v[-1][p] * min(1000/d, 2)
            if d > 1000:
                v = 4 * (v/r[p])
            s.v0.append(v)
        s.v0 = np.array(s.v0)

    return xframes[-1]


def nbody_srn_pulsar():
    import numpy as np
    import nbody

    n = 1000
    p = 3
    x0 = np.random.normal(0, 20, (n, p))
    v0 = np.random.normal(0, 50, (n, p))
    v0 = np.array([np.array([i[0], i[1], i[2]*10000]) for i in v0])
    q = np.random.normal(0, 0.0000001, (n,))
    r = np.random.normal(8, 2, (n,))
    m = np.random.normal(8, 1, (n,))

    m[m < 0] = np.abs(m[m < 0])
    m[m == 0] = 0.001

    r[r < 0] = np.abs(r[r < 0])
    r[r == 0] = 1E-3

    xframes = [x0]
    vframes = [v0]

    s = nbody.spheres(x0=x0, v0=v0, mass=m, charge=q, radii=r)
    for i in range(50):
        s.solve(0.02, 0.01, debug=False)
        xframes.append(s.x[-1])
        vframes.append(s.v[-1])
        s.x0 = s.x[-1]
        s.v0 = []
        for p in range(len(s.x[-1])):
            d = s.x0[p][0]**2 + s.x0[p][1]**2
            v = s.v[-1][p] * min(750/d, 2)
            if d > 750:
                v = 4 * (v/r[p])
            s.v0.append(v)
        s.v0 = np.array(s.v0)

    return xframes[-1]


def nbody_srn_disk():
    import numpy as np
    import nbody

    n = 1000
    p = 3
    x0 = np.random.normal(0, 20, (n, p))
    v0 = np.random.normal(0, 50, (n, p))
    q = np.random.normal(0, 0.0000001, (n,))
    r = np.random.normal(8, 2, (n,))
    m = np.random.normal(8, 1, (n,))

    m[m < 0] = np.abs(m[m < 0])
    m[m == 0] = 0.001

    r[r < 0] = np.abs(r[r < 0])
    r[r == 0] = 1E-3

    xframes = [x0]
    vframes = [v0]

    s = nbody.spheres(x0=x0, v0=v0, mass=m, charge=q, radii=r)
    for i in range(50):
        s.solve(0.02, 0.01, debug=False)
        xframes.append(s.x[-1])
        vframes.append(s.v[-1])
        s.x0 = s.x[-1]
        s.v0 = []
        for p in range(len(s.x[-1])):
            d = s.x0[p][0]**2 + s.x0[p][1]**2
            v = s.v[-1][p] * min(1000/d, 2)
            if d > 1000:
                v = 4 * (v/r[p])
            s.v0.append(v)
        s.v0 = np.array(s.v0)

    maxz = 0.1 * max([abs(i[2]) for i in xframes[-1]])
    for p in range(len(xframes[-1])):
        xframes[-1][p][2] = xframes[-1][p][2]/maxz

    return xframes[-1]


def raw_stars(seeds):
    from scipy.spatial import cKDTree, Delaunay
    import numpy as np
    polygons = []
    tree = cKDTree(seeds)
    for p in range(len(seeds)):
        q = tree.query(seeds[p], k=7)[1][1:]
        polygons.append(Delaunay([seeds[i] for i in q]))

    coords = []
    n = 300

    print(len(seeds))

    for p in range(len(seeds)):
        r = tree.query(seeds[p], k=5)[0][-1]
        theta = np.random.random(n) * 2 * np.pi
        phi = np.arccos((2 * np.random.random(n)) - 1)
        rr = pow(np.random.random(n), 1 / 3)*r
        x = (rr * np.sin(phi) * np.cos(theta)) + seeds[p][0]
        y = (rr * np.sin(phi) * np.sin(theta)) + seeds[p][1]
        z = (rr * np.cos(phi)) + seeds[p][2]

        chunk = [i for i in np.swapaxes(np.array([x, y, z]), 0, 1) if polygons[p].find_simplex(i) >= 0]
        if len(chunk) < 4:
            continue
        subtree = cKDTree(chunk)
        add = []
        noadd = []
        for q in range(len(chunk)):
            if q not in noadd:
                add.append(chunk[q])
                close_points = subtree.query_ball_point(chunk[q], r=0.01)
                noadd.extend(close_points)

        coords.extend(add)

    print(len(coords))

    return coords


def nested_polygons(seeds, av=300, var=0, level=1):
    from scipy.spatial import cKDTree, Delaunay
    import numpy as np
    import random
    pgs = []
    if len(seeds) < 7:
        return seeds
    tree = cKDTree(seeds)
    for p in range(len(seeds)):
        q = tree.query(seeds[p], k=5)[1][1:]
        pgs.append(Delaunay([seeds[i] for i in q]))

    coords = []

    print(len(seeds))

    for p in range(len(seeds)):
        n = max(4, int(random.gauss(av, var)))
        r = tree.query(seeds[p], k=5)[0][-1]*0.75
        theta = np.random.random(n) * 2 * np.pi
        phi = np.arccos((2 * np.random.random(n)) - 1)
        rr = pow(np.random.random(n), 1 / 3)*r
        x = (rr * np.sin(phi) * np.cos(theta)) + seeds[p][0]
        y = (rr * np.sin(phi) * np.sin(theta)) + seeds[p][1]
        z = (rr * np.cos(phi)) + seeds[p][2]

        chunk = [i for i in np.swapaxes(np.array([x, y, z]), 0, 1) if np.all(pgs[p].plane_distance(i) >= r/10)]

        if level > 0:
            chunk = nested_polygons(chunk, int(av/30), int(av/90), level-1)
        coords.extend(chunk)

    return coords


def main():
    """you have found my secret test function

    Returns
    -------
    nothing :
        nothing yet...

    """

    import numpy as np

    # supernova_remnant = nbody_srn3d()
    # np.save('nbody_SRN', supernova_remnant)
    # plusar = nbody_srn_pulsar()
    # np.save('nbody_SRN_pulsar', plusar)
    # disk_coords = nbody_srn_disk()
    # np.save('nbody_SRN_disk', disk_coords)

    seeds = np.load('../nbody_SRN.npy')
    # less_seeds = [seeds[i] for i in range(0, len(seeds), 6)]
    coords = raw_stars(seeds)

    np.save('../nbody_SRN_filled6.npy', coords, allow_pickle=False)

    # TODO: try out the spinning thing like lorena mentioned


if __name__ == '__main__':
    main()
