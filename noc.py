#Gernot Ohner, 1310210

#partly adapted from fself.dtd.wikispaces.com/code
#Licensed under Creative Commons Attribution Share-Alike 3.0 Licence
#http://www.creativecommons.org/licenses/by-sa/3.0
import time
import shelve
import math
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.animation as anim
import numpy as np 
import scipy.constants as const
import progressbar
from source import Source
import timeit

class FDTD():
    """
    Methods: 
    __init__
    pml()
    makeenv()
    luneberg()
    compute()
    fdplot()

    Instance variables:
    f, xmin, xmax, ymin, ymax, nt, interval, ds, dt, nx, ny, p, q, source, actualsource, R
    """
    
    def __init__(self, f, shape, nt, src = "pulse_gauss", interval = 1, p = 1, q = 1.5, R = 50):
        """Initialize the FDTD object and compute some basic additional parameters (ds, dt, nx, ny)"""

        self.f = f
        self.xmin, self.xmax, self.ymin, self.ymax = shape
        self.nt = nt
        self.interval = interval
        self.ds=const.c/(20*f) #spacial stepsize, according to stability criterion
        self.dt=self.ds/(const.c*math.sqrt(2))
        # that this doesnt check out is a possible source of the problem
        self.nx = int((self.xmax-self.xmin)/self.ds)
        self.ny = int((self.ymax-self.ymin)/self.ds)
        self.p = p
        self.q = q
        self.source = Source(self.xmin, self.xmax, self.ymin, self.ymax, self.nx, self.ny)
        self.actualsource = self.source.src(src)
        self.R = R
     
    def pml(self, eps, mu):
        """Creates matrices for the electric (sigma_x, sigma_y) and magnetic (sigma_mx, sigma_my) conductivities on
        at the border of the computational domain. Computes the values for these matrices at a given position.
        Returns these matrices."""

        #sigma_x = np.zeros((self.nx, self.ny+1))
        #sigma_y = np.zeros((self.nx+1, self.ny))
        m = 3
        nb = 10
        R0 = 1e-5
# mu and eps are not yet used
        sigma_x = np.zeros((self.nx, self.ny))
        sigma_y = np.zeros((self.nx, self.ny))
        sigmamax = -math.log(R0)*(m+1)/(np.sqrt(const.mu_0/const.epsilon_0)*2*nb*self.ds)/self.p
    
        for n in range(nb): 
            sigma_x[n,:] = ((nb-n)/nb)**m*sigmamax
            sigma_x[-n-1,:] = ((nb-n)/nb)**m*sigmamax
            sigma_y[:,n] = ((nb-n)/nb)**m*sigmamax
            sigma_y[:,-n-1] = ((nb-n)/nb)**m*sigmamax

            # sigma_mx[n,:] = ((nb-n+0.5)/nb)**m*sigmamax[n,:]
            # sigma_mx[-n-1,:] = ((nb-n-0.5)/nb)**m*sigmamax[-n-1,:]
            # sigma_my[:,n] = ((nb-n+0.5)/nb)**m*sigmamax[:,n]
            # sigma_my[:,-n-1] = ((nb-n-0.5)/nb)**m*sigmamax[:,-n-1]
        return sigma_x, sigma_y, sigma_x*const.mu_0/const.epsilon_0, sigma_y*const.mu_0/const.epsilon_0
    
    
    def makeenv(self):
        """Compute and return matrices of the permittivity and permeability."""
        eps=np.ones((self.nx,self.ny))*const.epsilon_0
        mu=np.ones((self.nx,self.ny))*const.mu_0

        eps[:20,:] *= self.q #adself.ds a space of higher permittivity 
        eps[-20:,:] *= self.q #adself.ds a space of higher permittivity 
        eps[:,:20] *= self.q #adself.ds a space of higher permittivity 
        eps[:,-20:] *= self.q #adself.ds a space of higher permittivity 
        #mu[:20,:] /= self.q #adself.ds a space of higher permittivity 
        #mu[-20:,:] /= self.q #adself.ds a space of higher permittivity 
        #mu[:,:20] /= self.q #adself.ds a space of higher permittivity 
        #mu[:,-20:] /= self.q #adself.ds a space of higher permittivity 

        return eps, mu    
    
    def luneberg(self, mx, my, R):
        """Modifies the permittivity to create a Luneberg lens at position (mx,my) of radius R
        Returns the a matrix containing the new permittivities"""
        e = np.ones((self.nx, self.ny))
        for qx in range(mx-R, mx+R):
            for qy in range(my-R, my+R):
                r = int(math.sqrt((qx-mx)**2 + (qy-my)**2))
                if r>R: continue
                e[qx-1, qy-1] = 2 - (r/R)**2

        return e*const.epsilon_0


    #def seteps(self, eps): self.eps = eps
    #def setmu(self, mu): self.mu = mu 

    def compute(self):
        """Creates matrices for the field components Ex, Ey, Hz, Hzx and Hzy.
        Does some extra computations.
        Computes the FDTD simulation.
        Returns a list of numpy matrices containing the sum of squares of Ex and Ey.""" 
        Ex=np.zeros((self.nx,self.ny+1))
        Ey=np.zeros((self.nx+1,self.ny))
        Hz=np.zeros((self.nx,self.ny))
        Hzx=np.zeros((self.nx,self.ny))
        Hzy=np.zeros((self.nx,self.ny))
    
        imx = []
        #eps, mu = self.makeenv()
        mu=np.ones((self.nx,self.ny))*const.mu_0
        eps = self.luneberg(int(self.nx/2), int(self.ny*2/3), self.R)
        eps[:20,:] *= self.q #adself.ds a space of higher permittivity 
        eps[-20:,:] *= self.q #adself.ds a space of higher permittivity 
        eps[:,:20] *= self.q #adself.ds a space of higher permittivity 
        eps[:,-20:] *= self.q #adself.ds a space of higher permittivity 

        c = self.dt/(eps*self.ds)
        d = self.dt/(mu* self.ds)
    
        sigma = self.pml(eps, mu)
        cay = 1 - (sigma[1][:,1:] + sigma[0][:,:-1]) * self.dt / (eps[:,1:]+eps[:,:-1])
        cax = 1 - (sigma[0][1:,:] + sigma[1][:-1,:]) * self.dt / (eps[1:,:]+eps[:-1,:])
        dax = 1 - (sigma[2] * self.dt / mu)
        day = 1 - (sigma[3] * self.dt / mu)
    
        ca1 = (c[:,1:]+c[:,:-1])/2
        ca2 = (c[1:,:]+c[:-1,:])/2

        bar = progressbar.ProgressBar()
        for n in bar(range(self.nt+1)):
            #Ex[:,1:-1] = cay*Ex[:,1:-1] + ca1*(Hz[:,1:]-Hz[:,:-1])
            Ex[:,1:-1] *= cay
            Ex[:,1:-1] += ca1*(Hz[:,1:]-Hz[:,:-1])
            #Ey[1:-1,:] = cax*Ey[1:-1,:] - ca2*(Hz[1:,:]-Hz[:-1,:])
            Ey[1:-1,:] *= cax 
            Ey[1:-1,:] -= ca2*(Hz[1:,:]-Hz[:-1,:])
    
            #Hzx = dax*Hzx - d*(Ey[1:,:] - Ey[:-1,:])
            Hzx *= dax
            Hzx -= d*(Ey[1:,:] - Ey[:-1,:])
            #Hzy = day*Hzy + d*(Ex[:,1:] - Ex[:,:-1])
            Hzy *= day
            Hzy += d*(Ex[:,1:] - Ex[:,:-1]) 
            Hz = Hzx + Hzy + self.actualsource(self.source, self.f, n, self.dt) 
    
            if(n%self.interval == 0): imx.append(Ex[:self.nx,:self.ny]**2 + Ey[:self.nx, :self.ny]**2)

        print('Computation complete.')
        shelf_file = shelve.open('fdtd_data')
        shelf_file['data'] = imx
        shelf_file.close()
        print('Saving computed values complete.')

    def fdplot(self):
        """Plots the matrices computed by compute(). Displays the generated images in sequence."""
        fig = plt.figure()
        shelf_file = shelve.open('fdtd_data')
        imx = shelf_file['data']
        shelf_file.close()
        maxval = np.max(imx)

        ims = list(map(lambda im: [plt.imshow(np.fabs(im),norm=colors.Normalize(0.0,maxval))], imx))
        animation = anim.ArtistAnimation(fig,ims,interval=50)
        plt.show()