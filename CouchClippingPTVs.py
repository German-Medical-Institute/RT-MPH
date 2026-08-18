"""
Script name: CouchClipping.py
Author: Alexandros Puckett Anastasiou, Junior Medical Physicist

Description:
Clips couch structures +3 cm SI and ±30 cm XY around ALL PTV/CTV/GTV contours.

Disclaimer:
Provided as a tool, not clinically validated. User must verify results.
"""

from connect import get_current

# -----------------------------
# Inputs
# -----------------------------
cube_name = "PTV_3mm_Cube"
clip_suffix = "_Clip"
margin_mm = 3

# -----------------------------
# Couch detection rules
# -----------------------------
couch_prefixes = ["Uni_iBeam_CF", "Uni_iBeam_Foam", "BB_CF", "BB_Foam"]

# -----------------------------
# Material mapping
# -----------------------------
couch_material_map = {
    "Uni_iBeam_CF": "CF0.6",
    "Uni_iBeam_Foam": "PMI Foam",
    "BB_CF": "CF0.6",
    "BB_Foam": "PMI Foam",
}

# -----------------------------
# Color mapping
# -----------------------------
couch_color_map = {
    "BB_CF": "LightBlue",
    "BB_Foam": "Pink",
    "Uni_iBeam_CF": "Blue",
    "Uni_iBeam_Foam": "Red",
}

# -----------------------------
# Get objects
# -----------------------------
case = get_current("Case")
exam = get_current("Examination")
pm = case.PatientModel
ss = pm.StructureSets[exam.Name]

roi_names = [r.Name for r in pm.RegionsOfInterest]

# =========================================================
# DELETE OLD CLIPS
# =========================================================
for roi in list(roi_names):
    if roi.endswith(clip_suffix):
        try:
            pm.RegionsOfInterest[roi].DeleteRoi()
        except Exception:
            pass

roi_names = [r.Name for r in pm.RegionsOfInterest]

# =========================================================
# FIND TARGET GEOMETRIES
# =========================================================
target_geoms = []

for g in ss.RoiGeometries:
    try:
        if g.HasContours() and any(k in g.OfRoi.Name for k in ["PTV", "CTV", "GTV"]):
            target_geoms.append(g)
    except Exception:
        continue

if not target_geoms:
    raise Exception("No PTV/CTV/GTV contours found")

print(f"Found {len(target_geoms)} target structure(s)")

# =========================================================
# BUILD CUBE BOUNDING BOX
# =========================================================
x_min = y_min = z_min = float("inf")
x_max = y_max = z_max = float("-inf")

for g in target_geoms:

    bbox = g.GetBoundingBox()

    x_min = min(x_min, bbox[0].x)
    y_min = min(y_min, bbox[0].y)
    z_min = min(z_min, bbox[0].z)

    x_max = max(x_max, bbox[1].x)
    y_max = max(y_max, bbox[1].y)
    z_max = max(z_max, bbox[1].z)

# Apply margins
x_min -= margin_mm + 30
x_max += margin_mm + 30
y_min -= margin_mm + 30
y_max += margin_mm + 30
z_min -= margin_mm
z_max += margin_mm

# =========================================================
# CREATE CUBE
# =========================================================
if cube_name in roi_names:
    try:
        pm.RegionsOfInterest[cube_name].DeleteRoi()
    except Exception:
        pass

pm.CreateRoi(Name=cube_name, Color="Yellow", Type="Control")
cube_roi = pm.RegionsOfInterest[cube_name]

cube_roi.CreateBoxGeometry(
    Size={"x": x_max - x_min, "y": y_max - y_min, "z": z_max - z_min},
    Center={
        "x": (x_min + x_max) / 2,
        "y": (y_min + y_max) / 2,
        "z": (z_min + z_max) / 2,
    },
    Examination=exam,
)

print("Cube created")

# =========================================================
# SNAPSHOT GEOMETRIES
# =========================================================
input_geoms = [g for g in ss.RoiGeometries if g.HasContours()]

processed_couch_rois = []

# =========================================================
# CLIP COUCH STRUCTURES
# =========================================================
for geom in input_geoms:

    roi = geom.OfRoi
    roi_name = roi.Name

    if not any(roi_name.startswith(p) for p in couch_prefixes):
        continue

    if roi_name.endswith(clip_suffix) or roi_name == cube_name:
        continue

    new_name = roi_name + clip_suffix

    print(f"Processing: {roi_name}")

    if new_name in [r.Name for r in pm.RegionsOfInterest]:
        try:
            pm.RegionsOfInterest[new_name].DeleteRoi()
        except Exception:
            pass

    # Create ROI
    pm.CreateRoi(Name=new_name, Color=roi.Color, Type=roi.Type)
    dst_roi = pm.RegionsOfInterest[new_name]

    # Copy material
    try:
        if roi.RoiMaterial is not None:
            dst_roi.SetRoiMaterial(Material=roi.RoiMaterial.OfMaterial)
    except Exception:
        pass

    # Copy color
    try:
        dst_roi.Color = roi.Color
    except Exception:
        pass

    # =====================================================
    # FIXED ALGEBRA GEOMETRY (CRITICAL FIX)
    # =====================================================
    dst_roi.CreateAlgebraGeometry(
        Examination=exam,
        Algorithm="Auto",
        ExpressionA={
            "Operation": "Union",
            "SourceRoiNames": [roi_name],
            "MarginSettings": {
                "Type": "Expand",
                "Superior": 0,
                "Inferior": 0,
                "Anterior": 0,
                "Posterior": 0,
                "Right": 0,
                "Left": 0,
            },
        },
        ExpressionB={
            "Operation": "Union",
            "SourceRoiNames": [cube_name],
            "MarginSettings": {
                "Type": "Expand",
                "Superior": 0,
                "Inferior": 0,
                "Anterior": 0,
                "Posterior": 0,
                "Right": 0,
                "Left": 0,
            },
        },
        ResultOperation="Intersection",
        ResultMarginSettings={
            "Type": "Expand",
            "Superior": 0,
            "Inferior": 0,
            "Anterior": 0,
            "Posterior": 0,
            "Right": 0,
            "Left": 0,
        },
    )

    processed_couch_rois.append(roi_name)

# =========================================================
# DELETE ORIGINALS + RENAME CLIPS
# =========================================================
successfully_replaced = []
failed_replacement = []

for roi_name in processed_couch_rois:

    clip_name = roi_name + clip_suffix

    print("\n--------------------------------")
    print(f"Replacing: {roi_name}")
    print("--------------------------------")

    try:
        pm.RegionsOfInterest[roi_name].DeleteRoi()
        print(f"Deleted original ROI: {roi_name}")
    except Exception as e:
        msg = f"DELETE FAILED for {roi_name}: " f"{type(e).__name__}: {e}"
        print(msg)
        failed_replacement.append(msg)
        continue

    try:
        pm.RegionsOfInterest[clip_name].Name = roi_name
        print(f"Renamed clipped ROI " f"{clip_name} -> {roi_name}")
        successfully_replaced.append(roi_name)

    except Exception as e:
        msg = f"RENAME FAILED for {clip_name}: " f"{type(e).__name__}: {e}"
        print(msg)
        failed_replacement.append(msg)

# =========================================================
# SUMMARY
# =========================================================
print("\n================================")
print("COUCH CLIPPING SUMMARY")
print("================================")

print(f"Successfully replaced: " f"{len(successfully_replaced)}")

for roi_name in successfully_replaced:
    print(f"  OK  - {roi_name}")

print(f"\nFailed replacements: " f"{len(failed_replacement)}")

for msg in failed_replacement:
    print(f"  FAIL - {msg}")

print("\n✅ Couch clipping completed")
