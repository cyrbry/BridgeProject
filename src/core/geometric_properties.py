"""
find geometric properties of a cross section

y_bar = neutral axis location
I = second moment of area
Q = first moment of area above a cut
width = total width at a y level
glue_width = area between plates at a given spot (area for glue to be on)
"""

def y_bar(plates):
    """
    calculate the neutral axis (ybar) of the crosssection

    Input =
        plates: list of dictionaries, each with 'b' (width), 'h' (height), 'x' (center x), 'y' (center y)

    Outputs =
        y_bar is the distance from bottom y=0 to neutral axis (mm)
    """
    total_area = 0
    sum_ay = 0

    for plate in plates:
        area = plate['b'] * plate['h']
        total_area += area
        sum_ay += area * plate['y']

    # division by zero protection
    if total_area < 1e-9:
        return 0.0

    return sum_ay / total_area

def I(plates):
    """
    calculate the total second moment of area I
    
    Input = 
        plates: list of dictionaries, each with 'b', 'h', 'x', 'y'
        
    Outputs = 
        I (mm^4)
    """
    ybar = y_bar(plates)
    
    I_total = 0
    
    for plate in plates:
        b = plate['b']
        h = plate['h']
        y = plate['y']
        area = b * h
        
        # Parallel Axis Theorem: I = I_local + A * d^2
        I_local = (b * h**3) / 12
        d = y - ybar
        
        I_total += I_local + area * d**2
        
    return I_total

def Q(plates, y_cut):
    """
    calculate the first moment of area Q for the area ABOVE y_cut (we might need to do below as well later?)
    
    Input = 
        plates: as above
        y_cut: the y-coordinate where the cut is made (mm)
        
    Outputs = 
        Q above y_cut (mm^3)
    """
    ybar = y_bar(plates)
    
    Q_total = 0
    
    for plate in plates:
        b = plate['b']
        h = plate['h']
        y_center = plate['y']
        
        y_top = y_center + h / 2
        y_bottom = y_center - h / 2
        
        # check if plate is completely below y_cut
        if y_top <= y_cut:
            continue
            
        # check if plate is completely above y_cut
        elif y_bottom >= y_cut:
            area = b * h
            d = y_center - ybar
            Q_total += area * d
            
        # plate is cut by y_cut
        else:
            # calculate stuff for portion above y_cut
            h_above = y_top - y_cut
            y_center_above = y_cut + h_above / 2
            
            area_above = b * h_above
            d = y_center_above - ybar
            Q_total += area_above * d
            
    return Q_total

def width(plates, y_cut):
    """
    calculate the total width of the cross-section at a specific y level

    Input =
        plates: list of dictionaries
        y_cut: the y-coordinate (mm)

    Outputs =
        total_width (mm)
    """
    total_width = 0
    for plate in plates:
        h = plate['h']
        y_center = plate['y']
        y_top = y_center + h / 2
        y_bottom = y_center - h / 2

        # check if y_cut is within the vertical range of the plate
        if y_bottom <= y_cut <= y_top:
             total_width += plate['b']

    return total_width

def glue_width(plates, y_glue):
    """
    calculate the actual glue contact width at a glue joint
    finds plates that meet at y_glue and calculates their overlap

    Input =
        plates: list of dictionaries with 'b', 'h', 'x', 'y'
        y_glue: the y-coordinate of the glue joint (mm)

    Outputs =
        glue_width is the total width of the contact are (mm)
    """
    # find plates with bottom edge at y_glue (plates above the joint)
    plates_above = []
    for plate in plates:
        y_bottom = plate['y'] - plate['h'] / 2
        if abs(y_bottom - y_glue) < 1e-6:
            plates_above.append(plate)

    # find plates with top edge at y_glue (plates below the joint)
    plates_below = []
    for plate in plates:
        y_top = plate['y'] + plate['h'] / 2
        if abs(y_top - y_glue) < 1e-6:
            plates_below.append(plate)

    # if no plates meet at this joint area is 0
    if not plates_above or not plates_below:
        return 0.0

    # for each plate below, find the overlap with plates above
    total_overlap = 0.0

    for plate_below in plates_below:
        # get horizontal are of plate below
        x_below_left = plate_below['x'] - plate_below['b'] / 2
        x_below_right = plate_below['x'] + plate_below['b'] / 2

        for plate_above in plates_above:
            x_above_left = plate_above['x'] - plate_above['b'] / 2
            x_above_right = plate_above['x'] + plate_above['b'] / 2

            # calc overlap
            overlap_left = max(x_below_left, x_above_left)
            overlap_right = min(x_below_right, x_above_right)

            if overlap_right > overlap_left:
                total_overlap += (overlap_right - overlap_left)

    return total_overlap
