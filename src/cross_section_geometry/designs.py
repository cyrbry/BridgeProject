"""
bridge cross-section designs

each design returns a dict with:
    'plates': list of plate dicts with 'b', 'h', 'x', 'y', 'plate_type'
    'glue_joints': list of y-coordinates where glue joints are

plate_type can be 'top_flange', 'web', or 'bottom_flange'
"""

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

    return {
        'plates': plates,
        'glue_joints': glue_joints
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
