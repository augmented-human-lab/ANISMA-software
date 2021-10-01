import math

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class GlobalVars():
    def __init__(self):
        self.skin_mass = 0.0
        self.skin_sprinconstant = 0.0
        self.skin_sprinconstant_diag = 0.0
        self.skin_damping = 0.0
        self.skin_damping_diag = 0.0
        self.anchor_sprinconstant = 0.0
        self.anchor_mass = 0.0
        self.anchor_damping = 0.0
        self.sma_damping = 0.0
        self.sma_mass = 0.0
        self.sma_sprinconstant = 0.0
        self.collisionconstraint = 0.01
        self.smapoweramplifier = 1.0
        self.collisionconstraint_dist = 1.0
        self.dampscale = 1.0
        self.simulationRunning = False

globalvars = GlobalVars()
stiffness = 1

E = 0.05*stiffness*10 # Pa = kg * m^-1 * s^-2
thickness = 0.001  # in meteres

globalvars.skin_mass = 1.02/1000 # in kg 1.02 g/cm2

# setting global skin spring and damping constants
globalvars.skin_sprinconstant = (4 * (5/16)*thickness*E)  # in kg * s^-2
globalvars.skin_sprinconstant_diag = (7/16)*thickness*E   # in kg * s^-2

dampscale = 1
globalvars.skin_damping = 2*math.sqrt(globalvars.skin_mass*globalvars.skin_sprinconstant) * dampscale #
globalvars.skin_damping_diag = 2*math.sqrt(globalvars.skin_mass*globalvars.skin_sprinconstant_diag) * dampscale  #

globalvars.anchor_mass = 0
globalvars.anchor_sprinconstant = 0.01*100
globalvars.anchor_damping = 0.1

globalvars.sma_mass = 5/10000
globalvars.sma_sprinconstant = 0
globalvars.sma_damping = 0.1
