"""
Script name: SetupBeams.py
Author: Alexandros Puckett Anastasiou, Junior Medical Physicist

Description:
This script is intended to modify the name, description, and maximum jaw aperture of setup beams within a treatment plan.

Disclaimer:
This script is provided as a tool and is not an officially endorsed or clinically validated script for use within RayStation.
It is supplied without any guarantees regarding accuracy, performance, or expected outcomes.
Users must independently verify all results prior to clinical application.

In accordance with the RaySearch Laboratories RayStation Instructions for Use,
all scripts must be thoroughly reviewed and validated by the end user before any clinical use.
Any use of this script, in whole or in part, is performed at the user’s own risk.
"""

from connect import *

case = get_current("Case")

for plan in case.TreatmentPlans:
    for beam_set in plan.BeamSets:
        setup_beams = beam_set.PatientSetup.SetupBeams

        if len(setup_beams) < 3:
            continue  # skip if not enough beams

        # Rename beams and match descriptions
        names = ["SG0", "SG90", "SG270"]

        for i in range(3):
            setup_beams[i].Name = names[i]
            setup_beams[i].Description = names[i]

        # Modify jaw + leaf positions
        for beam in setup_beams:
            for segment in beam.Segments:

                # -------------------------
                # JAWS (your original code)
                # -------------------------
                jaws = list(segment.JawPositions)

                jaws[0] = -12
                jaws[1] =  12
                jaws[2] = -12
                jaws[3] =  12

                segment.JawPositions = jaws

                # -------------------------
                # MLC LEAVES (ADDED)
                # -------------------------
                try:
                    leaves = segment.LeafPositions

                    # usually: leaves[0] = bank A, leaves[1] = bank B
                    for i in range(len(leaves[0])):

                        leaves[0][i] = -12
                        leaves[1][i] =  12

                    segment.LeafPositions = leaves

                except Exception as e:
                    print("Could not update leaf positions:", e)