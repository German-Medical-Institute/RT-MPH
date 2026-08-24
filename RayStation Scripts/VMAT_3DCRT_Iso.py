from connect import *

case = get_current("Case")
beam_set = get_current("BeamSet")

allowed_techniques = ["VMAT", "3D-CRT"]

pelvis_rois = [
    "Prostate", "Bladder", "FemoralHead_L", "FemoralHead_R",
    "Femur_L", "Femur_R", "Endometrium", "Uterus",
    "CTV_Pelvis", "PTV_Pelvis"
]

def is_pelvis_case(case):
    roi_names = [r.Name for r in case.PatientModel.RegionsOfInterest]
    return any(r in roi_names for r in pelvis_rois)

def is_allowed_technique(beam_set):
    return beam_set.DeliveryTechnique in allowed_techniques

if not is_allowed_technique(beam_set):
    print("Not VMAT/3DCRT - skipping")
elif not is_pelvis_case(case):
    print("Not pelvis case - skipping")
else:
    for beam in beam_set.Beams:
        x, y, z = beam.Isocenter.Position

        if z >= 12.5:
            beam.SetIsocenterPosition((x, y, 11.80))
            print(f"{beam.Name}: iso adjusted to 11.80 cm")