from ROOT import TMath

# Functions
def fcn_moyal(x : list, par : list):
  """Moyal Distribution
  Approximation for Landau distribution
  Reference:

  Parameter
    par[0]=mean
    par[1]=sigma
  """
  mean = par[0]
  sigma = par[1]
  t = (x[0] - mean) / sigma
  invsq2pi = 0.3989422804014
  expPseudo = -0.5 * (TMath.Exp(-t) + t)
  return invsq2pi / sigma * (TMath.Exp( expPseudo ))
  
def fcn_langaus(x : list, par : list):
  """Convoluted Landau and Gaussian Fitting Function

  Reference: https://root.cern/doc/master/langaus_8C.html

  Parameter
    par[0]=Width (scale) parameter of Landau density
    par[1]=Most Probable (MP, location) parameter of Landau density
    par[2]=Total area (integral -inf to inf, normalization constant)
    par[3]=Width (sigma) of convoluted Gaussian function
  """
  invsq2pi = 0.3989422804014  # (2 pi)^(-1/2)
  mpshift  = -0.22278298   # Landau maximum location
  np = 100.0 # number of convolution steps
  sc =   5.0 # convolution extends to +-sc Gaussian sigmas
  xx, mpc, fland, sum = 0., 0., 0., 0.
  xlow, xupp, step = 0., 0., 0.
  x[0] = x[0]
  for i in range(4):
    par[i] = par[i]
  mpc = par[1] - mpshift * par[0]
  xlow = x[0] - sc * par[3]
  xupp = x[0] + sc * par[3]
  step = (xupp-xlow) / np
  # Convolution integral of Landau and Gaussian by sum
  for i in range(1,int(np//2+1)):
    xx = xlow + (i - .5) * step
    fland = TMath.Landau(xx, mpc, par[0]) / par[0]
    sum += fland * TMath.Gaus(x[0], xx, par[3])
    xx = xupp - (i-.5) * step
    fland = TMath.Landau(xx, mpc, par[0]) / par[0]
    sum += fland * TMath.Gaus(x[0], xx, par[3])
  return float(par[2] * step * sum * invsq2pi / par[3])
