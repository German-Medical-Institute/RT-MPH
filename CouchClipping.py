"""
Script name: CouchClipping.py
Author: Alexandros Puckett Anastasiou, Junior Medical Physicist

Description:
This script is intended to clip the couches +3 cm sup/inf from the PTVs contour.

Disclaimer:
This script is provided as a tool and is not an officially endorsed or clinically validated script for use within RayStation.
It is supplied without any guarantees regarding accuracy, performance, or expected outcomes.
Users must independently verify all results prior to clinical application.

In accordance with the RaySearch Laboratories RayStation Instructions for Use,
all scripts must be thoroughly reviewed and validated by the end user before any clinical use.
Any use of this script, in whole or in part, is performed at the user’s own risk.
"""

from connect import *

# -----------------------------
# Inputs
# -----------------------------
cube_name = "PTV_3mm_Cube"
clip_suffix = "_Clip"
margin_mm = 3

# -----------------------------
# Couch detection rules
# -----------------------------
couch_prefixes = [
    "Uni_iBeam_CF",
    "Uni_iBeam_Foam",
    "BB_CF",
    "BB_Foam"
]

# -----------------------------
# Material mapping
# -----------------------------
couch_material_map = {
    "Uni_iBeam_CF": "CF0.6",
    "Uni_iBeam_Foam": "PMI Foam",
    "BB_CF": "CF0.6",
    "BB_Foam": "PMI Foam"
}

# -----------------------------
# Color mapping
# -----------------------------
couch_color_map = {
    "BB_CF": "LightBlue",
    "BB_Foam": "Pink",
    "Uni_iBeam_CF": "Blue",
    "Uni_iBeam_Foam": "Red"
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
        except:
            pass

roi_names = [r.Name for r in pm.RegionsOfInterest]

# =========================================================
# FIND TARGET ROI
# =========================================================
target_roi_name = None

for keyword in ["PTV", "CTV", "GTV"]:
    for roi in roi_names:
        if keyword in roi:
            target_roi_name = roi
            break
    if target_roi_name:
        break

if not target_roi_name:
    raise Exception("No target ROI found (PTV/CTV/GTV)")

print(f"Using target ROI: {target_roi_name}")

target_geom = ss.RoiGeometries[target_roi_name]

if not target_geom.HasContours():
    raise Exception(f"{target_roi_name} has no contours")

# =========================================================
# BUILD CUBE
# =========================================================
bbox = target_geom.GetBoundingBox()

x_min, x_max = bbox[0].x, bbox[1].x
y_min, y_max = bbox[0].y, bbox[1].y
z_min, z_max = bbox[0].z, bbox[1].z

x_min -= margin_mm + 30
x_max += margin_mm + 30
y_min -= margin_mm + 30
y_max += margin_mm + 30
z_min -= margin_mm
z_max += margin_mm

if cube_name in roi_names:
    try:
        pm.RegionsOfInterest[cube_name].DeleteRoi()
    except:
        pass

pm.CreateRoi(Name=cube_name, Color="Yellow", Type="Control")
cube_roi = pm.RegionsOfInterest[cube_name]

cube_roi.CreateBoxGeometry(
    Size={
        'x': x_max - x_min,
        'y': y_max - y_min,
        'z': z_max - z_min
    },
    Center={
        'x': (x_min + x_max) / 2,
        'y': (y_min + y_max) / 2,
        'z': (z_min + z_max) / 2
    },
    Examination=exam
)

print("Cube created")

# =========================================================
# SNAPSHOT GEOMETRIES
# =========================================================
input_geoms = [g for g in ss.RoiGeometries if g.HasContours()]

# Track processed couch ROIs
processed_couch_rois = []

# =========================================================
# CLIP COUCH STRUCTURES
# =========================================================
for geom in input_geoms:

    roi = geom.OfRoi
    roi_name = roi.Name

    # Skip non-couch
    if not any(roi_name.startswith(prefix) for prefix in couch_prefixes):
        continue

    # Skip generated
    if roi_name.endswith(clip_suffix) or roi_name == cube_name:
        continue

    new_name = roi_name + clip_suffix

    print(f"Processing: {roi_name}")

    if new_name in [r.Name for r in pm.RegionsOfInterest]:
        try:
            pm.RegionsOfInterest[new_name].DeleteRoi()
        except:
            pass

    # -----------------------------
    # COLOR ASSIGNMENT
    # -----------------------------
    roi_color = "Cyan"  # fallback
    for prefix, color in couch_color_map.items():
        if roi_name.startswith(prefix):
            roi_color = color
            break

    pm.CreateRoi(Name=new_name, Color=roi_color, Type=roi.Type)
    dst_roi = pm.RegionsOfInterest[new_name]

    # -----------------------------
    # MATERIAL ASSIGNMENT
    # -----------------------------
    material_assigned = False

    for prefix, mat_name in couch_material_map.items():
        if roi_name.startswith(prefix):
            try:
                dst_roi.SetRoiMaterial(Material=pm.Materials[mat_name])
                material_assigned = True
                print(f"{roi_name} → material {mat_name}")
            except:
                print(f"WARNING: Material '{mat_name}' not found")
            break

    if not material_assigned:
        try:
            if roi.RoiMaterial is not None:
                dst_roi.SetRoiMaterial(Material=roi.RoiMaterial.OfMaterial)
        except:
            pass

    # -----------------------------
    # CLIP GEOMETRY
    # -----------------------------
    dst_roi.CreateAlgebraGeometry(
        Examination=exam,
        Algorithm="Auto",
        ExpressionA={
            'Operation': "Union",
            'SourceRoiNames': [roi_name],
            'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0,
                               'Anterior': 0, 'Posterior': 0,
                               'Right': 0, 'Left': 0}
        },
        ExpressionB={
            'Operation': "Union",
            'SourceRoiNames': [cube_name],
            'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0,
                               'Anterior': 0, 'Posterior': 0,
                               'Right': 0, 'Left': 0}
        },
        ResultOperation="Intersection",
        ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0,
                              'Anterior': 0, 'Posterior': 0,
                              'Right': 0, 'Left': 0}
    )

    processed_couch_rois.append(roi_name)

# =========================================================
# DELETE ORIGINAL COUCH ROIS
# =========================================================
for roi_name in processed_couch_rois:

    clip_name = roi_name + clip_suffix

    try:
        pm.RegionsOfInterest[roi_name].DeleteRoi()
        print(f"Deleted original: {roi_name}")
    except:
        print(f"Could not delete: {roi_name} (likely in use)")
        continue

    # =====================================================
    # RENAME CLIPPED BACK
    # =====================================================
    try:
        pm.RegionsOfInterest[clip_name].Name = roi_name
        print(f"Renamed {clip_name} → {roi_name}")
    except:
        print(f"Could not rename {clip_name}")

print("✅ Couch clipping + replacement completed")