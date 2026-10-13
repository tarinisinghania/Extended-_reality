"""Convert each specimen GLB to USDZ so iOS Quick Look can open it."""
import os, numpy as np, trimesh
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, Vt, UsdUtils

SRC = "/mnt/user-data/outputs/prime-form/models"
names = [f[:-4] for f in sorted(os.listdir(SRC)) if f.endswith(".glb")]

for n in names:
    scene = trimesh.load(os.path.join(SRC, n + ".glb"))
    m = list(scene.geometry.values())[0]
    verts = np.asarray(m.vertices, dtype=np.float32)
    faces = np.asarray(m.faces, dtype=np.int32)
    cols = np.asarray(m.visual.vertex_colors)[:, :3].astype(np.float32) / 255.0

    usda = os.path.join(SRC, n + ".usda")
    stage = Usd.Stage.CreateNew(usda)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)

    root = UsdGeom.Xform.Define(stage, "/Specimen")
    stage.SetDefaultPrim(root.GetPrim())

    mesh = UsdGeom.Mesh.Define(stage, "/Specimen/Mesh")
    mesh.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(verts))
    mesh.CreateFaceVertexIndicesAttr(Vt.IntArray.FromNumpy(faces.ravel()))
    mesh.CreateFaceVertexCountsAttr(
        Vt.IntArray.FromNumpy(np.full(len(faces), 3, dtype=np.int32)))
    mesh.CreateSubdivisionSchemeAttr(UsdGeom.Tokens.none)
    mesh.CreateExtentAttr(Vt.Vec3fArray.FromNumpy(
        np.array(m.bounds, dtype=np.float32)))

    # per-vertex colour as the displayColor primvar
    pv = UsdGeom.PrimvarsAPI(mesh).CreatePrimvar(
        "displayColor", Sdf.ValueTypeNames.Color3fArray,
        UsdGeom.Tokens.vertex)
    pv.Set(Vt.Vec3fArray.FromNumpy(cols))

    # a UsdPreviewSurface that reads displayColor, so Quick Look shades it
    mat = UsdShade.Material.Define(stage, "/Specimen/Mat")
    shader = UsdShade.Shader.Define(stage, "/Specimen/Mat/Surface")
    shader.CreateIdAttr("UsdPreviewSurface")
    shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.55)
    shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)

    reader = UsdShade.Shader.Define(stage, "/Specimen/Mat/CVReader")
    reader.CreateIdAttr("UsdPrimvarReader_float3")
    reader.CreateInput("varname", Sdf.ValueTypeNames.String).Set("displayColor")
    reader.CreateOutput("result", Sdf.ValueTypeNames.Float3)
    shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).ConnectToSource(
        reader.ConnectableAPI(), "result")

    mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
    UsdShade.MaterialBindingAPI(mesh).Apply(mesh.GetPrim())
    UsdShade.MaterialBindingAPI(mesh).Bind(mat)

    stage.GetRootLayer().Save()

    usdz = os.path.join(SRC, n + ".usdz")
    if os.path.exists(usdz):
        os.remove(usdz)
    UsdUtils.CreateNewUsdzPackage(Sdf.AssetPath(usda), usdz)
    os.remove(usda)
    print(f"{n:16s} {os.path.getsize(usdz)/1024:7.1f} KB")
