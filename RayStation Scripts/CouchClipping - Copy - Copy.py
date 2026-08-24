"""
Script name: CouchClipping_SetupBeams.py
Author: Alexandros Puckett Anastasiou, Junior Medical Physicist

Description:
1. Clips couch structures +3 cm SI and ±30 cm XY around ALL PTV/CTV/GTV contours
2. Modifies name, description, and maximum jaw/leaf aperture of setup beams

Disclaimer:
This script is provided as a tool and is not an officially endorsed or clinically validated script for use within RayStation.
It is supplied without any guarantees regarding accuracy, performance, or expected outcomes.
Users must independently verify all results prior to clinical application.

In accordance with the RaySearch Laboratories RayStation Instructions for Use,
all scripts must be thoroughly reviewed and validated by the end user before any clinical use.
Any use of this script, in whole or in part, is performed at the user's own risk.
"""

from connect import get_current

# =========================================================
# COUCH CLIPPING CONFIGURATION
# =========================================================
cube_name = "PTV_3mm_Cube"
clip_suffix = "_Clip"
margin_mm = 3

# Couch detection rules
couch_prefixes = ["Uni_iBeam_CF", "Uni_iBeam_Foam", "BB_CF", "BB_Foam"]

# =========================================================
# SETUP BEAMS CONFIGURATION
# =========================================================
setup_beam_names = ["SG0", "SG90", "SG270"]
jaw_aperture = 12  # cm
min_setup_beams = 3


# =========================================================
# FUNCTION: CLIP COUCH STRUCTURES
# =========================================================
def clip_couch_structures():
    """Clip couch structures around target volumes"""

    # Get objects
    case = get_current("Case")
    exam = get_current("Examination")
    pm = case.PatientModel
    ss = pm.StructureSets[exam.Name]

    roi_names = [r.Name for r in pm.RegionsOfInterest]

    # Delete old clips
    for roi in list(roi_names):
        if roi.endswith(clip_suffix):
            try:
                pm.RegionsOfInterest[roi].DeleteRoi()
            except Exception:
                pass

    roi_names = [r.Name for r in pm.RegionsOfInterest]

    # Find target geometries
    target_geoms = []

    for g in ss.RoiGeometries:
        try:
            if g.HasContours() and any(
                k in g.OfRoi.Name for k in ["PTV", "CTV", "GTV"]
            ):
                target_geoms.append(g)
        except Exception:
            continue

    if not target_geoms:
        raise Exception("No PTV/CTV/GTV contours found")

    print(f"Found {len(target_geoms)} target structure(s)")

    # Build cube bounding box
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

    # Create cube
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

    # Snapshot geometries
    input_geoms = [g for g in ss.RoiGeometries if g.HasContours()]
    processed_couch_rois = []

    # Clip couch structures
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

        # Create algebra geometry
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

    # Delete originals and rename clips
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
            msg = f"DELETE FAILED for {roi_name}: {type(e).__name__}: {e}"
            print(msg)
            failed_replacement.append(msg)
            continue

        try:
            pm.RegionsOfInterest[clip_name].Name = roi_name
            print(f"Renamed clipped ROI {clip_name} -> {roi_name}")
            successfully_replaced.append(roi_name)
        except Exception as e:
            msg = f"RENAME FAILED for {clip_name}: {type(e).__name__}: {e}"
            print(msg)
            failed_replacement.append(msg)

    # Print summary
    print("\n================================")
    print("COUCH CLIPPING SUMMARY")
    print("================================")
    print(f"Successfully replaced: {len(successfully_replaced)}")
    for roi_name in successfully_replaced:
        print(f"  OK  - {roi_name}")

    print(f"\nFailed replacements: {len(failed_replacement)}")
    for msg in failed_replacement:
        print(f"  FAIL - {msg}")

    print("\n✅ Couch clipping completed")

    return successfully_replaced


# =========================================================
# FUNCTION: MODIFY SETUP BEAMS
# =========================================================
def modify_setup_beams():
    """Modify setup beam names, descriptions, jaws, and MLC leaves"""

    case = get_current("Case")
    modified_count = 0
    beam_set_index = 0  # Simple counter for beam set identification

    for plan in case.TreatmentPlans:
        for beam_set in plan.BeamSets:
            setup_beams = beam_set.PatientSetup.SetupBeams

            if len(setup_beams) < min_setup_beams:
                beam_set_index += 1
                continue  # skip if not enough beams

            # Simple identification without using index() method
            print(
                f"\nModifying setup beams in plan: {plan.Name}, beam set #{beam_set_index + 1}"
            )

            # Rename beams and match descriptions
            for i in range(min_setup_beams):
                if i < len(setup_beams):
                    old_name = setup_beams[i].Name
                    setup_beams[i].Name = setup_beam_names[i]
                    setup_beams[i].Description = setup_beam_names[i]
                    print(f"  Renamed beam {i}: {old_name} -> {setup_beam_names[i]}")
                    modified_count += 1

            # Modify jaw + leaf positions
            for beam in setup_beams:
                for segment in beam.Segments:

                    # Modify jaws
                    try:
                        jaws = list(segment.JawPositions)
                        if len(jaws) >= 4:
                            jaws[0] = -jaw_aperture
                            jaws[1] = jaw_aperture
                            jaws[2] = -jaw_aperture
                            jaws[3] = jaw_aperture
                            segment.JawPositions = jaws
                    except Exception as e:
                        print(f"  Could not update jaws for beam {beam.Name}: {e}")

                    # Modify MLC leaves
                    try:
                        leaves = segment.LeafPositions
                        if leaves is not None and len(leaves) >= 2:
                            for i in range(len(leaves[0])):
                                leaves[0][i] = -jaw_aperture
                                leaves[1][i] = jaw_aperture
                            segment.LeafPositions = leaves
                    except Exception as e:
                        print(
                            f"  Could not update leaf positions for beam {beam.Name}: {e}"
                        )

            beam_set_index += 1

    print(f"\n✅ Setup beam modification completed: {modified_count} beams modified")
    return modified_count


# =========================================================
# MAIN EXECUTION
# =========================================================
def main():
    """Execute both couch clipping and setup beam modification"""

    print("\n" + "=" * 60)
    print("STARTING COUCH CLIPPING AND SETUP BEAM MODIFICATION")
    print("=" * 60)

    try:
        # Part 1: Clip couch structures
        print("\n" + "-" * 40)
        print("PART 1: COUCH CLIPPING")
        print("-" * 40)
        clipped_rois = clip_couch_structures()

        # Part 2: Modify setup beams
        print("\n" + "-" * 40)
        print("PART 2: SETUP BEAM MODIFICATION")
        print("-" * 40)
        modified_beams = modify_setup_beams()

        # Final summary
        print("\n" + "=" * 60)
        print("COMPLETE SUMMARY")
        print("=" * 60)
        print(f"✓ Clipped {len(clipped_rois)} couch structure(s)")
        print(f"✓ Modified {modified_beams} setup beam(s)")
        print("\n✅ Both operations completed successfully")

    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        raise


# Run the script
if __name__ == "__main__":
    main()
