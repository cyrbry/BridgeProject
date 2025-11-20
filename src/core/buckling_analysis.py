"""
buckling capacity calculations for bridge cross-sections
"""

from src.core.buckling_capacities import sigma_buckling_flexural, tau_buckling_shear

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

def get_buckling_capacities(plates, E, nu):
    """
    calculate all buckling capacities for the cross-section

    Input =
        plates: list of plate dicts
        E: Young's modulus (MPa)
        nu: Poisson's ratio

    Output =
        dict with top_flange, web, bottom_flange, shear buckling stresses, and web_plates
    """
    web_plates = [p for p in plates if p.get('plate_type') == 'web']
    top_plates = [p for p in plates if p.get('plate_type') == 'top_flange']
    bottom_plates = [p for p in plates if p.get('plate_type') == 'bottom_flange']

    # top flange (case 1)
    if top_plates:
        b_top = get_unsupported_width(top_plates, web_plates)
        t_top = min(p['h'] for p in top_plates)
        sigma_buck1 = sigma_buckling_flexural(b_top, t_top, E, nu, case=1)
    else:
        sigma_buck1 = float('inf')

    # web (case 2)
    if web_plates:
        h_web = max(p['h'] for p in web_plates)
        t_web = max(p['b'] for p in web_plates)
        sigma_buck2 = sigma_buckling_flexural(h_web, t_web, E, nu, case=2)
        tau_buck = tau_buckling_shear(h_web, t_web, E, nu)
    else:
        sigma_buck2 = float('inf')
        tau_buck = float('inf')

    # bottom flange (case 3)
    if bottom_plates:
        b_bottom = get_unsupported_width(bottom_plates, web_plates)
        t_bottom = min(p['h'] for p in bottom_plates)
        sigma_buck3 = sigma_buckling_flexural(b_bottom, t_bottom, E, nu, case=3)
    else:
        sigma_buck3 = float('inf')

    return {
        'top_flange': sigma_buck1,
        'web': sigma_buck2,
        'bottom_flange': sigma_buck3,
        'shear': tau_buck,
        'web_plates': web_plates
    }
