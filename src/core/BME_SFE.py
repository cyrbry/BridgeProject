'''
Given the load case and the mass,
return max value of V or M at out of every posssible train location at 10,000 evenly spaced points
These are the SFE vals and the BME vals

These are: max value of V and M at every locaiton of the bridge out of every posssible train location
that the train rolls all the way over the bridge
--> x should range from -856 to 1250:
    - x_start = -856: rightmost wheel just on bridge (at position 0)
    - x_end = 1250: leftmost wheel leaves bridge (at position 1250)
'''

from src.core.reactions_BMD_SFD import SFDvals, BMDvals

def SFEvals(loadcase, mass, num_train_positions=1000):
    """
    Find shear force envelopes (max and min shear at each point on bridge)

    Input = 
        loadcase: 1, 2, or 3
        mass: total mass of train
        num_train_positions: number of train positions to test (default 1000)

    Outputs = 
        sfe_max: list of max shear force at 10,000 points along the bridge
         sfe_min: list of min shear force at 10,000 points along the bridge
    """
    # calculate the range of x values
    # rightmost wheel is at x + (176 + 164 + 176 + 164 + 176) = x + 856
    # x should start when rightmost wheel is before the bridge (x is negative)
    # x should end when rightmost wheel is past the bridge
    train_length = 856  # mm (from leftmost wheel to rightmost wheel)
    bridge_length = 1250  # mm

    x_start = -train_length  # leftmost wheel at -856 (rightmost wheel entering at 0)
    x_end = bridge_length  # leftmost wheel at bridge end (1250mm)

    # generate x positions for the train
    x_positions = [x_start + i * (x_end - x_start) / (num_train_positions - 1)
                   for i in range(num_train_positions)]

    num_points = 10000
    sfe_max = [float('-inf')] * num_points
    sfe_min = [float('inf')] * num_points

    # for each train position, calculate SFD and update envelope
    for x in x_positions:
        sfd = SFDvals(x, loadcase, mass)
        for i in range(num_points):
            sfe_max[i] = max(sfe_max[i], sfd[i])
            sfe_min[i] = min(sfe_min[i], sfd[i])

    return sfe_min, sfe_max

def BMEvals(loadcase, mass, num_train_positions=1000):
    train_length = 856
    bridge_length = 1250

    x_start = -train_length
    x_end = bridge_length

    x_positions = [x_start + i * (x_end - x_start) / (num_train_positions - 1)
                   for i in range(num_train_positions)]

    num_points = 10000
    bme_max = [float('-inf')] * num_points
    bme_min = [float('inf')] * num_points
    for x in x_positions:
        bmd = BMDvals(x, loadcase, mass)
        for i in range(num_points):
            bme_max[i] = max(bme_max[i], bmd[i])
            bme_min[i] = min(bme_min[i], bmd[i])

    return bme_min, bme_max