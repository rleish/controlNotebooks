import sys
sys.path.append('..')  # add parent directory
import pendulumParam as P
import matplotlib.pyplot as plt
from control import TransferFunction as tf
import control as cnt
import numpy as np 

P_in = tf([-2/P.m2/P.ell], [1, 0,-2*(P.m1+P.m2)*P.g/P.m2/P.ell])
Plant = P_in

#PLOT = True
PLOT = False

if PLOT: plt.figure(3), plt.clf() #, plt.hold(True)
mag, phase, omega = cnt.bode(Plant, dB=True, omega=np.logspace(-3, 5), Plot=False)
if PLOT: 
    plt.subplot(2, 1, 1), plt.grid(True)
    plantMagPlot, = plt.semilogx(omega, mag, label='Plant')
    plt.subplot(2, 1, 2), plt.grid(True)
    plantPhasePlot, = plt.semilogx(omega, phase, label='Plant')

#########################################
#   Define Design Specifications
#########################################

#----------- noise specification --------
omega_n = 200    # attenuate noise above this frequency
gamma_n = 0.1    # attenuate noise by this amount
w = np.logspace(np.log10(omega_n), np.log10(omega_n)+2)
if PLOT:
    plt.subplot(211)
    noisePlot, = plt.plot(w, (20*np.log10(gamma_n))*np.ones(len(w)), color='g', label='noise spec')


#########################################
#   Control Design
#########################################

C = tf([1], [1])

# Proportional control: correct for negative sign in plant 
K = tf([-1], [1])
C = C*K

#  phase lead: increase PM (stability)
w_max = 25 #location of maximum frequency bump (desired crossover)
phi_max = 60*np.pi/180
M = (1 + np.sin(phi_max))/(1 - np.sin(phi_max))  # lead ratio
z = w_max/np.sqrt(M)
p = w_max*np.sqrt(M)
Lead = tf([1/z, 1], [1/p, 1])
C = C*Lead

# find gain to set crossover at w_max = 25 rad/s
mag, phase, omega = cnt.bode(Plant*C, dB=False, omega=[w_max], Plot=False)
K = tf([1/mag.item(0)], [1])
C = K*C

############################################
#  Create Plots
############################################
# Open-loop transfer function
OPEN = Plant*C
# Closed loop transfer function from R to Y
CLOSED_R_to_Y = (Plant*C/(1.0+Plant*C))
# Closed loop transfer function from R to U
CLOSED_R_to_U = (C/(1.0+Plant*C))

mag, phase, omega = cnt.bode(OPEN, omega=np.logspace(-3, 5), dB=True, Plot=False)
if PLOT: 
    openMagPlot, = plt.semilogx(omega,mag, color='r', label='OPEN')
    plt.subplot(212)
    openPhasePlot, = plt.semilogx(omega,phase, color='r', label='OPEN')
    plt.legend(handles=[plantMagPlot, noisePlot, openMagPlot])
    plt.pause(0.0001)  # the pause causes the figure to be displayed during the simulation

if PLOT:
    plt.figure(4), plt.clf()

    plt.subplot(311),  plt.grid(True)
    mag, phase, omega = cnt.bode(CLOSED_R_to_Y, dB=True, Plot=False)
    plt.semilogx(omega, mag, color='b')
    plt.title('Close Loop Bode Plot')

    plt.subplot(312), plt.grid(True)
    T = np.linspace(0, 2, 100)
    T, yout = cnt.step_response(CLOSED_R_to_Y, T)
    plt.plot(T, yout, color='b')
    plt.title('Close Loop Step Response')

    plt.subplot(313), plt.grid(True)
    T = np.linspace(0, 2, 100)
    T, yout = cnt.step_response(CLOSED_R_to_U, T)
    plt.plot(T, yout, color='b')
    plt.title('Control Effort for Step Response')

if PLOT:
    # Keeps the program from closing until the user presses a button.
    print('Press key to close')
    plt.waitforbuttonpress()
    plt.close()

##############################################
#  Convert Controller to State Space Equations
##############################################
C_ss = cnt.tf2ss(C)  # convert to state space

########################################################################
#  Convert Controller to discrete transfer functions for implementation
########################################################################
C_in_d = tf.sample(C, P.Ts, method='bilinear') #bilinear: Tustin's approximation ("generalized bilinear transformation" with alpha=0.5)

