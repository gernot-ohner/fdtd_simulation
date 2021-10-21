import math
import numpy as np
import scipy.constants as const

class Source():
    
    def __init__(self, *args):
        #possible source types are: "pulse gauss", "continuous gauss"
        self.xmin, self.xmax, self.ymin, self.ymax, self.nx, self.ny = args[:6]
        self.x = np.linspace(self.xmin,self.xmax,self.nx)
        self.y = np.linspace(self.ymin,self.ymax,self.ny)
        

    def src(self, src_type):

        def cont_gauss(self, *args):
            X, Y = np.meshgrid(self.y,self.x)
            f, n, dt = args
            return np.sin(f*n*dt)*np.exp(-(X*X + Y*Y)/0.1**2) 

        def pulse_gauss(self, *args):
            X, Y = np.meshgrid(self.y,self.x)
            f, n, dt = args
            return np.sin(f*n*dt)*np.exp(-f*n*dt -(X*X + Y*Y)/0.1**2) 

        def point(self, *args):
            amp = args[0]
            return amp

    
        if src_type == "pulse_gauss":
            return pulse_gauss
        elif src_type == "cont_gauss":
            return cont_gauss
        elif src_type == "point":
            return point



