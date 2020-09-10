#!/usr/bin/env python3

import sys, os
import ROOT
import ana_util

# Plot UI curve
ana_util.ALICEStyle()

# Working path : INPUT from command-line
dataPath = sys.argv[1]

UI = [ [0 for col in range(16)] for row in range(61)]

c = ROOT.TCanvas('cUI', 'SiPM UI curve', 1280, 800)
c.SetMargin(0.15, 0.02, 0.15, 0.02)
c.Draw()

for nBoard in range(1,61):
  print('[-] Processing board ' + repr(nBoard) + ' / 60')
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
      print('----> SiPM ' + repr(nCh+1) + ' / 16')
      UI[nBoard][nCh] = ui.Clone('B%dC%d' % (nBoard,nCh))
    f.Close()
    ui = UI[nBoard][nCh]
    ana_util.SetColorAndStyle(ui)
    ui.GetListOfFunctions().At(0).Delete()
    if(ui.FindObject('stats')):
      ui.FindObject('stats').Delete()
    lgd.AddEntry(ui, ui.GetName(),'lp')
    mg.Add(ui, 'LP')
  c.Clear()
  mg.Draw('a')
  mg.GetYaxis().SetRangeUser(0,0.5)
  lgd.Draw('same')
  ana_util.PrintFigure(dataPath + '/UI_Board' + repr(nBoard))