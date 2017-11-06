import os
import json
import logging
import logging.config
from modules.utils import setup_logging, getLabel

def efficiencies(loglev, doMC, doData, doCSV, doDeepCSV, CSVWPs, DeepCSVWPs):
    import ROOT

    import modules.classes
    import modules.effPlots
    
    setup_logging(loglevel = loglev, logname = "efficiencyoutput", errname = "efficiencyerror")

    logger = logging.getLogger(__name__)

    logger.info("Starting shape comparison")


    
    if not (doMC or doData):
        if __name__ == "__main__":
            logging.warning("At least on of the flags --mc and --data should to be set")
            logging.warning("Falling back the only mc")
        else:
            logging.warning("At least on of the paramters doMC and doData should to be set")
            logging.warning("Falling back the only mc")
        doMC = True

            
    if loglev > 0:
        ROOT.gErrorIgnoreLevel = ROOT.kError# kPrint, kInfo, kWarning, kError, kBreak, kSysError, kFatal;

    basepaths = "effv3/"
        
    MCInput = "/mnt/t3nfs01/data01/shome/koschwei/scratch/HLTBTagging/DiLepton_v2/ttbar/ttbar_v2.root"
    DataInput = "/mnt/t3nfs01/data01/shome/koschwei/scratch/HLTBTagging/DiLepton_v2/MuonEG/MuonEG_v2.root"

    MCSelection = "1"
    VarSelection = "1"
    TriggerSelection = "HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_v4 > 0 || HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v4 > 0"
    LeptonSelection = "Sum$((abs(offTightElectrons_superClusterEta) <= 1.4442 || abs(offTightElectrons_superClusterEta) >= 1.5660) && offTightElectrons_pt > 30 && abs(offTightElectrons_eta) < 2.4) > 0 && Sum$(offTightMuons_iso < 0.25 && offTightMuons_pt > 20 && abs(offTightMuons_eta) < 2.4) > 0"


    logging.info("Using: doMC: {0} | doData: {1} | doCSV: {2} | doDeepCSV: {3}".format(doMC, doData, doCSV, doDeepCSV))


    offlineSelection = "Sum$(offJets_pt > 30 && abs(offJets_eta) < 2.4) > 2"

    samples = []
    if doMC:
        eventSelection = "({0}) && ({1}) && ({2}) && ({3})".format(VarSelection, TriggerSelection, LeptonSelection, MCSelection)
        samples.append( (modules.classes.Sample("ttbar", MCInput, eventSelection, 831.76, 4591.622871124, ROOT.kRed, 9937324, legendText = "Dataset: t#bar{t}"), "MC", getLabel("Dataset: t#bar{t}", 0.7)) )
    if doData:
        eventSelection = "({0}) && ({1}) && ({2})".format(VarSelection, TriggerSelection, LeptonSelection)
        samples.append( (modules.classes.Sample("data", DataInput, eventSelection, legendText = "Dataset: MuonEG"),"MuonEG", getLabel("Dataset: MuonEG", 0.7)) )

    CSVSelWP = "0.9535"
    DeepCSVSelWP = "0.8958"
    

    WPColors = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen+2, ROOT.kPink+7, ROOT.kViolet, ROOT.kCyan]
    
    CSVSelection = "Sum$(offJets_csv > {0}) >= 1".format(CSVSelWP)
    DeepCSVSelection = "Sum$(offJets_deepcsv > {0}) >= 1".format(DeepCSVSelWP)

    refbyCSVRank = { 0 : "offJets_ileadingCSV",
                     1 : "offJets_isecondCSV",
                     2 : "offJets_ithirdCSV",
                     3 : "offJets_ifourthCSV"}

    refbyDeepCSVRank = { 0 : "offJets_ileadingDeepCSV",
                         1 : "offJets_isecondDeepCSV",
                         2 : "offJets_ithirdDeepCSV",
                         3 : "offJets_ifourthDeepCSV"}

    if doCSV:
        logging.info("Processing plots for CSV")
        CSVPlotBaseObjs = {}

        for WP in CSVWPs:
            WPLabel = getLabel("PF WP: {0}".format(WP), 0.7, "under")
            logging.info("Using WP: {0}".format(WP))
            for i in range(3):
                JetSelection = "offJets_csv[{0}] >= 0 && abs(offJets_eta[{0}]) < 2.4 && offJets_pt[{0}] > 30 && offJets_passesTightLeptVetoID[{0}] > 0".format(refbyCSVRank[i])
                logging.info("Making effciency for Jet {0} ordered by CSV".format(i))
                CSVPlotBaseObjs[i] = modules.classes.PlotBase("offJets_csv[{0}]".format(refbyCSVRank[i]),
                                                              "{0} && {1} && ({2})".format(CSVSelection, offlineSelection, JetSelection),
                                                              "1",
                                                              [20,0,1],
                                                              modules.utils.getAxisTitle("csv", i, "csv"),
                                                              LegendPosition = [0.1,0.6,0.4,0.76])




                CSVPlotBaseObjs[i].color = WPColors[i]
                onlysamples = []

                for sampleStuff in samples:
                    sample, name, label = sampleStuff
                    onlysamples.append(sample)
                    if not (doMC and doData):
                        modules.effPlots.makeEffPlot(CSVPlotBaseObjs[i], sample, "Sum$(pfJets_csv >= {0} && pfJets_matchOff >= 0 && pfJets_matchOff == {1}) > 0)".format(WP, refbyCSVRank[i]),
                                                     basepaths+"Eff_{2}_Jet{0}_pfWP_{1}_CSV".format(i, WP, name), label = [label,WPLabel])

                if doMC and doData:
                    modules.effPlots.makeEffSCompPlot(CSVPlotBaseObjs[i], onlysamples, "Sum$(pfJets_csv >= {0} && pfJets_matchOff >= 0 && pfJets_matchOff == {1}) > 0".format(WP, refbyCSVRank[i]),
                                                      basepaths+"Eff_DataMC_Jet{0}_pfWP_{1}_CSV".format(i, WP), label = WPLabel)
            
            
    if doDeepCSV:
        logging.info("Processing plots for DeepCSV")
        DeepCSVPlotBaseObjs = {} 


        for WP in DeepCSVWPs:
            WPLabel = getLabel("PF WP: {0}".format(WP), 0.7, "under")
            logging.info("Using WP: {0}".format(WP))
            for i in range(3):
                JetSelection = "offJets_deepcsv[{0}] >= 0 && abs(offJets_eta[{0}]) < 2.4 && offJets_pt[{0}] > 30 && offJets_passesTightLeptVetoID[{0}] > 0".format(refbyCSVRank[i])
                logging.info("Making effciency for Jet {0} ordered by DeepCSV".format(i))
                DeepCSVPlotBaseObjs[i] = modules.classes.PlotBase("Sum$(offJets_deepcsv[{0}] + offJets_deepcsv_bb[{0}])".format(refbyDeepCSVRank[i]),
                                                                  "{0} && {1} && ({2})".format(DeepCSVSelection, offlineSelection, JetSelection),
                                                                  "1",
                                                                  [20,0,1],
                                                                  modules.utils.getAxisTitle("deepcsv", i, "deepcsv"),
                                                                  LegendPosition = [0.1,0.6,0.4,0.76])




                DeepCSVPlotBaseObjs[i].color = WPColors[i]
                onlysamples = []
                for sampleStuff in samples:
                    sample, name, label = sampleStuff
                    onlysamples.append(sample)
                    if not (doMC and doData): 
                        modules.effPlots.makeEffPlot(DeepCSVPlotBaseObjs[i], sample, "Sum$(pfJets_deepcsv >= {0} && pfJets_matchOff >= 0 && pfJets_matchOff == {1}) > 0".format(WP, refbyDeepCSVRank[i]),
                                                     basepaths+"Eff_{2}_Jet{0}_pfWP_{1}_DeepCSV".format(i, WP, name), label = [label,WPLabel])

                if doMC and doData:
                    modules.effPlots.makeEffSCompPlot(DeepCSVPlotBaseObjs[i], onlysamples, "Sum$(pfJets_deepcsv >= {0} && pfJets_matchOff >= 0 && pfJets_matchOff == {1}) > 0".format(WP, refbyDeepCSVRank[i]),
                                                      basepaths+"Eff_DataMC_Jet{0}_pfWP_{1}_DeepCSV".format(i, WP), label = WPLabel)



    

if __name__ == "__main__":
    import argparse
    ##############################################################################################################
    ##############################################################################################################
    # Argument parser definitions:
    argumentparser = argparse.ArgumentParser(
        description='Description'
    )

    argumentparser.add_argument(
        "--logging",
        action = "store",
        help = "Define logging level: CRITICAL - 50, ERROR - 40, WARNING - 30, INFO - 20, DEBUG - 10, NOTSET - 0 \nSet to 0 to activate ROOT root messages",
        type=int,
        default=20
    )

    argumentparser.add_argument(
        "--mc",
        action = "store_true",
        help = "Call without argument!",
    )
    argumentparser.add_argument(
        "--data",
        action = "store_true",
        help = "Call without argument!",
    )
    argumentparser.add_argument(
        "--CSV",
        action = "store_true",
        help = "Call without argument!",
    )
    argumentparser.add_argument(
        "--deepCSV",
        action = "store_true",
        help = "Call without argument!",
    )
    argumentparser.add_argument(
        "--CSVWP",
        action = "store",
        help = "CSV WPs that are plotted",
        nargs='+',
        type=str,
        default = ["0.8484"]
    )
    argumentparser.add_argument(
        "--DeepCSVWP",
        action = "store",
        help = "DeepCSV WPs that are plotted",
        nargs='+',
        type=str,
        default = ["0.6324"]
    )
    
    args = argumentparser.parse_args()
    #
    ##############################################################################################################
    ##############################################################################################################

        
    efficiencies(loglev = args.logging, doMC = args.mc, doData = args.data, doCSV = args.CSV, doDeepCSV = args.deepCSV, CSVWPs = args.CSVWP, DeepCSVWPs = args.DeepCSVWP)

    logging.info("Exiting efficiencies.py")