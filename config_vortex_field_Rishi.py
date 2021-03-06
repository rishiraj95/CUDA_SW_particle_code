from netCDF4 import Dataset
import numpy as np
import sys

##
### Specify simulation parameters
##

# Simulation paramters

Nx = 512
Ny = 512

Lx = 10.
Ly = 10.

dx = Lx/Nx
dy = Ly/Ny

g       = 9.81
H0      = 0.5
f0      =1/4*1.

output = 0
time  = 0.
final_time    = 200.
plot_interval = 1.

num_particles = 400**2
particle_int_distance=0.007

# Create the grid
x = np.arange(0, Lx, dx)
y = np.arange(0, Ly, dy)

X, Y = np.meshgrid(x, y)

Y -= y.mean()
X -= x.mean()

# Specify initial conditions
num_vortices = 180

mean_width = 0.03*Lx 
std_width = 0.05*mean_width

Ro = 0.1
mean_veloc = 4*Ro * f0 * mean_width
std_veloc = 0.05*mean_veloc

u_data = np.zeros(X.shape)
v_data = np.zeros(X.shape)
eta_data = np.zeros(X.shape)
t_data = np.random.rand(*X.shape)

# Loop through and add each vortex
for ii in range(num_vortices):
    
    xc = 0.8*(np.random.random() - 0.5) * Lx
    yc = 0.8*(np.random.random() - 0.5) * Ly

    width = -1.
    while (width <= 0):
        width = np.random.randn() * std_width + mean_width
    veloc = np.random.randn() * std_veloc + mean_veloc

    if (np.random.random() > 0.5):
        veloc *= -1.

    XX = X - xc
    YY = Y - yc

    XX *= 1./width
    YY *= 1./width

    Gaus = np.exp( - XX**2 - YY**2 )
    eta_0 = f0 * veloc * width * np.sqrt(np.exp(1)/2.) / g
    vel_0 = veloc * np.sqrt(2*np.exp(1))

    eta_data +=   eta_0           * Gaus
    v_data +=   vel_0 * XX * Gaus
    u_data += - vel_0 * YY * Gaus

b1_data=np.zeros(X.shape)
b2_data=np.zeros(X.shape)
H_data=H0*np.ones(X.shape)

# Specify initial particle positions

x_p = np.linspace(0.0, Lx, np.sqrt(num_particles))
y_p = np.linspace(0.0, Ly, np.sqrt(num_particles))

Xp,Yp = np.meshgrid(x_p,y_p);

x_part = Xp.ravel()
y_part = Yp.ravel()

u_part = 0*x_part;
v_part = 0*x_part;


##
### Output to initial_conditions.nc
###   user shouldn't need to modify anything after this
##

# Create file
fp = Dataset('initial_conditions.nc', 'w', format='NETCDF4')
fp.description = 'Initial conditions for simulation'
    
# Create dimension objects
x_dim = fp.createDimension('x',Nx)
y_dim = fp.createDimension('y',Ny)
traj_dim = fp.createDimension('trajectory',num_particles)
const_dim = fp.createDimension('const', 1)

# Create variables, assign attributes, and write data
u_var = fp.createVariable('u', 'd', ('y','x'), contiguous=True)
u_var.units = 'm/s'
u_var[:,:] = u_data

v_var = fp.createVariable('v', 'd', ('y','x'), contiguous=True)
v_var.units = 'm/s'
v_var[:,:] = v_data

eta_var = fp.createVariable('eta', 'd', ('y','x'), contiguous=True)
eta_var.units = 'm'
eta_var[:,:] = eta_data

t_var = fp.createVariable('tracer', 'd', ('y','x'), contiguous=True)
t_var.units = 'n/a'
t_var[:,:] = t_data

Nx_var = fp.createVariable('Nx', np.int, ('const',))
Nx_var[0] = Nx

Ny_var = fp.createVariable('Ny', np.int, ('const',))
Ny_var[0] = Ny

output_var = fp.createVariable('output', np.int, ('const',))
output_var[0] = output

Lx_var = fp.createVariable('Lx', 'd', ('const',))
Lx_var[0] = Lx

Ly_var = fp.createVariable('Ly', 'd', ('const',))
Ly_var[0] = Ly

Par_inter_distance = fp.createVariable('par_int', 'd', ('const',))
Par_inter_distance[0] = particle_int_distance

g_var = fp.createVariable('g', 'd', ('const',))
g_var[0] = g

H_var = fp.createVariable('H', 'd', ('y','x'), contiguous=True)
H_var.units = 'm'
H_var[:,:] = H_data

Hmax_var = fp.createVariable('Hmax', 'd', ('const',))
Hmax_var[0] = H0

b1_var = fp.createVariable('b1', 'd', ('y','x'), contiguous=True)
b1_var.units = 'm/s'
b1_var[:,:] = b1_data

b2_var = fp.createVariable('b2', 'd', ('y','x'), contiguous=True)
b2_var.units = 'm/s'
b2_var[:,:] = b2_data

f0_var = fp.createVariable('f', 'd', ('const',))
f0_var[0] = f0

time_var = fp.createVariable('time', 'd', ('const',))
time_var[0] = time

Tf_var = fp.createVariable('Tf', 'd', ('const',))
Tf_var[0] = final_time

plot_interval_var = fp.createVariable('plot_interval', 'd', ('const',))
plot_interval_var[0] = plot_interval

num_particles_var = fp.createVariable('num_particles', np.int, ('const',))
num_particles_var[0] = num_particles

x_part_pos = fp.createVariable('particle_x_position', 'd', ('trajectory',))
x_part_pos[:] = x_part

y_part_pos = fp.createVariable('particle_y_position', 'd', ('trajectory',))
y_part_pos[:] = y_part

# Close the file
fp.close()

