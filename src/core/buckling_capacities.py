import math

def sigma_buckling_flexural(b, t, E, nu, case=1):
    """
     buckling stress for flexural compression

    Input =
        b: width of plate (mm)
        t: thickness (mm)
        E: Young's modulus (MPa)
        nu: Poisson's ratio
        case: 1, 2, or 3 (different boundary conditions)

    Outputs sigma_crit in MPa
    """
    
    # buckling coefficient k depends on boundary conditions
    if case == 1:
        k = 4.0  # both edges restrained (for design)
    elif case == 2:
        k = 0.425  # one side restrained
    elif case == 3:
        k = 6.0  # triangular/irregular distribution
    
    # find critical buckling stress
    sigma_crit = (k * math.pi**2 * E) / (12 * (1 - nu**2)) * (t / b)**2
    
    return sigma_crit

def tau_buckling_shear(h, t, E, nu):
    """
    crit shear buckling stress for web

    Input =
        h: height of web (mm)
        t: thickness (mm)
        E: Young's modulus (MPa)
        nu: Poisson's ratio

    Outputs tau_crit (MPa)
    """
    
    # k=5 accounts for diagonal buckling
    k = 5.0
    
    # calculate critical shear buckling stress
    tau_crit = (k * math.pi**2 * E) / (12 * (1 - nu**2)) * (t / h)**2
    
    return tau_crit
