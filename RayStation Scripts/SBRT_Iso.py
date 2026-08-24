case = get_current("Case")
beam_set = get_current("BeamSet")

if beam_set.DeliveryTechnique != "SBRT":
    print("Not SBRT - skipping")
else:
    for beam in beam_set.Beams:
        x, y, z = beam.Isocenter.Position

        if z >= 2.0:
            beam.SetIsocenterPosition((x, y, 2.0))
            print(f"{beam.Name}: SBRT iso clamped to 2.0 cm")