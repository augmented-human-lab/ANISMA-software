import numpy as np

def predictForceSeries(coeffs, time):
    """
    Returns the prediction for the input variables x with the coefficients coeff.
    """
    a, b, c, k = coeffs

    x = np.log(time)

    return (a / (1+np.exp(-k*(x-c))) + b)
    # a: scale Y
    # b: translate Y
    # c: translate X
    # k: scale X
    # d: helper var that scales a and k simulataneously, a and k can run away too quick,
    #    therefore it helps the solver to find a best fit more easily

def predictForce(coeffs, time, sigmoid_coeffs):
    a,b = coeffs
    return predictForceSeries(sigmoid_coeffs, time*a)*b

def predictTimeSeries(coeffs, force):
    """
    Returns the prediction for the input variables x with the coefficients coeff.
    """
    a, b, c, k = coeffs

    return np.exp((-np.log(   a    / (force - b) - 1)) / k + c)
    # a: scale Y
    # b: translate Y
    # c: translate X
    # k: scale X
    # d: helper var that scales a and k simulataneously, a and k can run away too quick,
    #    therefore it helps the solver to find a best fit more easily

def predictTime(coeffs, force, sigmoid_coeffs):
    a,b = coeffs
    return predictTimeSeries(sigmoid_coeffs, force/b)/a

def predictParameter(coeffs, x):
    """
    Returns the prediction for the input variables x with the coefficients coeff.
    """
    a, b, c = coeffs

    return a + b*x + c*np.square(x)

def getSMAType(smaparams):
    if smaparams.getSpringDiameter() == 1.37:
        return "small"
    elif smaparams.getSpringDiameter() == 2.54:
        return "medium"
    else:
        return "unknown"

def getCoeffs(cool, smaparams):
    coeffsXScale = None
    coeffsYScale = None
    sigmoid_coeffs = None

    type = getSMAType(smaparams)
    if type == 'small':
        if cool:
            sigmoid_coeffs = np.array([-140.38223839,133.43249016,8.11882811,1.8858472 ])

            coeffsXScale = np.array([ 0.01087817,0.02710073,-0.00014913])
            coeffsYScale = np.array([5.16990431e-25,7.49442660e-03,-2.63985909e-13])
        else:
            sigmoid_coeffs = np.array([149.20719444,1.35288842,6.91375312,3.1908039])

            coeffsXScale = np.array([ 3.11188316e-04,-1.71103714e-02,2.05509842e+00])
            coeffsYScale = np.array([-5.99638234e-04,2.14375976e+00,-1.00211766e+00])
    elif type == "medium":
        if cool:
            sigmoid_coeffs = np.array([-210.58281991,  185.28446348,    8.42794064,    1.55897648])

            coeffsXScale = np.array([1.01499185e-02,7.57730344e-03, -1.35707812e-05])
            coeffsYScale = np.array([-5.36717340e-18,  5.39710661e-03, -3.88526416e-14])
        else:
            sigmoid_coeffs = np.array([863.78201464,  12.28246271,   8.45746089,   2.44565316])

            coeffsXScale = np.array([ 4.39908149e-05, 1.41559497e-01, 4.07317068e-01])
            coeffsYScale = np.array([-0.00048127,  0.15858345,  0.41632824])

    return [sigmoid_coeffs, coeffsXScale, coeffsYScale]

def getForce(actuationTime, power, smaparams):
    # hardcoded coefficients to predict the parameters to derive the corresponding
    # force by time function
    sigmoid_coeffs, coeffsXScale, coeffsYScale = getCoeffs(False, smaparams)

    a = predictParameter(coeffsXScale, power)# a: scale X
    b = predictParameter(coeffsYScale, power) # b: scale Y

    return predictForce([a,b], actuationTime, sigmoid_coeffs)

def getRelaxForce(relaxtime, actuationTime, power, smaparams):
    sigmoid_coeffs, coeffsXScale, coeffsYScale = getCoeffs(True, smaparams)

    force = getForce(actuationTime, power, smaparams)
    a = predictParameter(coeffsXScale, force)# a: scale X
    b = predictParameter(coeffsYScale, force) # b: scale Y

    return predictForce([1,b], relaxtime, sigmoid_coeffs)

def getTime(force, power, smaparams):
    # hardcoded coefficients to predict the parameters to derive the corresponding
    # force by time function
    sigmoid_coeffs, coeffsXScale, coeffsYScale = getCoeffs(False, smaparams)

    a = predictParameter(coeffsXScale, power)# a: scale X
    b = predictParameter(coeffsYScale, power) # b: scale Y

    return predictTime([a,b], force, sigmoid_coeffs)

def getRelaxTime(relaxforce, actuationTime, power, smaparams):
    # hardcoded coefficients to predict the parameters to derive the corresponding
    # force by time function
    sigmoid_coeffs, coeffsXScale, coeffsYScale = getCoeffs(True, smaparams)

    force = getForce(actuationTime, power, smaparams)

    # Dont calculate the time if its going to be less anyway
    if force <= relaxforce:
        return 0.0

    a = predictParameter(coeffsXScale, force)# a: scale X
    b = predictParameter(coeffsYScale, force) # b: scale Y

    return predictTime([1,b], relaxforce, sigmoid_coeffs)


def getMaxPower(smaparams):
    type = getSMAType(smaparams)

    if type == "small":
        return 0.7
    elif type == "medium":
        return 1.4

    return 0.7

def getMinPower():
    return 0.0

def getUpperForceLimit(power, smaparams):
    return getForce(20000, power, smaparams)

def getLowerForceLimit(power, smaparams):
    return getForce(0, power, smaparams)

def getAttackTime(power, smaparams):
    upLimit = getUpperForceLimit(power, smaparams)
    lowLimit = getLowerForceLimit(power, smaparams)
    fract = 0.90
    reqForce = lowLimit + (upLimit-lowLimit) * fract
    return getTime(reqForce, power, smaparams)

def getPowerToObtainMaxForce(force, smaparams):
    step = 0.01

    window = getMaxPower(smaparams)-getMinPower()
    for i in range(int(window/step)):
        pwr = getMinPower() + i*step
        if getForce(15000, pwr, smaparams) >= force:
            return pwr

    return 0
