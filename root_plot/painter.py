# ROOT painter for drawing objects in PDF file

# Basic Usage:
# p = Painter()
# p.PrintCover()
# p.DrawHist(h1)
# p.PrintBackCover()

import ROOT
from ROOT import TCanvas, TPaveText
from ROOT import gPad, gStyle

from root_plot.plot_util import *
from root_plot.fit_util import fcn_langaus

def NewCanvas(name="c1_painter", title="New Canvas", winX=1600, winY=1000, **kwargs):
  return TCanvas(name, title, winX,winY)


class Painter:
  """Master of ROOT drawing and plotting
  Output stored in PDF file
  
  Parameters:
    Canvas - name, title, winX, winY, nx, ny
    Gausssian - gausFitRange
  """
  def __init__(self, canvas = None, printer = "out.pdf", **kwargs):
    self.canvas = canvas if canvas is not None else NewCanvas(**kwargs)
       # Output PDF in 1 file
    self.printer = printer if printer.endswith(".pdf") else printer +".pdf"
    self.printAll = kwargs.get('printAll', False)
    self.printDir = kwargs.get('printDir', os.path.dirname(self.printer))
    if(self.printDir == ''): self.printDir = '.'
    self.printExt = kwargs.get('printExt', ['pdf','png'])
    self.saveROOT = kwargs.get('saveROOT', False)
    if self.saveROOT:
      self.rootfile = ROOT.TFile(printer.replace('.pdf','.root'), 'RECREATE')
    # Configuration
    self.subPadNX = kwargs.get('nx', 1)
    self.subPadNY = kwargs.get('ny', 1)
    0.14, 0.02, 0.12, 0.02
    self.marginTop = kwargs.get('marginTop', 0.02)
    self.marginBottom = kwargs.get('marginBottom', 0.12)
    self.marginLeft = kwargs.get('marginLeft', 0.14)
    self.marginRight = kwargs.get('marginRight', 0.02)
    self.showGrid = kwargs.get('showGrid', False)
    self.gridColor = kwargs.get('gridColor', kGray+1)
    ROOT.gStyle.SetGridColor(self.gridColor)
    self.showPageNo = kwargs.get('showPageNo', False)
    # Parameters
    self.GAUS_FIT_RANGE = kwargs['gausFitRange'] if kwargs.get('gausFitRange') else 1 # ratio of FWHM
    # Status
    self.padIndex = 0
    self.pageNo = 0
    self.pageName = "Start"
    self.padEmpty = True
    self.hasCover = False
    self.hasBackCover = False
    self.primaryHist = None
    self.counterSavedObjs = 0
    # Dump
    self.root_objs = []         # Temp storage to avoid GC
  def __del__(self):
    if(self.hasCover and not self.hasBackCover):
      self.PrintBackCover('')
    if self.saveROOT:
      self.rootfile.Close()
      print('[-] ROOT objects saved to ' + self.rootfile.GetName())
      print(f'> save_obj & TObject.Write() calls - {self.counterSavedObjs}')
  def save_obj(self, obj): # ROOT.TObject
    if not self.saveROOT: return
    self.rootfile.cd()
    if type(obj) is list:
      for tobj in obj:
        tobj.Write()
        self.counterSavedObjs += 1
    else:
      obj.Write()
      self.counterSavedObjs += 1
  def new_obj(self, obj):
    self.root_objs.append(obj)
    return self.root_objs[-1]
  def new_legend(self, xlow, ylow, xup, yup):
    lgd = self.new_obj(ROOT.TLegend(xlow, ylow, xup, yup))
    return lgd
  def add_text(self, pave : ROOT.TPaveText, s : str, **textAttr):
    text = pave.AddText(s)
    textAttr['color'] = textAttr.get('color', kBlack)
    textAttr['size'] = textAttr.get('size', 0.04)
    textAttr['font'] = textAttr.get('font', 42)
    textAttr['align'] = textAttr.get('align', 11)
    text.SetTextAlign(textAttr['align'])
    text.SetTextSize(textAttr['size'])
    text.SetTextFont(textAttr['font'])
    text.SetTextColor(textAttr['color'])
    return text
  def draw_text(self, xlow=0.25, ylow=0.4, xup=0.75, yup=0.6, title = '', **textAttr):
    pave = self.new_obj(ROOT.TPaveText(xlow, ylow, xup, yup, "brNDC"))
    pave.SetBorderSize(0)
    pave.SetFillStyle(0) # hollow
    pave.SetFillColor(ROOT.kWhite)
    if(title != ''):
      # Text Attributes
      textAttr['color'] = textAttr.get('color', kBlack)
      textAttr['size'] = textAttr.get('size', 0.05)
      textAttr['font'] = textAttr.get('font', 62)
      textAttr['align'] = textAttr.get('align', 11)
      self.add_text(pave, title, **textAttr)
    return pave
  def ResetCanvas(self):
    self.canvas.Clear()
    if(self.subPadNX * self.subPadNY > 1):
      self.canvas.Divide(self.subPadNX, self.subPadNY)
    self.padEmpty = True
    # Style
    ROOT.gPad.SetMargin(self.marginLeft, self.marginRight, self.marginBottom, self.marginTop)
    ROOT.gPad.SetGrid(self.showGrid, self.showGrid)
  def SetLayout(self, nx, ny):
    self.subPadNX = nx
    self.subPadNY = ny
    self.ResetCanvas()
  def GetLayout(self):
    return (self.subPadNX, self.subPadNY)
  def draw_pageno(self):
    # Left-Bottom corner
    self.draw_text(0.01,0.01,0.05,0.05,f'{self.pageNo}', 
      size=0.03, color=kGray+1, align=12).Draw()
  def PrintCover(self, title = '', isBack = False):
    self.canvas.Clear()
    pTxt = ROOT.TPaveText(0.25,0.4,0.75,0.6, "brNDC")
    if(title == ''):
      if(isBack):
        pTxt.AddText('Thanks for your attention!')
      else:
        pTxt.AddText(self.canvas.GetTitle())
    else:
      pTxt.AddText(title)
    self.canvas.cd()
    self.canvas.Draw()
    pTxt.Draw()
    if(isBack):
      self.canvas.Print(self.printer + ')', 'Title:End')
    else:
      self.draw_pageno()
      text_footnote = {
        'align': 32,
        'color': kGray+1,
        'size': 0.03,
      }
      pave = self.draw_text(0.5, 0, 1.0, 0.15, f'File : {self.printer}', **text_footnote)
      self.add_text(pave, f'Timestamp : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', **text_footnote)
      self.add_text(pave, f'Powered by #bf{{root_plot}}', **text_footnote)
      pave.Draw()
      self.canvas.Print(self.printer + '(', 'Title:Cover')
    pTxt.Delete()
    self.ResetCanvas()
  def PrintBackCover(self, title=''):
    self.PrintCover(title, isBack=True)
  def NextPage(self, title=""):
    # Print
    if self.printAll and not self.padEmpty:
      figureName = title
      if title == '':
        figureName = f'{self.primaryHist.GetName()}_{len(self.root_objs)}'
      figurePath = f'{self.printDir}/{figureName}'
      for ext in self.printExt:
        self.canvas.SaveAs(figurePath + '.' + ext)
    if(title == ""):
      title = self.pageName
    self.pageNo += 1
    if(self.showPageNo):
      self.canvas.cd()
      self.draw_pageno()
    self.canvas.Print(self.printer, f"Title:{title}")
    # New page
    self.padIndex = 0
    self.ResetCanvas()
  def NextPad(self, title=""):
    # Full sub-pads
    if(self.padIndex == self.subPadNX * self.subPadNY):
      self.NextPage()
    self.padIndex = self.padIndex + 1
    self.canvas.cd(self.padIndex)
    self.padEmpty = True
    self.primaryHist = None
    # Style
    ROOT.gPad.SetMargin(self.marginLeft, self.marginRight, self.marginBottom, self.marginTop)
    ROOT.gPad.SetGrid(self.showGrid, self.showGrid)
  def NextRow(self):
    while(self.padIndex % self.subPadNX != 0):
      self.NextPad()
  # Painter Objects
  def draw_band(self, xmin, xmax, color = kGray+1, style=3002, **kwargs):
    """Draw a rectangular band by TGraph
    Default: vertical gray band crossing the frame
    """
    grshade = self.new_obj(ROOT.TGraph(4))
    ROOT.gPad.Update()
    ymin = kwargs.get('ymin', ROOT.gPad.GetUymin())
    ymax = kwargs.get('ymax', ROOT.gPad.GetUymax())
    grshade.SetPoint(0, xmin, ymax)
    grshade.SetPoint(1, xmax, ymax)
    grshade.SetPoint(2, xmax, ymin)
    grshade.SetPoint(3, xmin, ymin)
    grshade.SetFillColor(color)
    grshade.SetFillStyle(style)
    grshade.SetLineColor(0)
    grshade.SetLineWidth(0)
    grshade.SetMarkerColor(0)
    grshade.SetMarkerSize(0)
    grshade.SetDrawOption('F')
    grshade.Draw('same F')
    return grshade
  # Drawing - Histograms
  def set_hist_palette(self, hist : ROOT.TH2, width=0.05):
    palette = hist.GetListOfFunctions().FindObject("palette")
    totalWidth = width + 0.05 + 0.05 # palette, label, title
    # Pad
    ROOT.gPad.SetRightMargin(totalWidth + self.marginRight)
    # Palette
    palette.SetX1NDC(1. - totalWidth)
    palette.SetX2NDC(1. - totalWidth + width)
    palette.SetY1NDC(self.marginBottom)
    palette.SetY2NDC(1. - self.marginTop)
    return palette
  def hist_rebin(self, hist, binning):
    """binning: width, min, max
    """
    binwidth = binning[0]
    valmin = binning[1]
    valmax = binning[2]
    nbingroup = int ( binwidth // hist.GetBinWidth(1))
    hist.Rebin(nbingroup)
    hist.GetXaxis().SetRangeUser(valmin, valmax)
  def new_hist(self, name, title, binning):
    """binning: width, min, max
    """
    binwidth = binning[0]
    valmin = binning[1]
    valmax = binning[2]
    nbins = int( (valmax - valmin) // binwidth)
    return self.new_obj(ROOT.TH1F(name, title, nbins, valmin, valmax))
  def draw_hist_text(self, hist, **textAttr):
    """Plot bin content as text for ROOT.TH2
    """
    xlower = ROOT.gPad.GetLeftMargin()
    xupper = 1 - ROOT.gPad.GetRightMargin()
    ylower = ROOT.gPad.GetBottomMargin()
    yupper = 1 - ROOT.gPad.GetTopMargin()
    wx = (xupper - xlower) / hist.GetNbinsX()
    wy = (yupper - ylower) / hist.GetNbinsY()
    # Text attributes
    textAttr['color'] = textAttr.get('color', kBlack)
    textAttr['size'] = textAttr.get('size', 0.06)
    textAttr['font'] = textAttr.get('font', 62)
    textAttr['align'] = textAttr.get('color', 22)
    for iy in range(hist.GetNbinsY()):
      for ix in range(hist.GetNbinsX()):
        val = hist.GetBinContent(ix + 1, iy +1)
        pave = self.draw_text(ix * wx + xlower, iy * wy + ylower, (ix+1) * wx + xlower, (iy+1)*wx + xlower)
        self.add_text(pave,f'{val:.3f}', **textAttr)
        pave.Draw('same')
  # Calculation
  def normalise_profile_y(self, hist):
    for ix in range(1,hist.GetNbinsX()+1):
      hpfx = hist.ProjectionY(f'_py_{ix}', ix, ix)
      norm = hpfx.GetMaximum()
      if norm < 1: continue
      for iy in range(1,hist.GetNbinsY()+1):
        raw = hist.GetBinContent(ix, iy)
        hist.SetBinContent(ix, iy, 1. * raw / norm)
      hpfx.Delete()
    return None
  def estimate_fwhm(self, hist):
    """Calculate FWHM and center for TH1D
    """
    peak = hist.GetMaximum()
    rms = hist.GetRMS()
    mean = hist.GetMean()
    halfLeft = hist.FindFirstBinAbove(peak/2.)
    halfRight = hist.FindLastBinAbove(peak/2.)
    center = 0.5 * (hist.GetBinCenter(halfRight) + hist.GetBinCenter(halfLeft))
    fwhm = hist.GetBinCenter(halfRight) - hist.GetBinCenter(halfLeft)
    if fwhm < 2 * hist.GetBinWidth(1):
      print(f'[X] Warning  - Histogram {hist.GetName()} - FWHM too narrow {center = :.2e}, {fwhm = :.2e}, {rms = :.2e}, {peak = :.2e}')
      return rms, mean
    return fwhm, center
  # Fitting -> Fitter?
  def optimise_hist_langau(self, hist, scale=1, **kwargs):
    """Adaptive fitter for Landau-Gaussian distribution
    """
    # Parameters
    N_PARS = 4
    fwhm, center = self.estimate_fwhm(hist)
    fitRange = kwargs.get('fitRange')
    if(not fitRange): fitRange = [0.3*hist.GetMean(), 1.5*hist.GetMean()]
    area = hist.Integral()
    pars = [
      [fwhm * 0.1, fwhm * 0., fwhm * 1],
      [center, center * 0.5, center * 2],
      [10 * area, area * 5, area * 100],
      [fwhm * 0.1, fwhm * 0., fwhm * 1],
    ]
    # Fitter
    langaufun = None
    try:
      langaufun = getattr(ROOT, 'langaufun')
    except AttributeError:
      script_path = os.path.dirname( os.path.realpath(__file__) )
      macroPath = script_path + '/langaus.C'
      if os.path.exists(macroPath):
        # C macro, faster than python implementation
        ROOT.gInterpreter.ProcessLine(f'#include "{macroPath}"')
        langaufun = ROOT.langaufun
      else:
        # python internel implementation
        langaufun = fcn_langaus
    fcnName = f'fitLangaus_{hist.GetName()}_{len(self.root_objs)}'
    fcnfit = self.new_obj(ROOT.TF1(fcnName, langaufun, fitRange[0], fitRange[1], N_PARS))
    startvals = [par[0] for par in pars]
    parlimitslo = [par[1] for par in pars]
    parlimitshi = [par[2] for par in pars]
    fcnfit.SetParameters(array('d', startvals))
    fcnfit.SetParNames("Width","MP","Area","GSigma")
    for i in range(N_PARS):
      fcnfit.SetParLimits(i, parlimitslo[i], parlimitshi[i])
    resultPtr = hist.Fit(fcnName, 'RB0SQN')
    try:
      params = resultPtr.GetParams()
    except ReferenceError:
      self.draw_text(0.50, 0.55, 0.80, 0.85, 'Langau fitting FAILED').Draw('same')
      print(f'[X] Warning  - {hist.GetName()} - Langau fitting FAILED')
      return None
    fiterrs = array('d',[0.] * N_PARS)
    fiterrs = fcnfit.GetParErrors()
    # Draw
    fcnfit.SetRange(hist.GetXaxis().GetXmin(), hist.GetXaxis().GetXmax())
    if(kwargs.get('color')):
      fcnfit.SetLineColor(kwargs['color'])
    if(kwargs.get('style')):
      fcnfit.SetLineStyle(kwargs['style'])
    if(kwargs.get('width')):
      fcnfit.SetLineWidth(kwargs['width'])
    fcnfit.Draw('lsame')
    if(kwargs.get('notext')):
      return fcnfit, resultPtr
    pave = self.draw_text(0.58, 0.55, 0.85, 0.85,title='Landau-Gaussian')
    self.add_text(pave, f'#chi^{{2}} / NDF = {resultPtr.Chi2():.1f} / {resultPtr.Ndf()}')
    self.add_text(pave, f'Mean = {hist.GetMean():.2e}')
    for ipar in range(N_PARS):
      self.add_text(pave, f'{fcnfit.GetParName(ipar)} = {params[ipar]:.2e}')
    pave.Draw('same')
    return fcnfit, resultPtr
  def optimise_hist_gaus(self, hist, scale=1, **kwargs):
    peak = hist.GetMaximum()
    mean = hist.GetMean()
    rms = hist.GetRMS()
    halfLeft = hist.FindFirstBinAbove(peak/2.)
    halfRight = hist.FindLastBinAbove(peak/2.)
    center = 0.5 * (hist.GetBinCenter(halfRight) + hist.GetBinCenter(halfLeft))
    fwhm = hist.GetBinCenter(halfRight) - hist.GetBinCenter(halfLeft)
    if fwhm < 2 * hist.GetBinWidth(1):
      print(f'[X] Warning  - FWHM too narrow {center = }, {fwhm = }, {rms = }, {peak = }')
      return None
    fitRange = min(5 * rms, self.GAUS_FIT_RANGE * fwhm)
    fcnGaus = self.new_obj(
      ROOT.TF1(f'fcnFitGaus_{hist.GetName()}_{len(self.root_objs)}',
      'gaus', center - fitRange, center + fitRange))
    resultPtr = hist.Fit(fcnGaus,'SQN','', center - fitRange, center + fitRange)
    try:
      params = resultPtr.GetParams()
    except ReferenceError:
      print(f'[X] Warning  - Fitting failed with {center = }, {fwhm = }, {rms = }, {peak = }')
      return None
    mean = params[1]
    sigma = params[2]
    fcnGaus.SetRange(mean - 5 * sigma, mean + 5 * sigma)
    fcnGaus.Draw('same')
    drawRange = min(15 * rms, 10 * params[2])
    hist.GetXaxis().SetRangeUser(center - drawRange, center + drawRange)
    if(kwargs.get('color')):
      fcnGaus.SetLineColor(kwargs['color'])
    if(kwargs.get('style')):
      fcnGaus.SetLineStyle(kwargs['style'])
    if(kwargs.get('width')):
      fcnGaus.SetLineWidth(kwargs['width'])
    fcnGaus.Draw('lsame')
    if(kwargs.get('notext')):
      return fcnGaus, resultPtr
    # Draw info
    pave = self.new_obj(ROOT.TPaveText(0.18, 0.55, 0.45, 0.85,'NDC'))
    pave.SetFillColor(ROOT.kWhite)
    self.add_text(pave, f'mean (#mu) = {params[1] * scale:.1f}')
    self.add_text(pave, f'#sigma = {params[2] * scale:.1f}')
    self.add_text(pave, f'#chi^{{2}} / NDF = {resultPtr.Chi2():.1f} / {resultPtr.Ndf()}')
    self.add_text(pave, f'RMS = {rms * scale:.1f}')
    self.add_text(pave, f'FWHM = {fwhm * scale:.1f}')
    pave.Draw('same')
    return resultPtr
  def DrawHist(self, htmp, title="", option="", optStat=False, samePad=False, optGaus=False, scale=1, **kwargs):
    ROOT.gStyle.SetOptStat(optStat)
    if(title == ""):
      title = htmp.GetTitle()
    if(not samePad):
      self.NextPad(title)
    elif not self.padEmpty:
      option = f'{option}same'
    else:
      self.primaryHist = htmp
    print("[+] DEBUG - Pad " + str(self.padIndex) + ' : ' + htmp.GetName())
    if kwargs.get('optNormY') == True:
      self.normalise_profile_y(htmp)
    htmp.Draw(option)
    self.padEmpty = False
    # Style
    if(option == "colz"):
      zmax = htmp.GetBinContent(htmp.GetMaximumBin())
      htmp.GetZaxis().SetRangeUser(0.0 * zmax, 1.1 * zmax)
    if(htmp.ClassName().startswith('TH') and self.subPadNX * self.subPadNY >= 4):
      htmp.SetTitleSize(0.08, "XY")
      htmp.SetTitleOffset(0.8, "XY")
    if(optGaus): self.optimise_hist_gaus(htmp, scale)
    if(kwargs.get('optLangau') == True):
      self.optimise_hist_langau(htmp, scale)
    ROOT.gPad.SetLogx(kwargs.get('optLogX') == True)
    ROOT.gPad.SetLogy(kwargs.get('optLogY') == True)
    ROOT.gPad.SetLogz(kwargs.get('optLogZ') == True)
