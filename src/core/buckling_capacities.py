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

def tau_buckling_shear(h, t, E, nu, spacing=None):
    """
    crit shear buckling stress for web

    Input =
        h: height of web (mm)
        t: thickness (mm)
        E: Young's modulus (MPa)
        nu: Poisson's ratio
        spacing: spacing between diaphragms (mm), optional

    Outputs tau_crit (MPa)
    """

    # k=5 accounts for diagonal buckling
    k = 5.0

    # calculate critical shear buckling stress
    # includes both height and spacing terms if spacing provided
    term1 = (t / h)**2
    term2 = (t / spacing)**2 if spacing else 0

    tau_crit = (k * math.pi**2 * E) / (12 * (1 - nu**2)) * (term1 + term2)

    return tau_crit

def euler_buckling_load(I, E, L):
    """
    critical load for global euler buckling of the whole bridge

    Input =
        I: moment of inertia (mm^4)
        E: Young's modulus (MPa)
        L: length of bridge (mm)

    Output = P_critical (N)
    """

    P_crit = (math.pi**2 * E * I) / (L**2)

    return P_crit
