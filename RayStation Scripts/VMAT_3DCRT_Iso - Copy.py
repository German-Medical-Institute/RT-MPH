from connect import *

case = get_current("Case")
beam_set = get_current("BeamSet")

allowed_techniques = ["VMAT", "3D-CRT"]

def is_allowed(beam_set):
    return beam_set.DeliveryTechnique in allowed_techniques

if not is_allowed(beam_set):
    print("Not VMAT/3DCRT - skipping")

else:
    setup = beam_set.PatientSetup
    ttp = setup.TreatmentSetupPositions[0].TableTopDisplacement
    couch_z = ttp[2]

    for beam in beam_set.Beams:
        x, y, iso_z = beam.Isocenter.Position

        distance = iso_z - couch_z

        print(f"{beam.Name}: iso-couch distance = {distance:.2f} cm")

        if distance >= 12.0:
            new_z = couch_z + 11.80
            beam.SetIsocenterPosition((x, y, new_z))
            print(f"{beam.Name}: adjusted to 11.80 cm above couch")