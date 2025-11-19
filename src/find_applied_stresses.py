
def sigma_top(M_env, y_top, I):
    return -M_env * y_top / I


def sigma_bot(M_env, y_bot, I):
    return M_env * y_bot / I


def tau_cent(V_env, Q_cent, I, b_cent):
    return abs(V_env) * Q_cent / (I * b_cent)


def tau_glue(V_env, Q_glue, I, b_glue):
    """
    V_env = shear force from envelope at location x (N)
    Q_glue = ffirst moment of area at glue joint (mm³)
    I = Second moment of area about neutral axis (mm⁴)
    b_glue =  width at the glue joint (mm)
    """
    return abs(V_env) * Q_glue / (I * b_glue)
