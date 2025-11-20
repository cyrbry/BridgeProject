"""
calculate reactions, then SFD and BMD for the bridge

Input =
    x: position of leftmost wheel on bridge (mm from left edge of bridge)
    loadcase: 1, 2 or 3 (load case 3 is really 2.1 where the last freight car is extra heavy)
    mass: mass of all trains

 reactions(x, loadcase, mass): returns RA and RB
SFDvals: returns shear force at 10,000 evenly spaced points
BMDvals: returns moment at 10,000 evenly spaced points

Assumptions
    - bridge is 1250 mm long
    - supports at 25 mm and 1225 mm

    load case 1:
    - 3 cars
    - 6 contact points with load equal to m/6 at each (6 point loads)
    - leftmost wheel is at x,
        second is 176 from that,
        3rd is 164 from that,
        4th is 176 from that,
        5th is 164 from that,
        6th is 176 from that.

    load case 2:
    - 3 cars still
    - same six contact points (note the leftmost two wheels are part of car 1, second 2 are car 2 etc)
    - leftmost car is a 'locomotive car" 1.35x the mass of the other two

    load case 3: (really 2.1 or load case 2 from train 3 onward pretty much)
    - same as load case 2, but:
    - rightmost car is a heavy freight car, 1.1 x the weight of the light freight car (which is in the middle)
    - leftmost car is the locomotive, 1.38x the wieght of the heavy freight car or 1.38x1.1 the wight of the light middle freight car
"""

def get_wheel_loads(x, loadcase, mass):
    """
    calculate wheel positions and loads for a the load case

    Input =
        x: position of leftmost wheel (mm from left edge of bridge)
        loadcase: 1, 2, or 3
        mass: total mass of train

    Outputs =
        wheel_positions is a list of 6 wheel positions (mm)
        wheel_loads is a list of 6 wheel loads (N)
    """
    # wheel positions (same for all load cases)
    wheel_positions = [
        x,
        x + 176,
        x + 176 + 164,
        x + 176 + 164 + 176,
        x + 176 + 164 + 176 + 164,
        x + 176 + 164 + 176 + 164 + 176
    ]

    # calculate wheel loads based on load case
    if loadcase == 1:
        # load case 1: all cars equal mass
        wheel_loads = [mass / 6] * 6

    elif loadcase == 2:
        # load case 2: locomotive + 2 regular cars
        locomotive_ratio = 1.35
        regular_ratio = 1.0

        total_ratio = locomotive_ratio + 2 * regular_ratio
        mass_regular_car = mass / total_ratio
        mass_locomotive = locomotive_ratio * mass_regular_car

        wheel_loads = [
            mass_locomotive / 2, mass_locomotive / 2,      # leftmost car (locomotive)
            mass_regular_car / 2, mass_regular_car / 2,    # middle car (regular)
            mass_regular_car / 2, mass_regular_car / 2     # rightmost car (regular)
        ]

    elif loadcase == 3:
        # load case 3: locomotive + light freight + heavy freight
        light_freight_ratio = 1.0
        heavy_freight_ratio = 1.1 * light_freight_ratio
        locomotive_ratio = 1.38 * heavy_freight_ratio

        total_ratio = locomotive_ratio + light_freight_ratio + heavy_freight_ratio
        mass_light_freight = mass / total_ratio
        mass_heavy_freight = heavy_freight_ratio * mass_light_freight
        mass_locomotive = locomotive_ratio * mass_light_freight

        wheel_loads = [
            mass_locomotive / 2, mass_locomotive / 2,           # leftmost car (locomotive)
            mass_light_freight / 2, mass_light_freight / 2,     # middle car (light freight)
            mass_heavy_freight / 2, mass_heavy_freight / 2      # rightmost car (heavy freight)
        ]

    return wheel_positions, wheel_loads


def reactions(x, loadcase, mass):
    """
    calculate reaction forces at supports A (25mm) and B (1225mm)

    Input =
        x: position of leftmost wheel (mm from left edge of bridge)
        loadcase: 1, 2, or 3
        mass: total mass of train

    Outputs =
        RA is the reaction force at left support (N)
        RB is the reaction force at right support (N)
    """
    # get wheel positions and loads
    wheel_positions, wheel_loads = get_wheel_loads(x, loadcase, mass)

    # support positions
    support_B = 1225  # mm from left
    span = 1200       # distance between supports

    # sum of moments about support B = 0 (to find RA)
    moment_sum = 0
    active_load_sum = 0
    
    for i, pos in enumerate(wheel_positions):
        # only consider wheels on the bridge (0 <= pos <= 1250)
        if 0 <= pos <= 1250:
            distance = support_B - pos
            moment_sum += wheel_loads[i] * distance
            active_load_sum += wheel_loads[i]

    # RA * span = moment_sum
    RA = moment_sum / span

    # sum of vertical forces = 0
    # only subtract RA from the sum of loads *on the bridge*
    RB = active_load_sum - RA

    return RA, RB

def SFDvals(x, loadcase, mass):
    """
    calculate shear force at 10,000 evenly spaced points

    Input =
        x: position of leftmost wheel (mm from left edge of bridge)
        loadcase: 1, 2, or 3
        mass: total mass of train

    Outputs =
        sfd is a list of shear force values at 10,000 points from 0 to 1250 mm
    """
    # get reaction forces and wheel loads
    RA, RB = reactions(x, loadcase, mass)
    wheel_positions, wheel_loads = get_wheel_loads(x, loadcase, mass)

    # Support positions
    support_A = 25    # mm from left
    support_B = 1225  # mm from left

    # create 10,000 evenly spaced points from 0 to 1250
    num_points = 10000
    bridge_length = 1250
    positions = [i * bridge_length / (num_points - 1) for i in range(num_points)]

    # calculate shear force at each position
    sfd = []
    for pos in positions:
        shear = 0

        # add reaction at support A if we're past it
        if pos >= support_A:
            shear += RA

        # subtract each wheel load if we're past it AND the wheel is on the bridge
        for i, wheel_pos in enumerate(wheel_positions):
            if pos >= wheel_pos and 0 <= wheel_pos <= bridge_length:
                shear -= wheel_loads[i]

        # add reaction at support B if we're past it
        if pos >= support_B:
            shear += RB

        sfd.append(shear)

    return sfd

def BMDvals(x, loadcase, mass):
    """
    calculate bending moment values at 10,000 evenly spaced points

    Input =
        x: position of leftmost wheel (mm from left edge of bridge)
        loadcase: 1, 2, or 3
        mass: total mass of train

    Outputs =
        bmd is a list of bending moment values at 10,000 points from 0 to 1250 mm
    """
    # Get reaction forces and wheel loads
    RA, RB = reactions(x, loadcase, mass)
    wheel_positions, wheel_loads = get_wheel_loads(x, loadcase, mass)

    # Support positions
    support_A = 25    # mm from left
    support_B = 1225  # mm from left

    # Create 10,000 evenly spaced points from 0 to 1250
    num_points = 10000
    bridge_length = 1250
    positions = [i * bridge_length / (num_points - 1) for i in range(num_points)]

    # calculate bending moment at each position
    # moment = sum of (force * distance to that force)
    bmd = []
    for pos in positions:
        moment = 0

        # add moment from reaction at support A if we're past it
        if pos >= support_A:
            moment += RA * (pos - support_A)

        # subtract moment from each wheel load if we're past it AND the wheel is on the bridge
        for i, wheel_pos in enumerate(wheel_positions):
            if pos >= wheel_pos and 0 <= wheel_pos <= bridge_length:
                moment -= wheel_loads[i] * (pos - wheel_pos)

        # add moment from reaction at support B if we're past it
        if pos >= support_B:
            moment += RB * (pos - support_B)

        bmd.append(moment)

    return bmd