"""
material properties for matboard and contact cement glue
"""

def get_matboard_properties():
    """
    matboard properties - E, nu, sigma_tens, sigma_comp, tau_max
    """
    return {
        'E': 4000,          # MPa
        'nu': 0.2,          # Poisson's
        'sigma_tens': 30,   # MPa
        'sigma_comp': 6,    # MPa
        'tau_max': 4        # MPa
    }

def get_glue_properties():
    """
    contact cement glue properties - tau_glue_max
    """
    return {
        'tau_glue_max': 2   # MPa
    }
