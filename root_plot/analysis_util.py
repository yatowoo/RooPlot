import ROOT

# numerical calculation
def efficiency_simple(nsel, nall):
  if(nall < 1.):
    return (0., 0.)
  eff = float(nsel) / float(nall)
  lowerErrorEff = eff - ROOT.TEfficiency.ClopperPearson(nall, nsel, 0.683, False)
  upperErrorEff = ROOT.TEfficiency.ClopperPearson(nall, nsel, 0.683, True) - eff
  error = (upperErrorEff + lowerErrorEff) / 2.
  return eff, error, lowerErrorEff, upperErrorEff
def show_efficiency(nsel, nall):
  eff, error, lerr, uerr = efficiency_simple(nsel, nall)
  return f'{eff * 100:.1f}^{{+{uerr * 100:.1f}}}_{{-{lerr * 100:.1f}}} %'