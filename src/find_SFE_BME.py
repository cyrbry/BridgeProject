'''
given the load case and the mass,
return max value of V or M at out of every posssible train location at 10,000 evenly spaced points
These are the SFE vals and the BME vals

These are: max value of V and M at every locaiton of the bridge out of every posssible train location
that the train rolls all the way over the bridge
--> x should start at -(52 + 176 + 164 + 176 + 164 + 176) and end at 1250-52 which is when the first (leftmost ) wheel is at 1250mm
This which is when the last (rightm ost) wheel is not yet even on the bridge (first wheel is at 0)
'''

from find_reactions_SFD_BMD import SFDvals, BMDvals

def SFEvals(loadcase, mass, num_train_positions=1000):
    """
    Find shear force envelopes (max and min shear at each point on bridge)

    Input = 
        loadcase: 1, 2, or 3
        mass: total mass of train
        num_train_positions: number of train positions to test (default 1000)

    Outputs = 
        sfe_max is a list of max shear force at 10,000 points along the bridge
         sfe_min is a list of min shear force at 10,000 points along the bridge
    """
    # calculate the range of x values
    # last wheel (rightmost wheel - firest on the bridge) is at x + (52 + 176 + 164 + 176 + 164 + 176) = x + 908
    # x should start when last (rightmost) wheel is before the bridge (negative)
    # x should end when last wheel is past the bridge
    train_length = 908  # mm (from start of train to last wheel, first wheel is at )
    bridge_length = 1250  # mm

    x_start = -train_length  # first wheel before the bridge
    x_end = bridge_length - 52  # first wheel at bridge end (x + 52 = 1250)

    # generate x positions for the train
    x_positions = [x_start + i * (x_end - x_start) / (num_train_positions - 1)
                   for i in range(num_train_positions)]

    # initialize envelopes
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
    """
    Find bending moment envelopes (max and min moment at each point on bridge)

    Input =
        loadcase: 1, 2, or 3
        mass: total mass of train
        num_train_positions: number of train positions to test (default 1000)

    Outputs =
        bme_max is a list of max bending moment at 10,000 points along the bridge
        bme_min is a list of min bending moment at 10,000 points along the bridge
    """
    train_length = 908
    bridge_length = 1250

    x_start = -train_length
    x_end = bridge_length - 52

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