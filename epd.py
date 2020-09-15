#!/usr/bin/env python3

import sys, os
import ROOT
import ana_util

# Plot UI curve
ana_util.ALICEStyle()

# Working path : INPUT from command-line
dataPath = sys.argv[1]

UI = [ [0 for col in range(16)] for row in range(61)]

DRAW_FLAG = False
DEBUG_FLAG = False

if(DRAW_FLAG):
  c = ROOT.TCanvas('cUI', 'SiPM UI curve', 1280, 800)
  c.SetMargin(0.15, 0.02, 0.15, 0.02)
  c.Draw()

fout = ROOT.TFile(dataPath + '/UI-count.root','RECREATE')
hIstart = ROOT.TH1F('hImin','Minimum/Baseline current;I_{start} (Unit: #muA);N_{SiPM}',10, -0.005,0.095)
hIop = ROOT.TH1F('hIop','2nd Minimum/Working current;I_{op} (Unit: #muA);N_{SiPM}',10, -0.005,0.095)
hVmin = ROOT.TH1F('hVmin','Minmum voltage with value of Iop;U_{min} (Unit: V);N_{SiPM}', 30,50,65)
hVavg = ROOT.TH1F('hVavg','Average voltage with value of Iop;U_{min} (Unit: V);N_{SiPM}', 30,50,65)
hVmax = ROOT.TH1F('hVmax','Maximum voltage with value of Iop;U_{min} (Unit: V);N_{SiPM}', 30,50,65)

def CalcVop(ui):
  Istart = ui.GetPointY(0) # min. value (=0.02)
  Iop = Istart # second min. current
  for i in range(0,ui.GetN()):
    Inow = ui.GetPointY(i)
    if(Inow <= Istart):
      continue
    if(Iop == Istart):
      Iop = Inow
      Vmin = ui.GetPointX(i-1)
    if(Inow > Iop):
      Vmax = ui.GetPointX(i-1)
      break
  print("%.2f\t%.2f\t%.1f\t%.1f\t%.1f" % (Istart, Iop, Vmin, (Vmin+Vmax)/2., Vmax))
  hIstart.Fill(Istart)
  hIop.Fill(Iop)
  hVmin.Fill(Vmin)
  hVavg.Fill((Vmin+Vmax)/2.)
  hVmax.Fill(Vmax)

for nBoard in range(1,61):
  if(DEBUG_FLAG):
    print('[-] Processing board ' + repr(nBoard) + ' / 60')
  if(DRAW_FLAG):
    c.Clear()
    mg = ROOT.TMultiGraph()
    mg.SetTitle('UI curve measured by FEE board;U_{op} (Unit: V);I (Unit: #muA)')
    lgd = ROOT.TLegend(0.2, 0.6, 0.6, 0.9)
    lgd.SetBorderSize(0)
    lgd.SetNColumns(4)
    ana_util.COLOR = ana_util.SelectColor()
    ana_util.MARKER = ana_util.SelectMarker()
  for nCh in range(0,16):
    f = ROOT.TFile(dataPath + '/Board%d/SiPM%d.root' % (nBoard, nCh))
    if(not f.IsOpen()):
      print('[X] Missing Board %d SiPM %d' % (nBoard, nCh))
      continue
    ui = f.Get('UI_S%dC%d' % (nBoard,nCh))
    if(not ui):
      print('[X] Missing Board %d SiPM %d' % (nBoard, nCh))
      continue
    else:
      if(DEBUG_FLAG):
        print('----> SiPM ' + repr(nCh+1) + ' / 16')
      UI[nBoard][nCh] = ui.Clone('B%dC%d' % (nBoard,nCh))
    f.Close()
    ui = UI[nBoard][nCh]
    CalcVop(ui)
    if(not DRAW_FLAG):
      continue
    ana_util.SetColorAndStyle(ui)
    ui.GetListOfFunctions().At(0).Delete()
    if(ui.FindObject('stats')):
      ui.FindObject('stats').Delete()
    lgd.AddEntry(ui, ui.GetName(),'lp')
    mg.Add(ui, 'LP')
  if(DRAW_FLAG):
    c.Clear()
    mg.Draw('a')
    mg.GetYaxis().SetRangeUser(0,0.5)
    lgd.Draw('same')
    ana_util.PrintFigure(dataPath + '/UI_Board' + repr(nBoard))

fout.cd()
hIstart.Write()
hIop.Write()
hVmin.Write()
hVavg.Write()
hVmax.Write()
fout.Close()