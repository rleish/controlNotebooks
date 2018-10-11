import satelliteParamHW8 as P
from PDControl import PDControl

class satelliteController:
    ''' 
        This class inherits other controllers in order to organize multiple controllers.
    '''

    def __init__(self,kp_th=P.kp_th,kd_th=P.kd_th,kp_ph=P.kp_phi,kd_ph=P.kd_phi):
        # Instantiates the SS_ctrl object
        # Allow the user to add other than the default gains
        self.phiCtrl = PDControl(kp_ph, kd_ph, P.theta_max, P.beta, P.Ts)
        self.thetaCtrl = PDControl(kp_th, kd_th, P.tau_max, P.beta, P.Ts)

    def u(self, y_r, y):
        # y_r is the referenced input
        # y is the current state
        phi_r = y_r[0]
        theta = y[0]
        phi = y[1]
        # the reference angle for theta comes from the outer loop PD control
        theta_r = self.phiCtrl.PD(phi_r, phi, flag=False)
        # the torque applied to the base comes from the inner loop PD control
        tau = self.thetaCtrl.PD(theta_r, theta, flag=False)
        return [tau]







