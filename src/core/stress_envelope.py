"""
stress envelope and section property calculations
"""

from src.core.geometric_properties import y_bar, I, Q, width, glue_width
from src.core.stresses import sigma_top, sigma_bot, tau_glue

def get_section_properties(plates, glue_joints):
    """
    calculate all geometric properties at of a cross sections

    Input =
        plates: list of plate dicts
        glue_joints: list of y-coordinates where glue is

    Output =
        dict with ybar, I, y_top, y_bot, Q_cent, b_cent
    """
    ybar = y_bar(plates)
    I_val = I(plates)
    y_top = max(plate['y'] + plate['h']/2 for plate in plates) - ybar
    y_bot = ybar - min(plate['y'] - plate['h']/2 for plate in plates)
    Q_cent = Q(plates, ybar)
    b_cent = width(plates, ybar)

    return {
        'ybar': ybar,
        'I': I_val,
        'y_top': y_top,
        'y_bot': y_bot,
        'Q_cent': Q_cent,
        'b_cent': b_cent
    }

def get_stress_envelope(M_max, M_min, y_top, y_bot, I_val):
    """
    find worst-case tension and compression stresses at top and bottom fibers

    Input =
        M_max, M_min: max and min bending moments (N·mm)
        y_top, y_bot: distances from neutral axis to top/bottom (mm)
        I_val: moment of inertia (mm^4)

    Output =
        dict with tension_max, compression_max, top_compression, bottom_compression
    """
    # positive moment (sagging): top in compression, bottom in tension
    sigma_t_pos = sigma_top(M_max, y_top, I_val)  # negative (compression)
    sigma_b_pos = sigma_bot(M_max, y_bot, I_val)  # positive (tension)

    # negative moment (hogging): top in tension, bottom in compression
    sigma_t_neg = sigma_top(M_min, y_top, I_val)  # positive (tension)
    sigma_b_neg = sigma_bot(M_min, y_bot, I_val)  # negative (compression)

    # worst case stresses for each fiber
    sigma_t_comp = min(sigma_t_pos, sigma_t_neg)
    sigma_t_tens = max(sigma_t_pos, sigma_t_neg)
    sigma_b_tens = max(sigma_b_pos, sigma_b_neg)
    sigma_b_comp = min(sigma_b_pos, sigma_b_neg)

    return {
        'tension_max': max(sigma_t_tens, sigma_b_tens),
        'compression_max': min(sigma_t_comp, sigma_b_comp),
        'top_compression': sigma_t_comp,
        'bottom_compression': sigma_b_comp
    }

def get_max_glue_stress(plates, glue_joints, V_env, I_val):
    """
    find maximum shear stress in any glue joint

    Input =
        plates: list of plate dicts
        glue_joints: list of y-coordinates where glue is
        V_env: shear force (N)
        I_val: moment of inertia (mm^4)

    Output =
        max glue shear stress (MPa)
    """
    tau_glue_list = []
    for glue_y in glue_joints:
        Q_glue = Q(plates, glue_y)
        b_glue = glue_width(plates, glue_y)
        if b_glue > 0:
            tau_g = tau_glue(V_env, Q_glue, I_val, b_glue)
            tau_glue_list.append(tau_g)

    return max(tau_glue_list) if tau_glue_list else 0

def get_web_compression_stress(web_plates, M_max, M_min, ybar, I_val):
    """
    calculate compression stress at top of web

    Input =
        web_plates: list of web plate dicts
        M_max, M_min: max and min bending moments (N·mm)
        ybar: neutral axis location (mm)
        I_val: moment of inertia (mm^4)

    Output =
        compression stress at top of web (MPa)
    """
    if not web_plates:
        return 0

    web_top_y = max(p['y'] + p['h']/2 for p in web_plates)
    web_top_dist = web_top_y - ybar

    # use moment that puts web top in compression
    if M_max > 0:
        return -M_max * web_top_dist / I_val
    else:
        return -M_min * web_top_dist / I_val
