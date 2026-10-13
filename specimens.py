"""Procedural mineral/organic specimens for the pigment AR sampler."""
import numpy as np, trimesh, os

OUT = "/mnt/user-data/outputs/prime-form/models"
os.makedirs(OUT, exist_ok=True)


def fbm(p, octaves=4, lac=2.1, gain=0.5, seed=0):
    total = np.zeros(len(p)); amp, freq = 1.0, 1.0
    r = np.random.default_rng(seed)
    for _ in range(octaves):
        dirs = r.normal(size=(6, 3)); dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
        phase = r.uniform(0, 2 * np.pi, 6)
        layer = np.zeros(len(p))
        for d, ph in zip(dirs, phase):
            layer += np.sin(p @ d * freq * 3.0 + ph)
        total += amp * layer / 6.0
        amp *= gain; freq *= lac
    return total


def rough_chunk(seed, subdiv=4, rough=.30, squash=(1,.78,.92), facet=0.0):
    m = trimesh.creation.icosphere(subdivisions=subdiv, radius=1.0)
    v = m.vertices.copy()
    n = v / np.linalg.norm(v, axis=1, keepdims=True)
    disp = 1.0 + rough * fbm(v * 1.6, 4, seed=seed)
    if facet > 0:
        disp = np.round(disp / facet) * facet
    m.vertices = n * disp[:, None] * np.array(squash)
    return m


def botryoidal(seed, n_blobs=16):
    r = np.random.default_rng(seed)
    parts = [rough_chunk(seed + 5, 3, .18, (1, .62, .88))]
    for _ in range(n_blobs):
        rad = r.uniform(.22, .58)
        d = r.normal(size=3); d /= np.linalg.norm(d); d[1] = abs(d[1]) * .9 + .05
        pos = d * r.uniform(.55, 1.05)
        s = trimesh.creation.icosphere(subdivisions=3, radius=rad)
        s.apply_scale([1, r.uniform(.75, 1), r.uniform(.85, 1.15)])
        s.apply_translation(pos); parts.append(s)
        if r.random() < .55:
            s2 = trimesh.creation.icosphere(subdivisions=2, radius=rad * r.uniform(.4, .6))
            d2 = r.normal(size=3); d2 /= np.linalg.norm(d2); d2[1] = abs(d2[1])
            s2.apply_translation(pos + d2 * rad * .85); parts.append(s2)
    m = trimesh.util.concatenate(parts); m.apply_scale([1, .70, 1]); return m


def crystal_cluster(seed, n=7, sides=6, lo=.9, hi=2.0, rlo=.13, rhi=.26):
    r = np.random.default_rng(seed)
    parts = [rough_chunk(seed + 99, 3, .22, (1, .42, 1))]
    for _ in range(n):
        h = r.uniform(lo, hi); rad = r.uniform(rlo, rhi)
        prism = trimesh.creation.cylinder(radius=rad, height=h, sections=sides)
        tip = trimesh.creation.cone(radius=rad, height=rad * 1.9, sections=sides)
        tip.apply_translation([0, 0, h / 2])
        c = trimesh.util.concatenate([prism, tip]); c.apply_translation([0, 0, h / 2])
        c.apply_transform(trimesh.transformations.rotation_matrix(r.uniform(0, .85), [1, 0, 0]))
        c.apply_transform(trimesh.transformations.rotation_matrix(r.uniform(0, 2 * np.pi), [0, 0, 1]))
        c.apply_transform(trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0]))
        c.apply_translation([r.uniform(-.35, .35), 0, r.uniform(-.35, .35)])
        parts.append(c)
    return trimesh.util.concatenate(parts)


def murex_shell(seed=1, turns=3.4, seg=190, ring=22, spines=True):
    """A spiral gastropod shell — the Tyrian purple source."""
    r = np.random.default_rng(seed)
    t = np.linspace(0, turns * 2 * np.pi, seg)
    growth = np.exp(0.26 * t)
    cx = growth * np.cos(t); cy = growth * np.sin(t); cz = 0.30 * growth
    centre = np.stack([cx, cy, cz], 1)
    centre /= growth.max()
    tube = 0.26 * growth / growth.max()

    tan = np.gradient(centre, axis=0)
    tan /= np.linalg.norm(tan, axis=1, keepdims=True)
    up = np.array([0, 0, 1.0])
    nrm = np.cross(tan, up); nrm /= np.linalg.norm(nrm, axis=1, keepdims=True)
    bin_ = np.cross(tan, nrm)

    th = np.linspace(0, 2 * np.pi, ring, endpoint=False)
    verts = []
    for i in range(seg):
        rr = tube[i] * (1 + .17 * np.sin(th * 7 + i * .22))   # ribbed
        pts = centre[i][None, :] + (np.cos(th) * rr)[:, None] * nrm[i][None, :] \
                                 + (np.sin(th) * rr)[:, None] * bin_[i][None, :]
        verts.append(pts)
    verts = np.concatenate(verts)

    faces = []
    for i in range(seg - 1):
        for j in range(ring):
            a = i * ring + j
            b = i * ring + (j + 1) % ring
            c = (i + 1) * ring + (j + 1) % ring
            d = (i + 1) * ring + j
            faces += [[a, b, c], [a, c, d]]
    m = trimesh.Trimesh(vertices=verts, faces=np.array(faces), process=False)

    if spines:
        parts = [m]
        for i in range(26, seg - 4, 11):
            rad = tube[i] * .40
            sp = trimesh.creation.cone(radius=rad, height=rad * 3.4, sections=5)
            d = nrm[i] * .55 + bin_[i] * .55 + np.array([0, 0, .25])
            d /= np.linalg.norm(d)
            T = trimesh.geometry.align_vectors([0, 0, 1], d)
            sp.apply_transform(T)
            sp.apply_translation(centre[i] + d * tube[i] * .85)
            parts.append(sp)
        m = trimesh.util.concatenate(parts)
    return m


def root_bundle(seed=1, n=9):
    """Gnarled root cluster — madder."""
    r = np.random.default_rng(seed)
    parts = []
    for _ in range(n):
        seg = 9
        pts = [np.array([r.uniform(-.2, .2), 0, r.uniform(-.2, .2)])]
        d = np.array([r.uniform(-1, 1), r.uniform(.25, 1), r.uniform(-1, 1)])
        d /= np.linalg.norm(d)
        for _ in range(seg):
            d = d + r.normal(scale=.42, size=3); d /= np.linalg.norm(d)
            pts.append(pts[-1] + d * r.uniform(.17, .30))
        pts = np.array(pts)
        rad = np.linspace(r.uniform(.07, .12), r.uniform(.02, .04), len(pts))
        for i in range(len(pts) - 1):
            v = pts[i + 1] - pts[i]; h = np.linalg.norm(v)
            cyl = trimesh.creation.cylinder(radius=(rad[i] + rad[i + 1]) / 2,
                                            height=h, sections=7)
            T = trimesh.geometry.align_vectors([0, 0, 1], v / h)
            cyl.apply_transform(T); cyl.apply_translation((pts[i] + pts[i + 1]) / 2)
            parts.append(cyl)
            parts.append(trimesh.creation.icosphere(subdivisions=1, radius=rad[i] * 1.05)
                         .apply_translation(pts[i]) or parts[-1])
    m = trimesh.util.concatenate([p for p in parts if isinstance(p, trimesh.Trimesh)])
    return m


def colourise(m, base_hex, variation=.10, fleck=None, fleck_hex="#C9A227",
              fleck_amount=.05, seed=0):
    base = np.array([int(base_hex[i:i + 2], 16) for i in (1, 3, 5)], float)
    v = m.vertices
    d = fbm(v * 3.4, 3, seed=seed + 11)
    d = (d - d.min()) / (np.ptp(d) + 1e-9)
    cols = np.clip(base[None, :] * (1 + (d - .5) * 2 * variation)[:, None], 0, 255)
    if fleck is not None:
        fc = np.array([int(fleck_hex[i:i + 2], 16) for i in (1, 3, 5)], float)
        f = fbm(v * fleck, 2, seed=seed + 57)
        f = (f - f.min()) / (np.ptp(f) + 1e-9)
        cols[f > (1 - fleck_amount)] = fc
    rgba = np.hstack([cols, np.full((len(cols), 1), 255.)]).astype(np.uint8)
    m.visual = trimesh.visual.ColorVisuals(mesh=m, vertex_colors=rgba)
    return m


def finish(m, name, size=.11):
    m.apply_translation(-m.bounds.mean(axis=0))
    m.apply_scale(size / max(m.extents))
    m.apply_translation([0, -m.bounds[0][1], 0])
    trimesh.Scene(m).export(os.path.join(OUT, name + ".glb"))
    print(f"{name:18s} {len(m.vertices):6d} v  {os.path.getsize(os.path.join(OUT,name+'.glb'))/1024:7.1f} KB")


# ---------------------------------------------------------------- specimens
SPECS = []

m = rough_chunk(3, 4, .26, (1, .80, .92))
colourise(m, "#2B4C9B", .16, fleck=7.0, fleck_hex="#C9A227", fleck_amount=.14, seed=3)
finish(m, "lapis-lazuli", .105)

m = rough_chunk(81, 4, .20, (1, .85, .95))
colourise(m, "#2A6FA8", .13, fleck=9.0, fleck_hex="#7FC4E8", fleck_amount=.10, seed=81)
finish(m, "egyptian-blue", .09)

m = botryoidal(12, 17)
colourise(m, "#3C8A62", .22, seed=12)
finish(m, "malachite", .115)

m = crystal_cluster(21, 8)
colourise(m, "#C8342A", .14, seed=21)
finish(m, "cinnabar", .095)

m = crystal_cluster(44, 9, sides=4)
colourise(m, "#E0B93C", .17, seed=44)
finish(m, "orpiment", .10)

m = rough_chunk(66, 4, .34, (1, .70, .88), facet=.085)
colourise(m, "#A8432A", .20, seed=66)
finish(m, "red-ochre", .12)

m = rough_chunk(101, 4, .42, (1, .74, .86), facet=.11)
colourise(m, "#1A1715", .34, seed=101)
finish(m, "charcoal", .13)

m = crystal_cluster(131, 10, sides=4, lo=.7, hi=1.5, rlo=.08, rhi=.17)
colourise(m, "#E8E4DA", .09, seed=131)
finish(m, "cerussite", .095)

m = murex_shell(5)
colourise(m, "#B8A890", .16, fleck=6.0, fleck_hex="#6B2144", fleck_amount=.22, seed=5)
finish(m, "murex-shell", .13)

m = root_bundle(9, 10)
colourise(m, "#9C4A3C", .24, seed=9)
finish(m, "madder-root", .145)

m = rough_chunk(177, 4, .30, (1, .68, .90), facet=.07)
colourise(m, "#6B4226", .22, seed=177)
finish(m, "umber-earth", .125)

m = botryoidal(203, 13)
colourise(m, "#3A6E99", .18, seed=203)
finish(m, "azurite", .10)
