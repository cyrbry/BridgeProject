"""
bridge cross-section designs

each design returns a dict with:
    'plates': list of plate dicts with 'b', 'h', 'x', 'y', 'plate_type'
    'glue_joints': list of y-coordinates where glue joints are

plate_type can be 'top_flange', 'web', or 'bottom_flange'
"""

def design0():
    """
    cross section with 100mm top flange, 80mm bottom flange, two webs, and small glue tab flanges
    """
    plates = [
        {'b': 100, 'h': 1.27, 'x': 50, 'y': 74.365, 'plate_type': 'top_flange'},    # top flange
        {'b': 1.27, 'h': 72.46, 'x': 10.635, 'y': 37.5, 'plate_type': 'web'},   # left web
        {'b': 1.27, 'h': 72.46, 'x': 89.365, 'y': 37.5, 'plate_type': 'web'},  # right web
        {'b': 80, 'h': 1.27, 'x': 50, 'y': 0.635, 'plate_type': 'bottom_flange'},     # bottom flange
        {'b': 5, 'h': 1.27, 'x': 13.77, 'y': 73.095, 'plate_type': 'top_flange'},  # left glue tab
        {'b': 5, 'h': 1.27, 'x': 86.23, 'y': 73.095, 'plate_type': 'top_flange'},  # right glue tab
    ]

    glue_joints = [73.73, 1.27]
    diaphragm_spacing = 150  # mm between diaphragms

    return {
        'plates': plates,
        'glue_joints': glue_joints,
        'diaphragm_spacing': diaphragm_spacing
    }


def simple_square():
    """
    hollow box
    """
    plates = [
        {'b': 100, 'h': 1.27, 'x': 50, 'y': 99.365, 'plate_type': 'top_flange'},    # top flange
        {'b': 1.27, 'h': 97.46, 'x': 0.635, 'y': 50, 'plate_type': 'web'},   # left web
        {'b': 1.27, 'h': 97.46, 'x': 99.365, 'y': 50, 'plate_type': 'web'},  # right web
        {'b': 100, 'h': 1.27, 'x': 50, 'y': 0.635, 'plate_type': 'bottom_flange'},     # bottom flange
    ]

    glue_joints = [98.73, 1.27]
    diaphragm_spacing = 150  # mm between diaphragms

    return {
        'plates': plates,
        'glue_joints': glue_joints,
        'diaphragm_spacing': diaphragm_spacing
    }


def cigar():

    plates = [
        {'b': 100.0, 'h': 1.27, 'x': 49.650, 'y': 113.122, 'plate_type': 'top_flange'},
        {'b': 1.27, 'h': 112.0, 'x': 10.635, 'y': 56.487, 'plate_type': 'web'},
        {'b': 75.0, 'h': 1.27, 'x': 48.770, 'y': 1.122, 'plate_type': 'bottom_flange'},
        {'b': 75.0, 'h': 1.27, 'x': 48.770, 'y': 110.582, 'plate_type': 'top_flange'},
        {'b': 75.0, 'h': 1.27, 'x': 48.770, 'y': 111.852, 'plate_type': 'top_flange'},
        {'b': 1.27, 'h': 112.0, 'x': 86.905, 'y': 56.487, 'plate_type': 'web'},
    ]

    glue_joints = []
    diaphragm_spacing = 150  # mm between diaphragms

    return {
        'plates': plates,
        'glue_joints': glue_joints,
        'diaphragm_spacing': diaphragm_spacing
    }


def get_geometry_at_x(geometry, x):
    """
    gives the cross section geometry at position along the bridge

    for now, this just returns the same geometry everywhere
    later we can extende it to have the geometry change along the bridge

    Input =
        geometry: dict from simple_square() or other geometry function
        x: position along bridge (mm)

    Outputs =
        plates is a list of plate dicts at position x
        glue_joints is a list of glue joint y-coordinates at position x
    """
    # for constant cross-section we just return the same geometry
    return geometry['plates'], geometry['glue_joints']
