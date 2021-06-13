from dictsandlists import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import re
import calendar

# Takes the team region (or ALL) and returns the team codes for all teams in the region (V1)
def getTop10(teamRegion):
    teamCodesInitial = []
    teamCodesFinal = []
    driver = webdriver.Chrome(executable_path=r"chromedriver.exe")
    driver.get(filterLinks["rankings"])
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    links = driver.find_elements_by_tag_name("a")
    for link in links:
       if (str(link.get_attribute('href')).find("/team/") != -1): teamCodesInitial.append(str(link.get_attribute('href'))[24:])
    [teamCodesFinal.append(x) for x in teamCodesInitial if x not in teamCodesFinal]
    time.sleep(10)
    driver.close()
    if (teamRegion == "EU"): return teamCodesFinal[0:10]
    elif (teamRegion == "NA"): return teamCodesFinal[10:20]
    elif (teamRegion == "LATAM"): return teamCodesFinal[20:30]
    elif (teamRegion == "OCE"): return teamCodesFinal[30:40]
    elif (teamRegion == "ASIA"): return teamCodesFinal[40:50]
    elif (teamRegion == "KR"): return teamCodesFinal[50:60]
    elif (teamRegion == "MENA"): return teamCodesFinal[60:70]
    elif (teamRegion == "ALL"): return teamCodesFinal
    else: return []

# Takes team code and returns the event codes in a list (V1)
def getEvents(teamCode):
    eventCodesInitial = []
    eventCodesFinal = []
    driver = webdriver.Chrome(executable_path=r"chromedriver.exe")
    driver.get(filterLinks["overview"]+teamCode)
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    links = driver.find_elements_by_tag_name("a")
    for link in links:
       if (str(link.get_attribute('href')).find("/event/") != -1): eventCodesInitial.append(str(link.get_attribute('href'))[25:])
    [eventCodesFinal.append(x) for x in eventCodesInitial if x not in eventCodesFinal]
    #print(eventCodesFinal[0].split('/')[0])
    return eventCodesFinal

# Takes event code and returns all of the teams at that event (V1)
def getTeamsFromEvent(eventCode):
    teamCodesInitial = []
    teamCodesFinal = []
    driver = webdriver.Chrome(executable_path=r"chromedriver.exe")
    driver.get(filterLinks["events"]+eventCode)
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    links = driver.find_elements_by_tag_name("a")
    for link in links:
       if (str(link.get_attribute('href')).find("/team/") != -1): teamCodesInitial.append(str(link.get_attribute('href'))[24:])
    [teamCodesFinal.append(x) for x in teamCodesInitial if x not in teamCodesFinal]
    time.sleep(10)
    driver.close()
    return teamCodesFinal

# Takes Data and gives it an appropriate context description such as Never, Very Low, High, etc (V1)
def getHLDescription(inputType, inputData):
    if(inputType == "Agent Pick Rate"):
        if (inputData == 0): return "agents never picked"
        elif (0 < inputData <= 20): return "agents picked rarely"
        elif (20 < inputData <= 40): return "agents picked sometimes"
        elif (40 < inputData <= 60): return "agents picked about half the time"
        elif (60 < inputData <= 80): return "agents picked often"
        elif (80 < inputData < 100): return "agents picked very often"
        elif (inputData == 100): return "agents alwasy picked"
        else: return "ERROR"
    if(inputType == "Map Pick Rate"):
        if (inputData == 0): return "Never"
        elif (0 < inputData <= 5): return "Very Low"
        elif (5 < inputData <= 14): return "Low"
        elif (14 < inputData <= 22): return "Medium"
        elif (22 < inputData <= 30): return "High"
        elif (inputData >= 30): return "Very High"
        else: return "ERROR"
    return "ERROR: Did you forget an HLDescription argument"

# Takes regional ranking link and returns a list od dicts of all teams (V2)
def getTeamsFromRanking(regionLink):
    driver = webdriver.Chrome(executable_path=r"chromedriver.exe")
    driver.get(regionLink)
    outputList = []
    valuesList = []
    siteClassesList = ['rank-item-team', 'rank-item-rating', 'rank-item-streak.mod-right', 'rank-item-record.mod-right', 'rank-item-earnings.mod-right', 'rank-item-team-country']
    # Gathers data for team name, rating, W-L streak, record, earnings, and country
    for category in siteClassesList:
        tmpCatList = []
        dataSource = driver.find_elements_by_class_name(category)
        if ((category == 'rank-item-record.mod-right') or (category == 'rank-item-team-country') or (category == 'rank-item-earnings.mod-right')): 
            for dataVal in dataSource: tmpCatList.append(dataVal.text)
        else:
            for dataVal in dataSource: tmpCatList.append(dataVal.get_attribute('data-sort-value'))
        valuesList.append(tmpCatList)

    valuesList.append(getHrefsFromClass('.//td[contains(@class, "rank-item-team")]', '/team/', 24, driver))
    valuesList = [valuesList[0][1:], valuesList[1][1:], valuesList[2][1:], valuesList[3][1:], valuesList[4][1:], valuesList[5], valuesList[6]] # Clips off some extra values at the start of some of the lists

    # Takes data from lists and transforms it into dictionaries that get appended to outputList
    for teams in range(len(valuesList[0])):
        teamDict = { 'Team Name': valuesList[0][teams], 'Team Code': valuesList[6][teams], 'Country': valuesList[5][teams], 'Rank': teams+1, 'Rating': valuesList[1][teams], 'Streak': valuesList[2][teams], \
                    'Record': valuesList[3][teams], 'Earnings': valuesList[4][teams] }
        outputList.append(teamDict)

    time.sleep(3)
    driver.close()
    return outputList

def getMatchesFromTeamPage(matchesLink): # Gets matches from team page and returns them as a list of dicts. This needs cleaning (V2)
    driver = webdriver.Chrome(executable_path=r"chromedriver.exe")
    driver.get(matchesLink)
    outputList = []
    totalPages = len(driver.find_elements_by_class_name('btn.mod-page'))
    if totalPages == 0: totalPages = 1
    for page in range(totalPages):
        firstTeamName = driver.find_element_by_tag_name('h1').text
        eventStageList = getInnerDetailsList("//div[@class='rm-item-event']//div[contains(@class, 'text-of')]", driver)
        eventList = eventStageList[1::2]
        stageList = eventStageList[0::2]
        dateAndTimeList = getInnerDetailsList("//div[@class='rm-item-date']", driver)
        matchLinkList = []
        for match in driver.find_elements_by_class_name('wf-module-item'):
            matchLinkList.append(match.get_attribute('href')[19:])

        for match in range(len(eventList)):
            matchDict = {}
            matchDict.clear()
            matchDict = { 'Match Link': matchLinkList[match], 'Event': eventList[match], 'Event Stage': stageList[match],\
                         'Time': dateAndTimeList[match].split('<br>')[0], 'Date': dateAndTimeList[match].split('<br>')[1] }
            outputList.append(matchDict.copy())
        time.sleep(3)
        driver.close()
        driver = webdriver.Chrome(executable_path=r"chromedriver.exe")
        driver.get(matchesLink + '?page=' + str(page+2))

    time.sleep(3)
    driver.close()
    return outputList

# Support function that takes a class xpath string and the driver and returns the href from it (V2)
def getHrefsFromClass(xpathString, prefix, cutoff, driver):
    teamCodes = []
    linkGrab = driver.find_elements_by_xpath(xpathString)
    for link in linkGrab:
        linkAtt = link.find_element_by_tag_name("a")
        if (str(linkAtt.get_attribute('href')).find(prefix) != -1): teamCodes.append(str(linkAtt.get_attribute('href'))[cutoff:])
    return teamCodes

# Support function that takes xpath and driver and returns list of cleaned innerHTML attributes (V2)
def getInnerDetailsList(xpath, driver):
    elementList = driver.find_elements_by_xpath(xpath)
    outputList = []
    for elements in elementList:
        if(innerHTMLCleaner(elements.get_attribute('innerHTML')) == 'FFW'): # This handles FFW error in getMatchesFromTeamPage and may need further fixing
            outputList.append(-1)
            outputList.append(-1)
        else: outputList.append(innerHTMLCleaner(elements.get_attribute('innerHTML')))
    return outputList

# Support function that takes xpath and driver and returns list of cleaned whatever attributes (V2)
def getInnerAttrList(xpath, attribute, driver):
    elementList = driver.find_elements_by_xpath(xpath)
    outputList = []
    for elements in elementList:
        outputList.append(innerHTMLCleaner(elements.get_attribute(attribute)))
    return outputList

# Support function that takes an input string found using the innerHTML attribute and cleans tabs and newlines (V2)
def innerHTMLCleaner(inputString):
    return inputString.replace('\n', '').replace('\t', '')

# prints list one by one (V2)
def printL(inputList):
    for x in inputList: print(x)

# Strips matches not in date or event range out of the running #TODO: Fill or delete
def dateAndEventStrip():
    None

# Support function that takes an xpath directed at agents and returns all the agents in that match (in parsing order) (V2)
def getAgents(xpath, driver):
    elementList = driver.find_elements_by_xpath(xpath)
    outputList = []
    for elements in elementList:
        tmpList = []
        for name in agentNames:
            if (elements.get_attribute('innerHTML').find(name) != -1):
                tmpList.append(name)
        outputList.append(tmpList)
    return outputList

# Support function that takes an xpath directed at maps and returns all the agents in that match (V2)
def getMaps(xpath, driver):
    elementList = driver.find_elements_by_xpath(xpath)
    outputList = []
    for elements in elementList:
        for maps in valMaps:
            if (elements.get_attribute('innerHTML').find(maps) != -1):
                outputList.append(maps)
    return outputList


# Support function that takes an xpath directed at players and returns all the players in that match (in parsing order) (V2)
def getPlayers(xpath, driver):
    elementList = driver.find_elements_by_xpath(xpath)
    outputList = []

    for elements in elementList:
        outputList.append(elements.find_element_by_tag_name('a').get_attribute('href').split('/')[5])

    return outputList

# Takes a list of strings with who won rounds and returns the side (attack or defense) (v2)
def getSideWonText(inputList):
    outputList = []
    for element in inputList:
        if(element.split(' ')[2] == 'mod-t'): outputList.append('Attack')
        elif (element.split(' ')[2] == 'mod-ct'): outputList.append('Defense')
        else: None
    return outputList

# Takes a list of links to the round win icon and outputs the type of round win (elim, defuse, time, bomb) (V2)
def getRoundWinIconText(inputList):
    outputList = []
    for element in inputList:
        if(element.find('defuse') != -1): outputList.append('Defuse')
        elif(element.find('time') != -1): outputList.append('Time')
        elif(element.find('elim') != -1): outputList.append('Elimination')
        elif(element.find('boom') != -1): outputList.append('Bomb')
        else: None
    return outputList


# Takes a link to a match and returns all the data associated with said map as a dict. Many things are poorly named here. (V2)
def getMapStatsData(mapLink):
    driver = webdriver.Chrome(executable_path=r"chromedriver.exe")
    driver.get(mapLink)
    
    tabLinks = getHrefsFromClass("//div[contains(@class, 'vm-stats-tabnav')]", '/', 0, driver)
    econLink = tabLinks[0][:-8]+'economy'
    performanceLink = tabLinks[0][:-8]+'performance'
    time.sleep(3)
    driver.close()

    econStatsList = getEconStats(econLink, driver)

    driver = webdriver.Chrome(executable_path=r"chromedriver.exe")
    driver.get(mapLink)
    
 
    mapStatsDict = {} # eventually pull this in from matches

    teams = getInnerDetailsList("//div[contains(@class, 'wf-title-med')]", driver)
    matchScores = getInnerDetailsList("//div[@class='match-header-vs-score']//span[@class='match-header-vs-score-winner' or @class='match-header-vs-score-loser']", driver)
    mapScores = getInnerDetailsList("//div[@class='vm-stats-game-header']//div[contains(@class, 'score')]", driver)
    statsNoSpec = getInnerDetailsList("//td[@class='mod-stat']//span[@class='stats-sq']", driver)
    allACS = statsNoSpec[0::2]
    allHS = statsNoSpec[1::2]
    allADR = getInnerDetailsList("//td[@class='mod-stat']//span[contains(@class, 'mod-combat')]", driver)
    mapKills = getInnerDetailsList("//td[contains(@class, 'mod-vlr-kills')]//span[@class='stats-sq']", driver)
    mapDeathsUC = getInnerDetailsList("//td[contains(@class, 'mod-vlr-deaths')]//span[@class='stats-sq']", driver)
    mapDeaths = []
    for x in mapDeathsUC:
        mapDeaths.append(x.split('>')[3].split('<')[0])
    mapAssists = getInnerDetailsList("//td[contains(@class, 'mod-vlr-assists')]//span[@class='stats-sq']", driver)
    #mapKillDiff = getInnerDetailsList("//td[contains(@class, 'mod-kd-diff')]//span[@class='stats-sq.stats-sq.mod-negative']", driver)
    firstKills = getInnerDetailsList("//td[contains(@class, 'mod-fb')]//span[@class='stats-sq']", driver)
    firstDeaths = getInnerDetailsList("//td[contains(@class, 'mod-fd')]//span[@class='stats-sq']", driver)

    sideRounds = getInnerDetailsList("//span[@class='mod-t' or @class='mod-ct']", driver)
    currScore = getInnerDetailsList("//div[@class='vlr-rounds-row-col']//div[@class='rnd-currscore']", driver)
    currScore = [x for x in currScore if x != '']
    roundWinIcon = getInnerDetailsList("//div[@class='vlr-rounds-row-col']//div[contains(@class, 'mod-win')]", driver)
    newRoundWinIcon = getRoundWinIconText(roundWinIcon)
    roundWinSide = getInnerAttrList("//div[@class='vlr-rounds-row-col']//div[contains(@class, 'mod-win')]", 'class', driver)
    newRoundWinSide = getSideWonText(roundWinSide)
    agentPlayed = getAgents("//td[@class='mod-agents']", driver)
    playersOrdered = getPlayers("//td[@class='mod-player']", driver)
    mapsOrdered = getMaps("//div[contains(@class, 'vm-stats-gamesnav-item')]", driver)

    time.sleep(3)
    driver.close()
    performanceStatsList = getPerformanceStats(performanceLink, mapsOrdered, driver)
       
    mapStatsDict["Maps Played"] = mapsOrdered[0:int(len(mapScores)/2)]

    mapTotalRounds = []
    matchRounds = [0]
    for matches in range(int(len(mapScores)/2)):
        mapTotalRounds.append(int(mapScores[matches*2]) + int(mapScores[matches*2+1]))
        matchRounds.append(int(mapScores[matches*2]) + int(mapScores[matches*2+1]) + int(matchRounds[matches])) # creates indices to divide up map rounds
        mapStatsDict[mapsOrdered[matches]] = {} # Creates nested dict for each map
        
    mapStatsDict['Team One'] = teams[0]
    mapStatsDict['Team Two'] = teams[1]
    
    if(int(matchScores[0]) > int(matchScores[1])): 
        mapStatsDict['Winner'] = teams[0]
        mapStatsDict['Loser'] = teams[1]
    elif(int(matchScores[0]) < int(matchScores[1])):
        mapStatsDict['Winner'] = teams[1]
        mapStatsDict['Loser'] = teams[0]
    else:
        mapStatsDict['Winner'] = 'N/A'
        mapStatsDict['Loser'] = 'N/A'
        mapStatsDict['Outcome'] = 'Tie'

    mapStatsDict['Match Score'] = str(matchScores[0]) + "-" + str(matchScores[1])


    for matches in range(int(len(mapScores)/2)): # matches is not named correctly for an iterator in this case, probably should fix
        for teamNums in range(2):
            mapStatsDict[mapsOrdered[matches]][str(teams[teamNums])+' Pistol Rounds'] = 0
            mapStatsDict[mapsOrdered[matches]][str(teams[teamNums])+' 2nd Round Conversion Wins'] = 0
            mapStatsDict[mapsOrdered[matches]][str(teams[teamNums])+' 2nd Round Conversion Losses'] = 0

        for count in range(matchRounds[matches+1] - matchRounds[matches]):
            mapStatsDict[mapsOrdered[matches]]['Round ' + str(count + 1)] = { 'Current Score': currScore[matchRounds[matches]+count], 'Side Won': newRoundWinSide[matchRounds[matches]+count], 
                                                                             'Won By': newRoundWinIcon[matchRounds[matches]+count] }


            if((count == 0) and (mapStatsDict[mapsOrdered[matches]]['Round 1']['Current Score'] == '1-0') and (mapStatsDict[mapsOrdered[matches]]['Round 1']['Side Won'] == 'Attack')):
                mapStatsDict[mapsOrdered[matches]]['Attack Start'] = teams[0]
                mapStatsDict[mapsOrdered[matches]]['Defense Start'] = teams[1]
            elif((count == 0) and (mapStatsDict[mapsOrdered[matches]]['Round 1']['Current Score'] == '1-0') and (mapStatsDict[mapsOrdered[matches]]['Round 1']['Side Won'] == 'Defense')):
                mapStatsDict[mapsOrdered[matches]]['Defense Start'] = teams[0]
                mapStatsDict[mapsOrdered[matches]]['Attack Start'] = teams[1]
            elif((count == 0) and (mapStatsDict[mapsOrdered[matches]]['Round 1']['Current Score'] == '0-1') and (mapStatsDict[mapsOrdered[matches]]['Round 1']['Side Won'] == 'Attack')):
                mapStatsDict[mapsOrdered[matches]]['Attack Start'] = teams[1]
                mapStatsDict[mapsOrdered[matches]]['Defense Start'] = teams[0]
            elif((count == 0) and (mapStatsDict[mapsOrdered[matches]]['Round 1']['Current Score'] == '0-1') and (mapStatsDict[mapsOrdered[matches]]['Round 1']['Side Won'] == 'Defense')):
                mapStatsDict[mapsOrdered[matches]]['Defense Start'] = teams[1]
                mapStatsDict[mapsOrdered[matches]]['Attack Start'] = teams[0]
            
            
            if(0 <= count < 12) or ((count >= 24) and (count % 2 != 0)):
                if(mapStatsDict[mapsOrdered[matches]]['Round ' + str(count + 1)]['Side Won'] == 'Attack'):
                    mapStatsDict[mapsOrdered[matches]]['Round ' + str(count + 1)]['Round Winner'] = mapStatsDict[mapsOrdered[matches]]['Attack Start']
                    mapStatsDict[mapsOrdered[matches]]['Round ' + str(count + 1)]['Round Loser'] = mapStatsDict[mapsOrdered[matches]]['Defense Start']
                elif(mapStatsDict[mapsOrdered[matches]]['Round ' + str(count + 1)]['Side Won'] == 'Defense'):
                    mapStatsDict[mapsOrdered[matches]]['Round ' + str(count + 1)]['Round Winner'] = mapStatsDict    [mapsOrdered[matches]]['Defense Start']
                    mapStatsDict[mapsOrdered[matches]]['Round ' + str(count + 1)]['Round Loser'] = mapStatsDict[mapsOrdered[matches]]['Attack Start']
            else:
                if(mapStatsDict[mapsOrdered[matches]]['Round ' + str(count + 1)]['Side Won'] == 'Attack'):
                    mapStatsDict[mapsOrdered[matches]]['Round ' + str(count + 1)]['Round Winner'] = mapStatsDict[mapsOrdered[matches]]['Defense Start']
                    mapStatsDict[mapsOrdered[matches]]['Round ' + str(count + 1)]['Round Loser'] = mapStatsDict[mapsOrdered[matches]]['Attack Start']
                elif(mapStatsDict[mapsOrdered[matches]]['Round ' + str(count + 1)]['Side Won'] == 'Defense'):
                    mapStatsDict[mapsOrdered[matches]]['Round ' + str(count + 1)]['Round Winner'] = mapStatsDict[mapsOrdered[matches]]['Attack Start']
                    mapStatsDict[mapsOrdered[matches]]['Round ' + str(count + 1)]['Round Loser'] = mapStatsDict[mapsOrdered[matches]]['Defense Start']

            if (count == 0) or (count == 12): # Pistol rounds
                if(mapStatsDict[mapsOrdered[matches]]['Round ' + str(count + 1)]['Round Winner'] == mapStatsDict['Team One']):
                    mapStatsDict[mapsOrdered[matches]]['Round ' + str(count + 1)]['Buy Result'] =\
                    str(mapStatsDict['Team One']) + " " + 'Pistol' + " won vs " + str(mapStatsDict['Team Two']) + " " + 'Pistol'
                    mapStatsDict[mapsOrdered[matches]][mapStatsDict['Team One'] + ' Pistol Rounds'] = mapStatsDict[mapsOrdered[matches]][mapStatsDict['Team One'] + ' Pistol Rounds'] + 1
                else:
                    mapStatsDict[mapsOrdered[matches]]['Round ' + str(count + 1)]['Buy Result'] = str(mapStatsDict['Team Two']) + " " + 'Pistol' + " won vs " +\
                    str(mapStatsDict['Team One']) + " " + 'Pistol'
                    mapStatsDict[mapsOrdered[matches]][mapStatsDict['Team Two'] + ' Pistol Rounds'] = mapStatsDict[mapsOrdered[matches]][mapStatsDict['Team Two'] + ' Pistol Rounds'] + 1
            elif (count == 1) or (count == 13): # Pistol round conversions
                if(mapStatsDict[mapsOrdered[matches]]['Round ' + str(count)]['Round Winner'] == mapStatsDict[mapsOrdered[matches]]['Round ' + str(count+1)]['Round Winner']):
                    mapStatsDict[mapsOrdered[matches]][str(mapStatsDict[mapsOrdered[matches]]['Round ' + str(count)]['Round Winner'])+' 2nd Round Conversion Wins'] += 1
                else:
                    mapStatsDict[mapsOrdered[matches]][str(mapStatsDict[mapsOrdered[matches]]['Round ' + str(count)]['Round Winner'])+' 2nd Round Conversion Losses'] += 1

            else:
                if(mapStatsDict[mapsOrdered[matches]]['Round ' + str(count + 1)]['Round Winner'] == mapStatsDict['Team One']):
                    mapStatsDict[mapsOrdered[matches]]['Round ' + str(count + 1)]['Buy Result'] =\
                    str(mapStatsDict['Team One']) + " " + str(econStatsList[0][matchRounds[matches]+count]) + " won vs " + str(mapStatsDict['Team Two']) + " " + str(econStatsList[1][matchRounds[matches]+count])
                else: 
                    mapStatsDict[mapsOrdered[matches]]['Round ' + str(count + 1)]['Buy Result'] = str(mapStatsDict['Team Two']) + " " + str(econStatsList[1][matchRounds[matches]+count]) + " won vs " +\
                    str(mapStatsDict['Team One']) + " " + str(econStatsList[0][matchRounds[matches]+count])
                    


    for statsDivs in range(int(len(playersOrdered)/10)):
        if(statsDivs == 1):
            for xcount in range(10):
                mapStatsDict[playersOrdered[10+xcount]] = { 'Agent Played': agentPlayed[10+xcount], 'ACS': allACS[10+xcount], 'HS': allHS[10+xcount], 'ADR': allADR[10+xcount],
                                                           'Kills': mapKills[10+xcount], 'Deaths': mapDeaths[10+xcount], 'Assists': mapAssists[10+xcount], 
                                                           'First Kills': firstKills[10+xcount], 'First Deaths': firstDeaths[10+xcount] }
        else:
            lowerDiv = statsDivs*10
            upperDiv = statsDivs*10+10
            for xcount in range(10):
                if (statsDivs == 0): statsIndex = statsDivs
                else: statsIndex = statsDivs-1
                mapStatsDict[mapsOrdered[statsIndex]][playersOrdered[lowerDiv+xcount]] = { 'Agent Played': agentPlayed[lowerDiv+xcount], 'ACS': allACS[lowerDiv+xcount], 'HS': allHS[lowerDiv+xcount], 'ADR': allADR[lowerDiv+xcount],
                                                                                         'Kills': mapKills[lowerDiv+xcount], 'Deaths': mapDeaths[lowerDiv+xcount], 'Assists': mapAssists[lowerDiv+xcount],
                                                                                         'First Kills': firstKills[lowerDiv+xcount], 'First Deaths': firstDeaths[lowerDiv+xcount]}
    matchPref = ['2K', '3K', '4K', '5K', '1v1', '1v2', '1v3', '1v4', '1v5']
    matchEPD = ['Economy', 'Plant', 'Defuse']

    """ # needs conditional fixes and testing on matches that are missing stats
    for maps in range(int(len(mapScores)/2)):
        for players in range(10):
            for stat in range(9):
                mapStatsDict[mapsOrdered[maps]][performanceStatsList[0][players]][matchPref[stat]] = performanceStatsList[1][maps*90+9*players+stat]
            for stat in range(3):
                mapStatsDict[mapsOrdered[maps]][performanceStatsList[0][players]][matchEPD[stat]] = performanceStatsList[3][maps*30+3*players+stat]

    for players in range(10):
        for stat in range(9):
            mapStatsDict[performanceStatsList[0][players]][matchPref[stat]] = performanceStatsList[2][9*players+stat]
        for stat in range(3):
            mapStatsDict[performanceStatsList[0][players]][matchEPD[stat]] = performanceStatsList[4][3*players+stat]
    """
        
    for maps in range(int(len(mapStatsDict['Maps Played']))):
        for econType in econTypes:
            for teamCount in range(2):
                mapStatsDict[mapsOrdered[maps]][str(teams[teamCount])+ ' ' + econType + ' Wins'] = 0
                mapStatsDict[mapsOrdered[maps]][str(teams[teamCount])+ ' ' + econType + ' Losses'] = 0

    for econType in econTypes:
        for teamCount in range(2):
            for wlVal in winsLosses:
                mapStatsDict[str(teams[teamCount])+ ' ' + econType + ' ' + wlVal] = 0


    if int(len(mapStatsDict['Maps Played']))*10 == int(len(econStatsList[2])):
        print("Not missing data")
        for maps in range(int(len(mapStatsDict['Maps Played']))):
            mapStatsDict[mapsOrdered[maps]][str(teams[0])+' Eco Wins'] = int(mapStatsDict[mapsOrdered[maps]][str(teams[0])+' Eco Wins']) + int(econStatsList[2][maps*10+1].split(' ')[1])-int(econStatsList[2][maps*10+0])
            mapStatsDict[mapsOrdered[maps]][str(teams[0])+' Eco Losses'] = int(mapStatsDict[mapsOrdered[maps]][str(teams[0])+' Eco Losses']) + int(econStatsList[2][maps*10+1].split(' ')[1])-2-(int(econStatsList[2][maps*10+1].split(' ')[1])-int(econStatsList[2][maps*10+0]))
            mapStatsDict[mapsOrdered[maps]][str(teams[1])+' Eco Wins'] = int(mapStatsDict[mapsOrdered[maps]][str(teams[0])+' Eco Wins']) + int(econStatsList[2][maps*10+6].split(' ')[1])-int(econStatsList[2][maps*10+5])
            mapStatsDict[mapsOrdered[maps]][str(teams[1])+' Eco Losses'] = int(mapStatsDict[mapsOrdered[maps]][str(teams[0])+' Eco Losses']) + int(econStatsList[2][maps*10+6].split(' ')[0])-2-(int(econStatsList[2][maps*10+6].split(' ')[1])-int(econStatsList[2][maps*10+5]))

            for val in range(3):
                mapStatsDict[mapsOrdered[maps]][str(teams[0])+ ' ' + str(econTypes[val+1]) + ' Wins'] = int(mapStatsDict[mapsOrdered[maps]][str(teams[0])+ ' ' + str(econTypes[val+1]) + ' Wins']) + int(econStatsList[2][maps*10+val+1].split(' ')[1])
                mapStatsDict[mapsOrdered[maps]][str(teams[0])+' ' + str(econTypes[val+1]) + ' Losses'] = int(mapStatsDict[mapsOrdered[maps]][str(teams[0])+' ' + str(econTypes[val+1]) + ' Losses']) + int(econStatsList[2][maps*10+val+1].split(' ')[0]) - int(econStatsList[2][maps*10+val+1].split(' ')[1])
                mapStatsDict[mapsOrdered[maps]][str(teams[1])+' ' + str(econTypes[val+1]) + ' Wins'] = int(mapStatsDict[mapsOrdered[maps]][str(teams[0])+' ' + str(econTypes[val+1]) + ' Wins']) + int(econStatsList[2][maps*10+val+6].split(' ')[1])
                mapStatsDict[mapsOrdered[maps]][str(teams[1])+' ' + str(econTypes[val+1]) + ' Losses'] = int(mapStatsDict[mapsOrdered[maps]][str(teams[0])+' ' + str(econTypes[val+1]) + ' Losses']) + int(econStatsList[2][maps*10+val+6].split(' ')[0]) - int(econStatsList[2][maps*10+val+6].split(' ')[1])
    else:
        print(mapLink)


    mapStatsDict[str(teams[0])+' Eco Wins'] = int(econStatsList[3][1].split(' ')[1])-int(econStatsList[3][0])
    mapStatsDict[str(teams[0])+' Eco Losses'] = int(econStatsList[3][1].split(' ')[0])-(2*len(mapStatsDict['Maps Played']))-(int(econStatsList[3][1].split(' ')[1])-int(econStatsList[3][0]))
    mapStatsDict[str(teams[1])+' Eco Wins'] = int(econStatsList[3][6].split(' ')[1])-int(econStatsList[3][5])
    mapStatsDict[str(teams[1])+' Eco Losses'] =  int(econStatsList[3][6].split(' ')[0])-(2*len(mapStatsDict['Maps Played']))-(int(econStatsList[3][6].split(' ')[1])-int(econStatsList[3][5]))

    for teamNum in range(2):
        mapStatsDict[str(teams[teamNum])+' 2nd Round Conversion Wins'] = 0 # These are used elsewhere but here is a good place to fil them
        mapStatsDict[str(teams[teamNum])+' 2nd Round Conversion Losses'] = 0
        if teamNum == 0:
            for econVals in range(3):
                mapStatsDict[str(teams[teamNum])+ ' ' + econTypes[econVals+1] + ' Wins'] = int(econStatsList[3][econVals+2].split(' ')[1])
                mapStatsDict[str(teams[teamNum])+ ' ' + econTypes[econVals+1] + ' Losses'] = int(econStatsList[3][econVals+2].split(' ')[0]) - int(econStatsList[3][econVals+2].split(' ')[1])
        else:
            for econVals in range(3):
                mapStatsDict[str(teams[teamNum])+ ' ' + econTypes[econVals+1] + ' Wins'] = int(econStatsList[3][econVals+7].split(' ')[1])
                mapStatsDict[str(teams[teamNum])+ ' ' + econTypes[econVals+1] + ' Losses'] = int(econStatsList[3][econVals+7].split(' ')[0]) - int(econStatsList[3][econVals+7].split(' ')[1])

    

    #for x in mapStatsDict['Haven']:
        #print(x)

    for maps in mapStatsDict["Maps Played"]:
        for teamNum in range(2):
            mapStatsDict[str(teams[teamNum])+' 2nd Round Conversion Wins'] += mapStatsDict[maps][str(teams[teamNum])+' 2nd Round Conversion Wins']
            mapStatsDict[str(teams[teamNum])+' 2nd Round Conversion Losses'] += mapStatsDict[maps][str(teams[teamNum])+' 2nd Round Conversion Losses']


    #for key, value in mapStatsDict.items():
      #print(str(key))
      #print(value)

    return mapStatsDict

# Support function that takes a link to the econ page of a match and returns a list of relevant econ stats (V2)
def getEconStats(econLink, driver):
    driver = webdriver.Chrome(executable_path=r"chromedriver.exe")
    driver.get(econLink)
    bank = getInnerDetailsList("//div[contains(@class, 'bank')]", driver) # maybe ill use this later
    buySQ = getInnerDetailsList("//div[contains(@class, 'rnd-sq')]", driver)
    totStatsUC =  getInnerDetailsList("//div[contains(@class, 'stats-sq')]", driver)
    totStats = []
    for x in totStatsUC:
        totStats.append(x.replace('(', ' ').replace(')',''))
       
    buys = []
    for buy in buySQ:
        if (buy == ''): buys.append('Eco')
        elif (buy == '$'): buys.append('LowBuy')
        elif (buy == '$$'): buys.append('HalfBuy')
        elif (buy == '$$$'): buys.append('FullBuy')
        else: None

    time.sleep(3)
    driver.close()

    return [buys[0::2], buys[1::2], totStats[0:-10], totStats[-10:]]

# Supoprt function that takes a link to the performance page of a match and returns a list of relevant perforamnce stats (V2)
def getPerformanceStats(performanceLink, mapsOrdered, driver):
    driver = webdriver.Chrome(executable_path=r"chromedriver.exe")
    driver.get(performanceLink)
    outputList = []

    statsAllMaps = getInnerDetailsList("//table[contains(@class, 'mod-adv-stats')]//div[contains(@class, 'mod-')]", driver)[0:90]
    statsIndvMaps = getInnerDetailsList("//table[contains(@class, 'mod-adv-stats')]//div[contains(@class, 'mod-')]", driver)[90:]
    statsEPD = getInnerDetailsList("//table[contains(@class, 'mod-adv-stats')]//div[@class='stats-sq']", driver)
    statsEPDClean = []

    for stats in statsEPD:
        if(stats.find('img') == -1): statsEPDClean.append(stats)
    statsEPDAllClean = statsEPDClean[0:30]
    statsEPDIndvClean = statsEPDClean[30:]

    statsIndvMapsClean = []
    statsAllMapsClean = []
    for stats in statsIndvMaps:
        if(stats.split('<')[0] == ''): statsIndvMapsClean.append('0')
        else: statsIndvMapsClean.append(stats.split('<')[0])
    for stats in statsAllMaps:
        if(stats == ''): statsAllMapsClean.append('0')
        else: statsAllMapsClean.append(stats)



    playerNamesContainer = getInnerDetailsList("//table[contains(@class, 'mod-adv-stats')]//div[contains(@class, 'team')]", driver)[0::2][0:10]
    playerNames = []
    indvStatsDict = {}
    for container in playerNamesContainer:
        playerNames.append(container.split('<div')[1][1:].lower())

    outputList = [playerNames, statsIndvMapsClean, statsAllMapsClean, statsEPDIndvClean, statsEPDAllClean]
    time.sleep(3)
    driver.close()
    return outputList

# Takes a list of match dicts and returns a filtered list based on event and/or date range (V2)
def filterMatches(matches, eventFilter, eventName, dateFilter, startDate, endDate):
    outputList = []
    if (eventFilter == True):
        for match in matches:
            if(str(match['Event']) == str(eventName)):
                outputList.append(match)
    #TODO: implement date range. you can simply do < or > comparisons on dates in iso format
    return outputList

# Support function that gets an event name from an event link (V2)
def getEventNameByEventLink(eventCode):
    eventLink = filterLinks['events'] + eventCode
    driver = webdriver.Chrome(executable_path=r"chromedriver.exe")
    driver.get(eventLink)
    eventName = getInnerDetailsList("//h1[contains(@class, 'wf-title')]", driver)
    time.sleep(3)
    driver.close()
    return eventName

# Support function thattTakes match output from map stats and returns a list of the names of all the teams in a usable format (V2)
def getTeamListFromMatchOutput(matchOutputList):
    teamList = []
    for match in matchOutputList:
        teamList.append(match['Team One'])
        teamList.append(match['Team Two'])
    teamList = list(dict.fromkeys(teamList))
    return teamList


if __name__ == "__main__":
    #teamsList = getTeamsFromEvent('372')
    teamsList = ['2/sentinels']
    matchLinkDicts = []
    for teams in teamsList:
        matches = getMatchesFromTeamPage(filterLinks['matches']+teams)
        for match in matches:
            matchLinkDicts.append(match)
    eventName = getEventNameByEventLink('353')
    filteredMatchLinkDicts = filterMatches(matchLinkDicts, True, eventName[0], False, '', '')
    uniqueFilteredMLD = [dict(t) for t in set([tuple(d.items()) for d in filteredMatchLinkDicts])]
    statsDictOutputList = []
    tmpLinkList = []
    # needed nonsense steps because it wasn't liking my links for some reason
    for x in uniqueFilteredMLD:
        tmpLinkList.append(x['Match Link'].split('/')[0])
    print(tmpLinkList)
    for y in tmpLinkList:
        statsDictOutputList.append(getMapStatsData(filterLinks['nopref'] + y))

    print(statsDictOutputList)