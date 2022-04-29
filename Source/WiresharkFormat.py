
import ExcelHandler
import UtilsLib

print_console = False

bandCombinationList = []
bcUplinkList = []
layersList = []
bcsList = []
bandsList = []
modulationList = []


def parseSupportedBandsV9WiresharkFormat(lines):
    bandListV9 = []
    foundV9 = False
    emptyItem = -1
    for i, bandV9 in enumerate(lines):
        if bandV9.find("supportedBandListEUTRA-v9") != -1:
            foundV9 = True
        elif foundV9 and bandV9.find("Item") != -1:
            if emptyItem == 1:
                bandListV9.append("")
        elif foundV9 and bandV9.find("SupportedBandEUTRA-v9") != -1:
            emptyItem = 1
        elif foundV9 and bandV9.find("bandEUTRA-v9") != -1:
            emptyItem = 0
            bandLine = lines[i]
            band = bandLine[lines[i].find(":") + 2:None].replace('\n','')
            bandListV9.append(band)
        elif foundV9 and bandV9.find("nonCriticalExtension") != -1:
            foundV9 = False
            break
    #Concatenate both supportedBandListEUTRA and supportedBandListEUTRA-v9, replacing  B64 by v9 one
    for i, (j, k) in enumerate(zip(bandsList,bandListV9)):
        if k != "":
            bandsList[i] = bandListV9[i]



def parseSupportedBandsWiresharkFormat(lines):
    found = False
    foundBandV9 = False
    for i, bands in enumerate(lines):
        if bands.find("supportedBandListEUTRA:") != -1:
            found = True
        elif found and bands.find("bandEUTRA:") != -1:
            bandLine = lines[i]
            band = bandLine[lines[i].find("bandEUTRA:") + len("bandEUTRA: "):None].replace('\n','')
            if band == "64":
                foundBandV9 = True
            bandsList.append(band)
        elif found and bands.find("measParameters") != -1:
            found = False
            break
    # Need to add Band Rel9 (B66, B46, B252, B253, B254 and B255)
    if (foundBandV9):
        parseSupportedBandsV9WiresharkFormat(lines)



def parseBandCombinationV10WiresharkFormat(fileLines):
    item = 0
    comboItem = 0
    foundStart = False
    combo = ""
    isCombo = False
    band_combination_item_start_index = -1
    band_item_Index = -1
    bandObj = {}
    bandCombinationItemList = []
    bandCombinationV10List = []
    bandCombinationItemListIndex = 0
    subItem = -1
    i = UtilsLib.findstring(fileLines, "supportedBandCombination-v1090:")
    while True:
        # ********************************************* INIT *******************************************************************
        if fileLines[i].find("supportedBandCombination-v1090:") != -1:
            foundStart = True
            if (fileLines[i + 1].find("Item") != -1):
                band_combination_item_start_index = fileLines[i + 1].find("Item")
                if (fileLines[i + 2].find("BandCombinationParameters-v1090") != -1):
                    if (fileLines[i + 3].find("Item") != -1):
                        band_item_Index = fileLines[i + 3].find("Item")

        # ********************************************* ITEM *******************************************************************
        elif foundStart and fileLines[i].find("Item") == band_combination_item_start_index:
            if (subItem != -1): #in case there is no bandEUTRA-v1090, subItem will be different from -1, so, we need to append anyway for concistency
                bandCombinationV10List.append(bandCombinationItemList)
            itemLine = fileLines[i]
            item = int(itemLine[fileLines[i].find("Item") + len("Item "):None])
            bandCombinationItemListIndex = -1
            bandCombinationItemList = []
            isCombo = False
            subItem = -1
            combo = ""
        elif foundStart and fileLines[i].find("BandCombinationParameters-v1090") != -1:
            comboItems = fileLines[i]
            comboItem = int(comboItems[fileLines[i].find("BandCombinationParameters-v1090") + len("BandCombinationParameters-v1090: "):fileLines[i].find("item")].replace('\n',''))
        elif foundStart and fileLines[i].find("Item") == band_item_Index:
            bandObj = {}
            bandCombinationItemList.append(bandObj)
            bandCombinationItemListIndex += 1
            subItem += 1
            if comboItem > 1:
                isCombo = True
            if print_console:
                print("Item: {}".format(item))
                if (isCombo):
                    print("Band Combination: {}".format(combo))
                    print("")
                else:
                    combo = combo.replace('\n', '')
                    print("Band: {}".format(combo))
        # ********************************************* BAND ********************************************************************
        elif foundStart and fileLines[i].find("bandEUTRA-v1090:") != -1:
            bandLine = fileLines[i]
            band = bandLine[bandLine.find("bandEUTRA-v1090") + len("bandEUTRA-v1090: "):None].replace('\n','')
            if isCombo:
                combo = ''.join([combo, " + {}".format(band)]).replace('\n', '')
            else:
                combo = "{}".format(band)
            bandCombinationItemList[bandCombinationItemListIndex]['Band'] = band
            if comboItem == subItem:
                bandCombinationV10List.append(bandCombinationItemList)
                subItem = -1
        # ********************************************** END ********************************************************************
        elif fileLines[i].find("nonCriticalExtension") != -1:
            # finish
            bandCombinationV10List.append(bandCombinationItemList)
            foundStart = False
            break
        i += 1
    #Need to change order of PCC, as it is already changed in bandCombinationList
    for i, (bcListv10, uplinkOrderList) in enumerate(zip(bandCombinationV10List, bcUplinkList)):
        for j, (bcV10, uplinkList) in enumerate(zip(bcListv10,uplinkOrderList)):
            if j != 0 and uplinkList == True:
                temp = bcListv10[0]
                bcListv10[0] = bcListv10[j]
                bcListv10[j] = temp

    #Concatenate both supportedBandListEUTRA and supportedBandListEUTRA-v9, replacing  B64 by v9 one
    for bcList, bcListv10 in zip(bandCombinationList,bandCombinationV10List):
        for bc, bcV10 in zip(bcList,bcListv10):
            if bc['Band'] == "64":
                if 'Band' in bcV10 and bcV10['Band'] != int(0):
                    bc['Band'] = bcV10['Band']


# Wireshark format of UE Capability Information message
def parseBandCombinationWiresharkFormat(fileLines):
    print("Wireshark Format.")
    i = UtilsLib.findstring(fileLines, "supportedBandCombination-r")
    #no Carrier Aggregation support
    if (i == None):
        bandCombinationList.append("None")
        return
    item = 0
    foundStart = False
    previousItem = -1
    combo = ""
    mimo = ""
    isCombo = False
    band_combination_item_start_index = -1
    layers = 0
    mimoList = []
    bwClass = ""
    hasUplink = False
    mimoListIndex = 0
    bandObj = {}
    bandCombinationItemList = []
    bandCombinationUplinkList = []
    bandCombinationItemListIndex = 0
    foundBandCombinationV10 = False
    while True:
# ********************************************* INIT *******************************************************************
        if fileLines[i].find("supportedBandCombination-r10:") != -1:
            foundStart = True
            if (fileLines[i+1].find("Item") != -1):
                band_combination_item_start_index = fileLines[i+1].find("Item")
# ********************************************* ITEM *******************************************************************
        elif foundStart and fileLines[i].find("Item") == band_combination_item_start_index:
            itemLine = fileLines[i]
            item = int(itemLine[fileLines[i].find("Item") + len("Item "):None])
#********************************************* BAND ********************************************************************
        elif foundStart and fileLines[i].find("bandEUTRA-r10:") != -1:
            #get supported bands
            bandLine = fileLines[i]
            band = bandLine[bandLine.find("bandEUTRA-r10") + len("bandEUTRA-r10: "):None].replace('\n','')
            if band == "64":
                foundBandCombinationV10 = True
            bandObj = {}
            if item != previousItem:
                #new Item found
                if combo != "":
                    bandCombinationList.append(bandCombinationItemList)
                    bcUplinkList.append(bandCombinationUplinkList)
                    layersList.append(layers)
                    #bandCombinationList.append(layers)
                    if print_console:
                        print("Item: {}".format(item-1))
                        if (isCombo):
                            print("Band Combination: {}".format(combo))
                            print("Layers: {}".format(layers))
                            print("MIMO: {}".format(mimoList).replace('[','').replace(']','').replace('\'','').replace('\n',''))
                            print("")
                        else:
                            combo = combo.replace('\n','')
                            print("Band: {}".format(combo))
                            print("MIMO: {}".format(mimo))
                            if bwClass == "b" or bwClass == "c" or bwClass == "d" or bwClass == "e":
                                print("Layers: {}\n".format(layers))
                            else:
                                print("")
                isCombo = False
                layers = 0
                mimoListIndex = 0
                bandCombinationItemListIndex = 0
                bandCombinationItemList = []
                bandCombinationUplinkList = []
                mimoList = []
                previousItem = item
                combo = "{}".format(band)
            else:
                isCombo = True
            bandCombinationItemList.append(bandObj)
            bandCombinationItemList[bandCombinationItemListIndex]['Band'] = band
            bandCombinationItemList[bandCombinationItemListIndex]['Item'] = item
            if fileLines[i + 1].find("bandParametersUL-r10:") != -1:
                hasUplink = True
                bandCombinationItemList[bandCombinationItemListIndex]['HasUplink'] = True
                bandCombinationUplinkList.append(True)
            else:
                hasUplink = False
                bandCombinationUplinkList.append(False)
#********************************************* MIMO ********************************************************************
        elif fileLines[i].find("supportedMIMO-CapabilityDL-r10") != -1:
            #get number of supported antennas
            mimoLine = fileLines[i]
            mimo = mimoLine[fileLines[i].find("supportedMIMO-CapabilityDL-r10") + len("supportedMIMO-CapabilityDL-r10: "):fileLines[i].find("(")-1]
            bandCombinationItemList[bandCombinationItemListIndex]['SupportedMIMOLayers'] = mimo
            if fileLines[i-1].find("ca-BandwidthClassDL-r10") != -1:
                #get bandwidth class
                bwClassStart = fileLines[i-1].find("ca-BandwidthClassDL-r10") + len("ca-BandwidthClassDL-r10: ")
                bwLine = fileLines[i-1]
                bwClass = bwLine[bwClassStart:bwClassStart+1]
                bandCombinationItemList[bandCombinationItemListIndex]['BwClass'] = bwClass
                if isCombo:
                    if hasUplink:
                        # this is the main band, as contains UL
                        combo = ''.join(["{}{} + ".format(band,bwClass.upper()), combo]).replace('\n', '')
                        mimoList.insert(mimoListIndex-1,mimo)
                        bandCombinationItemList[bandCombinationItemListIndex]['HasUplink'] = True
                        temp = bandCombinationItemList[bandCombinationItemListIndex]                        #
                        bandCombinationItemList[bandCombinationItemListIndex] = bandCombinationItemList[0]  #Swap Uplink
                        bandCombinationItemList[0] = temp                                                   #
                    else:
                        combo = ''.join([combo, " + {}{}".format(band,bwClass.upper())]).replace('\n', '')
                        mimoList.insert(mimoListIndex,mimo)
                        bandCombinationItemList[bandCombinationItemListIndex]['HasUplink'] = False
                else:
                    combo = ''.join([combo, "{}".format(bwClass.upper())]).replace('\n', '')
                    mimoList.insert(mimoListIndex - 1, mimo)
                mimoListIndex += 1
                layers = UtilsLib.calculateLayers(layers, mimo, bwClass)
            bandCombinationItemListIndex += 1
#********************************************** END ********************************************************************
        elif fileLines[i].find("measParameters-v1020") != -1:
            #finish
            bandCombinationList.append(bandCombinationItemList)
            bcUplinkList.append(bandCombinationUplinkList)
            layersList.append(layers)
            if print_console:
                print("Item: {}".format(item - 1))
                if (isCombo):
                    print("Band Combination: {}".format(combo))
                    print("Layers: {}".format(layers))
                    print("MIMO: {}".format(mimoList).replace('[','').replace(']','').replace('\'','').replace('\n', ''))
                    print("")
                else:
                    combo = combo.replace('\n', '')
                    print("Band: {}".format(combo))
                    print("MIMO: {}".format(mimo))
                    if bwClass == "b" or bwClass == "c" or bwClass == "d" or bwClass == "e":
                        print("Layers: {}\n".format(layers))
                    else:
                        print("")
            foundStart = False
            break
        i += 1
    # Handle supportedBandCombination-v1090
    if foundBandCombinationV10:
        parseBandCombinationV10WiresharkFormat(fileLines)


def parseBandwidthCombinationSetWiresharkFormat(fileLines):

    i = UtilsLib.findstring(fileLines, "supportedBandCombinationExt-r10:")

    #no Carrier Aggregation support
    if (i == None):
        bcsList.append("None")
        return

    foundStart = False
    bandwidth_combination_set_item_start_index = -1

    while True:
        # ********************************************* INIT *******************************************************************
        if fileLines[i].find("supportedBandCombinationExt-r10:") != -1:
            foundStart = True
            if (fileLines[i+1].find("Item") != -1):
                bandwidth_combination_set_item_start_index = fileLines[i+1].find("Item")
        elif foundStart and fileLines[i].find("Item") == bandwidth_combination_set_item_start_index:
            itemLine = fileLines[i]
            item = int(itemLine[fileLines[i].find("Item") + len("Item "):None])
        elif foundStart and fileLines[i].find("BandCombinationParametersExt-r10") != -1:
            if fileLines[i+1].find("supportedBandwidthCombinationSet-r10") == -1:
                bcsList.append("")
        elif foundStart and fileLines[i].find("supportedBandwidthCombinationSet-r10") != -1:
            bcsLine = fileLines[i]
            bcs = bcsLine[fileLines[i].find("supportedBandwidthCombinationSet-r10") + len(
                "supportedBandwidthCombinationSet-r10: "):fileLines[i].find("[") - 1]
            bcsList.append(UtilsLib.convertBCS(bcs.lower(),True))
        else:
            foundStart = False
            break
        i += 1



def parseHighOrderModulationWiresharkFormat(lines):
    dicMod = {}
    found = False
    for i, modulation in enumerate(lines):
        if modulation.find("supportedBandListEUTRA-v1250:") != -1:
            found = True
        elif found and modulation.find("dl-256QAM-r12:") != -1:
            dicMod = {}
            modLine = lines[i]
            downlink = modLine[lines[i].find("dl-256QAM-r12") + len("dl-256QAM-r12: "):lines[i].find(" (")]
            dicMod['dl-256QAM-r12'] = downlink
        elif found and modulation.find("ul-64QAM-r12") != -1:
            modLine = lines[i]
            uplink = modLine[lines[i].find("ul-64QAM-r12") + len("ul-64QAM-r12: "):lines[i].find(" (")]
            dicMod['ul-64QAM-r12'] = uplink
            modulationList.append(dicMod)
        elif found and modulation.find("freqBandPriorityAdjustment") != -1:
            break
    #if there is no support for 256QAM or 64QAM
    if found == False:
        for band in enumerate(bandsList):
            modList = []
            dicMod = {}
            dicMod['dl-256QAM-r12'] = "not supported"
            dicMod['ul-64QAM-r12'] = "not supported"
            modulationList.append(dicMod)



#************* Called from main loop. This method will call all other parsers and will store data in DB*****************
def parseWiresharkFormat(lines,fileName):
    #Parse supported LTE bands
    parseSupportedBandsWiresharkFormat(lines)

    #Parse supported band combination
    parseBandCombinationWiresharkFormat(lines)

    #Parse supported BCS
    parseBandwidthCombinationSetWiresharkFormat(lines)

    #Parse support for 256QAM in DL and 64QAM in UL
    parseHighOrderModulationWiresharkFormat(lines)

    # write table on Excel
    ExcelHandler.write2Excel(bandsList, bandCombinationList, layersList, bcsList, modulationList, fileName)