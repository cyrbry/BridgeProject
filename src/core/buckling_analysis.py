"""
buckling capacity calculations for bridge cross-sections
"""

from src.core.buckling_capacities import sigma_buckling_flexural, tau_buckling_shear

def get_stacked_thickness_vertical(plates):
    """
    if plates are stacked vertically (touching in y), sum their thicknesses (h values)
    otherwise return min thickness

    Input =
        plates: list of plate dicts

    Output =
        total thickness if stacked, otherwise min thickness (mm)
    """
    if not plates:
        return 0
    if len(plates) == 1:
        return plates[0]['h']

    # sort by y position
    sorted_plates = sorted(plates, key=lambda p: p['y'])

    # check if all consecutive plates are touching vertically
    all_touching = True
    for i in range(len(sorted_plates)-1):
        p1 = sorted_plates[i]
        p2 = sorted_plates[i+1]
        gap = (p2['y'] - p2['h']/2) - (p1['y'] + p1['h']/2)
        if abs(gap) > 0.01:  # more than 0.01mm gap
            all_touching = False
            break

    if all_touching:
        return sum(p['h'] for p in plates)  # stack them
    else:
        return min(p['h'] for p in plates)  # use thinnest

def get_stacked_thickness_horizontal(plates):
    """
    if plates are stacked horizontally (touching in x), sum their thicknesses (b values)
    otherwise return max thickness

    Input =
        plates: list of plate dicts

    Output =
        total thickness if stacked, otherwise max thickness (mm)
    """
    if not plates:
        return 0
    if len(plates) == 1:
        return plates[0]['b']

    # sort by x position
    sorted_plates = sorted(plates, key=lambda p: p['x'])

    # check if all consecutive plates are touching horizontally
    all_touching = True
    for i in range(len(sorted_plates)-1):
        p1 = sorted_plates[i]
        p2 = sorted_plates[i+1]
        gap = (p2['x'] - p2['b']/2) - (p1['x'] + p1['b']/2)
        if abs(gap) > 0.01:  # more than 0.01mm gap
            all_touching = False
            break

    if all_touching:
        return sum(p['b'] for p in plates)  # sum widths if touching
    else:
        return max(p['b'] for p in plates)  # use thickest if separate

def get_unsupported_width(flange_plates, web_plates):
    """
    calculate max unsupported width between webs for a flange

    Input =
        flange_plates: list of plates in the flange
        web_plates: list of web plates

    Output =
        max unsupported width (mm)
    """
    if not web_plates or len(web_plates) < 2:
        return max(p['b'] for p in flange_plates)

    web_x = sorted([p['x'] for p in web_plates])
    gaps = [web_x[i+1] - web_x[i] for i in range(len(web_x) - 1)]

    # check edge gaps too
    flange_width = max(p['b'] for p in flange_plates)
    flange_x = flange_plates[0]['x']
    left_gap = web_x[0] - (flange_x - flange_width/2)
    right_gap = (flange_x + flange_width/2) - web_x[-1]
    gaps.extend([left_gap, right_gap])

    return max(gaps)

def get_flange_overhang_widths(flange_plates, web_plates):
    """
    calculate inside width and overhang widths for a flange

    Input =
        flange_plates: list of plates in the flange
        web_plates: list of web plates

    Output =
        dict with inside_width, left_overhang, right_overhang, max_overhang (mm)
    """
    if not flange_plates:
        return {'inside_width': 0, 'left_overhang': 0, 'right_overhang': 0, 'max_overhang': 0}

    # find flange edges
    flange_width = max(p['b'] for p in flange_plates)
    flange_x = flange_plates[0]['x']
    flange_left = flange_x - flange_width/2
    flange_right = flange_x + flange_width/2

    if not web_plates:
        # no webs = entire flange is overhang
        return {
            'inside_width': 0,
            'left_overhang': flange_width,
            'right_overhang': 0,
            'max_overhang': flange_width
        }

    # find web inner edges (clear span between supports)
    web_left_edges = []
    web_right_edges = []
    for web in web_plates:
        web_left_edges.append(web['x'] - web['b']/2)
        web_right_edges.append(web['x'] + web['b']/2)

    # leftmost inner edge and rightmost inner edge
    leftmost_web_outer = min(web_left_edges)
    rightmost_web_outer = max(web_right_edges)
    leftmost_web_inner = min(web_right_edges)  # inner edge of leftmost web
    rightmost_web_inner = max(web_left_edges)  # inner edge of rightmost web

    # calculate widths - use inner edges for clear span
    left_overhang = max(0, leftmost_web_outer - flange_left)
    right_overhang = max(0, flange_right - rightmost_web_outer)
    inside_width = rightmost_web_inner - leftmost_web_inner

    return {
        'inside_width': inside_width,
        'left_overhang': left_overhang,
        'right_overhang': right_overhang,
        'max_overhang': max(left_overhang, right_overhang)
    }

def get_buckling_capacities(plates, E, nu, neutral_axis_y, diaphragm_spacing=None):
    """
    calculate all buckling capacities for the cross-section

    Input =
        plates: list of plate dicts
        E: Young's modulus (MPa)
        nu: Poisson's ratio
        neutral_axis_y: location of neutral axis from bottom (mm)
        diaphragm_spacing: spacing between diaphragms along bridge (mm), optional

    Output =
        dict with top_flange_inside, top_flange_overhang, web, shear buckling stresses, and web_plates
    """
    web_plates = [p for p in plates if p.get('plate_type') == 'web']
    top_plates = [p for p in plates if p.get('plate_type') == 'top_flange']

    # top flange case 1 (k=4) - inside portion between webs
    if top_plates:
        overhang_info = get_flange_overhang_widths(top_plates, web_plates)
        t_top = get_stacked_thickness_vertical(top_plates)

        # inside width buckling
        if overhang_info['inside_width'] > 0:
            sigma_buck1 = sigma_buckling_flexural(overhang_info['inside_width'], t_top, E, nu, case=1)
        else:
            sigma_buck1 = float('inf')

        # overhang buckling (case 2, k=0.425)
        if overhang_info['max_overhang'] > 0:
            # determine thickness for overhang - might be less than full stack if some plates don't extend
            t_overhang = get_stacked_thickness_vertical(top_plates)  # for now use same thickness
            sigma_buck2 = sigma_buckling_flexural(overhang_info['max_overhang'], t_overhang, E, nu, case=2)
        else:
            sigma_buck2 = float('inf')  # no overhang = no case 2 check
    else:
        sigma_buck1 = float('inf')
        sigma_buck2 = float('inf')

    # web (case 3, k=6) - compression zone from NA to top of web
    if web_plates:
        web_top = max(p['y'] + p['h']/2 for p in web_plates)
        compression_zone_height = web_top - neutral_axis_y
        t_web = get_stacked_thickness_horizontal(web_plates)
        sigma_buck3 = sigma_buckling_flexural(compression_zone_height, t_web, E, nu, case=3)

        # shear - full height, web thickness, optional spacing
        h_web = max(p['h'] for p in web_plates)
        if diaphragm_spacing:
            tau_buck = tau_buckling_shear(h_web, t_web, E, nu, spacing=diaphragm_spacing)
        else:
            tau_buck = tau_buckling_shear(h_web, t_web, E, nu)
    else:
        sigma_buck3 = float('inf')
        tau_buck = float('inf')

    return {
        'top_flange_inside': sigma_buck1,
        'top_flange_overhang': sigma_buck2,
        'web': sigma_buck3,
        'shear': tau_buck,
        'web_plates': web_plates
    }
