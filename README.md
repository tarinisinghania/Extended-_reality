# Prime Form

Point a phone camera at anything. The colour is read off the surface, matched to the
historical pigment it most resembles, and **the raw material that pigment was ground from
appears on your floor** at real specimen scale.

A blue mug becomes a lump of Afghan lapis. A terracotta pot becomes the ochre that has
been dug for a hundred thousand years. A black jacket becomes charcoal.

Submission artefacts: a live website link and a GitHub repo.

## Publishing

```bash
cd prime-form
git init && git add . && git commit -m "Prime Form"
gh repo create prime-form --public --source=. --push
```

Then **Settings → Pages → Deploy from a branch → main → / (root)**. The site is at
`https://<username>.github.io/prime-form/`. GitHub Pages serves `.glb` and `.usdz`
correctly with no configuration.

## Testing locally

```bash
python3 -m http.server 8000
```

`http://localhost:8000` — localhost counts as a secure context, so the camera works on a
laptop. The AR button won't appear there, because a desktop browser has no AR session to
enter; the page says so instead.

For AR before publishing: Android over USB via `chrome://inspect` → Port forwarding →
`8000`. For iOS, `cloudflared tunnel --url http://localhost:8000`.

## How it works

**Sampling.** A 60px disc at the screen centre is read from the video frame, converted to
linear light, the brightest and darkest 10% by luma trimmed off to resist specular
highlights and shadow, and the remainder averaged.

**Matching.** The sample goes to CIELAB and is compared against all twelve pigments with
CIEDE2000. The interface always prints the ΔE and labels it honestly:

| ΔE | shown as |
|----|----------|
| under 10 | close match |
| 10–22 | loose match |
| over 22 | nearest in the set, not a match |

Measured against ordinary surfaces: denim → lapis lazuli at 6.0, brick → red ochre at
3.2, white paper → cerussite at 1.7, aubergine → murex shell at 9.7, mustard → orpiment
at 5.8. Pale sky blue returns cerussite at 24.4 and is correctly flagged as not a match —
the set has no pale blue, and the app says so rather than inventing confidence.

**AR.** `<model-viewer>` with `ar-scale="fixed"`, so specimens appear at true size
(9–14 cm) and cannot be pinch-resized. The scale is information, not a viewing
convenience. WebXR on Android, Quick Look on iOS.

## The twelve

| Specimen | Pigment | Covers |
|---|---|---|
| Lapis lazuli | Ultramarine | deep blue |
| Egyptian blue frit | Egyptian blue | mid blue |
| Azurite | Azurite | grey-blue |
| Malachite | Malachite green | green |
| Cinnabar | Vermilion | scarlet |
| Madder root | Madder lake | crimson |
| Orpiment | King's yellow | yellow |
| Ochre earth | Red ochre | earth red |
| Umber earth | Burnt umber | brown |
| Murex shell | Tyrian purple | purple |
| Charcoal | Carbon black | black |
| Cerussite | Lead white | white |

## About the models

Procedural stand-ins generated with trimesh — displaced icospheres for massive specimens,
swept prism clusters for crystalline ones, a logarithmic-spiral tube with ribbing and
spines for the murex shell, branching swept cylinders for the madder root. Per-vertex
colour noise throughout, with pyrite flecks in the lapis. `specimens.py` and `make_usdz.py`
are included so you can regenerate or alter them.

They are not scans. If you want photoreal minerals, Sketchfab has CC-licensed scans that
export as GLB — filter by Downloadable + CC Attribution and credit the author. Drop the
file into `models/`, keep the `id`, and convert to USDZ with Apple's free Reality
Converter or with `make_usdz.py`.

## Known limitations

- **White balance is the camera's.** The same wall reads differently under tungsten and
  daylight. A grey-card calibration step would fix this and is the most worthwhile
  addition.
- **Twelve pigments is a coarse net.** Pale and desaturated colours have no good match.
  The ΔE label is the mitigation.
- Matching is against a single mass-tone per pigment, which is a real simplification: a
  pigment's appearance depends on grind size, binder and what is underneath it.
- Quick Look ignores `auto-rotate` and some lighting attributes.
- WebXR AR on Android requires Google Play Services for AR.

## Content accuracy

Histories are drawn from standard pigment scholarship. Verify anything you intend to say
aloud — the Almadén labour conditions, Cennini's orpiment warning, and the Blombos Cave
ochre workshop are all well documented, but phrasing and dates vary between sources.
Starting points: the Forbes Pigment Collection at Harvard, the National Gallery technical
bulletins, Philip Ball's *Bright Earth*, Victoria Finlay's *Colour*.
