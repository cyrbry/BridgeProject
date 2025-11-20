
def sigma_top(M_env, y_top, I):
    if abs(I) < 1e-9:
        return 0.0
    return -M_env * y_top / I


def sigma_bot(M_env, y_bot, I):
    if abs(I) < 1e-9:
        return 0.0
    return M_env * y_bot / I


def tau_cent(V_env, Q_cent, I, b_cent):
    if abs(I) < 1e-9 or abs(b_cent) < 1e-9:
        return 0.0
    return abs(V_env) * Q_cent / (I * b_cent)


def tau_glue(V_env, Q_glue, I, b_glue):
    """
    shear stress at glue joint

    tau = VQ/Ib where Q is first moment above the joint, b is glue width
    """
    if abs(I) < 1e-9 or abs(b_glue) < 1e-9:
        return 0.0
    return abs(V_env) * Q_glue / (I * b_glue)
