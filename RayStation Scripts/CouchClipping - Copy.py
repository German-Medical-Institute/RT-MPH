"""
Script name: CouchClipping_Updated.py
Author: Alexandros Puckett Anastasiou, Junior Medical Physicist

Description:
This script clips couch structures around all PTVs using a
bounding box expanded:
    - ±3 cm in Superior/Inferior (Z)
    - ±30 cm in X/Y

The clipped couch ROIs preserve:
    - ROI material
    - Density override
    - ROI color
    - ROI type

The original couch ROIs are deleted and replaced by the clipped versions.

Disclaimer:
This script is provided as a tool and is not an officially endorsed
or clinically validated script for use within RayStation.

Users must independently verify all results prior to clinical application.
"""

from connect import *

# =========================================================
# INPUTS
# =========================================================
cube_name = "PTV_3mm_Cube"
clip_suffix = "_Clip"

# Margins (cm)
si_margin_cm = 3      # Superior / Inferior
xy_margin_cm = 30     # Left/Right/Anterior/Posterior

# =========================================================
# COUCH DETECTION RULES
# =========================================================
couch_prefixes = [
    "Uni_iBeam_CF",
    "Uni_iBeam_Foam",
    "BB_CF",
    "BB_Foam"
]

# =========================================================
# GET CURRENT OBJECTS
# =========================================================
case = get_current("Case")
exam = get_current("Examination")

pm = case.PatientModel
ss = pm.StructureSets[exam.Name]

roi_names = [r.Name for r in pm.RegionsOfInterest]

# =========================================================
# DELETE OLD CLIPPED ROIS
# =========================================================
for roi_name in list(roi_names):

    if roi_name.endswith(clip_suffix):

        try:
            pm.RegionsOfInterest[roi_name].DeleteRoi()
            print(f"Deleted old clip: {roi_name}")

        except:
            pass

roi_names = [r.Name for r in pm.RegionsOfInterest]

# =========================================================
# FIND ALL PTVS
# =========================================================
ptv_geoms = []

for geom in ss.RoiGeometries:

    try:
        roi_name = geom.OfRoi.Name

        if "PTV" in roi_name and geom.HasContours():
            ptv_geoms.append(geom)

    except:
        continue

if not ptv_geoms:
    raise Exception("No PTVs found")

print(f"Found {len(ptv_geoms)} PTV(s)")

# =========================================================
# BUILD COMBINED BOUNDING BOX
# =========================================================
x_min = float("inf")
y_min = float("inf")
z_min = float("inf")

x_max = float("-inf")
y_max = float("-inf")
z_max = float("-inf")

for geom in ptv_geoms:

    bbox = geom.GetBoundingBox()

    x_min = min(x_min, bbox[0].x)
    y_min = min(y_min, bbox[0].y)
    z_min = min(z_min, bbox[0].z)

    x_max = max(x_max, bbox[1].x)
    y_max = max(y_max, bbox[1].y)
    z_max = max(z_max, bbox[1].z)

# =========================================================
# APPLY MARGINS
# =========================================================

# X/Y ±30 cm
x_min -= xy_margin_cm
x_max += xy_margin_cm

y_min -= xy_margin_cm
y_max += xy_margin_cm

# Z ±3 cm
z_min -= si_margin_cm
z_max += si_margin_cm

# =========================================================
# DELETE EXISTING CUBE
# =========================================================
if cube_name in roi_names:

    try:
        pm.RegionsOfInterest[cube_name].DeleteRoi()
        print(f"Deleted existing cube: {cube_name}")

    except:
        pass

# =========================================================
# CREATE CUBE ROI
# =========================================================
pm.CreateRoi(
    Name=cube_name,
    Color="Yellow",
    Type="Control"
)

cube_roi = pm.RegionsOfInterest[cube_name]

# Limit dimensions to avoid RayStation failures
size_x = min(x_max - x_min, 200)
size_y = min(y_max - y_min, 200)
size_z = min(z_max - z_min, 200)

cube_roi.CreateBoxGeometry(
    Size={
        'x': size_x,
        'y': size_y,
        'z': size_z
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
# SNAPSHOT COUCH ROIS
# =========================================================
couch_rois = []

for roi in list(pm.RegionsOfInterest):

    if roi.Name == cube_name:
        continue

    if roi.Name.endswith(clip_suffix):
        continue

    if any(roi.Name.startswith(prefix) for prefix in couch_prefixes):
        couch_rois.append(roi)

if not couch_rois:
    raise Exception("No couch ROIs found")

print(f"Found {len(couch_rois)} couch ROI(s)")

# =========================================================
# PROCESS COUCHS
# =========================================================
for roi in couch_rois:

    original_name = roi.Name
    clip_name = original_name + clip_suffix

    print(f"\nProcessing: {original_name}")

    # -----------------------------------------------------
    # Delete existing clip if present
    # -----------------------------------------------------
    if clip_name in [r.Name for r in pm.RegionsOfInterest]:

        try:
            pm.RegionsOfInterest[clip_name].DeleteRoi()
            print(f"Deleted old clip ROI: {clip_name}")

        except:
            pass

    # -----------------------------------------------------
    # Create replacement ROI
    # -----------------------------------------------------
    pm.CreateRoi(
        Name=clip_name,
        Color=roi.Color,
        Type=roi.Type
    )

    dst_roi = pm.RegionsOfInterest[clip_name]

    # -----------------------------------------------------
    # Copy ROI material / density override
    # -----------------------------------------------------
    try:

        if roi.RoiMaterial is not None:

            dst_roi.SetRoiMaterial(
                Material=roi.RoiMaterial.OfMaterial
            )

            print("Copied ROI material")

    except Exception as e:

        print(f"Could not copy material: {e}")

    # -----------------------------------------------------
    # Copy color
    # -----------------------------------------------------
    try:
        dst_roi.Color = roi.Color

    except:
        pass

    # -----------------------------------------------------
    # Create clipped geometry
    # -----------------------------------------------------
    try:

        dst_roi.CreateAlgebraGeometry(

            Examination=exam,
            Algorithm="Auto",

            ExpressionA={
                'Operation': "Union",

                'SourceRoiNames': [original_name],

                'MarginSettings': {
                    'Type': "Expand",

                    'Superior': 0,
                    'Inferior': 0,

                    'Anterior': 0,
                    'Posterior': 0,

                    'Right': 0,
                    'Left': 0
                }
            },

            ExpressionB={
                'Operation': "Union",

                'SourceRoiNames': [cube_name],

                'MarginSettings': {
                    'Type': "Expand",

                    'Superior': 0,
                    'Inferior': 0,

                    'Anterior': 0,
                    'Posterior': 0,

                    'Right': 0,
                    'Left': 0
                }
            },

            ResultOperation="Intersection",

            ResultMarginSettings={
                'Type': "Expand",

                'Superior': 0,
                'Inferior': 0,

                'Anterior': 0,
                'Posterior': 0,

                'Right': 0,
                'Left': 0
            }
        )

        print("Created clipped geometry")

    except Exception as e:

        print(f"Clipping failed for {original_name}: {e}")
        continue

    # -----------------------------------------------------
    # Delete original ROI
    # -----------------------------------------------------
    try:

        roi.DeleteRoi()
        print(f"Deleted original ROI: {original_name}")

    except Exception as e:

        print(f"Could not delete {original_name}: {e}")
        continue

    # -----------------------------------------------------
    # Rename clipped ROI back to original name
    # -----------------------------------------------------
    try:

        dst_roi.Name = original_name
        print(f"Renamed {clip_name} -> {original_name}")

    except Exception as e:

        print(f"Rename failed: {e}")

# =========================================================
# DONE
# =========================================================
print("\n✅ Couch clipping + replacement completed")