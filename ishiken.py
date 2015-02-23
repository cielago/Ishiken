import requests
import re
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--title", help="title")
parser.add_argument("-s", "--set", help="set")
parser.add_argument("-k", "--keyword", help="keyword")
parser.add_argument("-l", "--legality", help="legality")
parser.add_argument("-r", "--rarity", help="rarity")
parser.add_argument("-x", "--text", help="card text")
parser.add_argument("-y", "--type", help="card type")
parser.add_argument("-c", "--clan", help="clan")
parser.add_argument("-o", "--output")
args = parser.parse_args()
opts = vars(args)

if args.output not in ['names','ids','info']:
    print "invalid output specified"
    sys.exit(1)
else:
    print args.output

def getCard(cardid):
    cardurl = 'http://imperialassembly.com/oracle/docard'
    payload = {'cardid':cardid}
    getcard = requests.post(cardurl, params=payload)
    cardinfo = {}
    cardinfo['title'] = str(re.findall('<td colspan="2">(.*)',getcard.text.split('</td>')[0])[0].replace('&#149;','-'))
    #sets
    try:
        setlist = re.sub('<[^<]+?>', '',getcard.text.split('<td class="cardlisting labelblankline"')[0].split('Set')[-1].split('shadowdatashadow')[0])[:-12].split('&#149;')
        if len(setlist) == 1:
            setlist = str(setlist[0]).replace('&ndash;','-')
        else:
            setlist = str(",".join(setlist )).replace('&ndash;','-')
        cardinfo['sets'] = setlist
    except:
        cardinfo['sets'] = ""
    #souls
    try:
        cardinfo['soulof'] = str(list(set(re.findall('Soul of ([\s\w]+)', getcard.text)))[0])
    except:
        cardinfo['soulof'] = "none"
    #clan
    try:
        clan = re.sub('<[^<]+?>', '',
                      getcard.text.split('Printed Clan')[1].split('Collections')[0].split('</div>')[1]).split(' &#149; ')
        if len(clan) == 1:
            clan = str(clan[0])
        else:
            clan = str(",".join(clan))
    except:
        clan = "none"
    cardinfo['clan'] = clan
    #type
    cardinfo['type'] = str(re.findall('<div class="shadowdatacurrent" style="">([\w]+)</div>',
                                      getcard.text.split('Printed Card Type')[-1].split('Rarity')[0])[0])
    #rarity
    cardinfo['rarity'] = str(re.sub('<[^<]+?>', '',
                                    getcard.text.split('Rarity')[2].split('Legality')[0].split('</div>')[1]))

    return cardinfo

def doSearchFlex(**kwargs):
    searchurl = 'http://imperialassembly.com/oracle/dosearch'
    template = {"search_13":"title",
               "search_sel_14[]":"type",
               "search_sel_12[]":"clan",
               "search_7":"keyword",
               "search_15":"text",
               "search_sel_35[]":"set",
               "search_sel_38[]":"rarity",
               "search_sel_10[]":"legality",
               "page":"page"}
    payload = {}

    for arg in dict(kwargs):
        for sarg in template:
            if template[sarg] == arg:
                payload[sarg] = dict(kwargs)[arg]
    r = requests.post(searchurl, data=payload)
    return r

def doSearchByPage(page, **kwargs):
    r = doSearchFlex(**kwargs)
    rawresults = r.text.split('\\n')
    rawmatches = []
    goodresults = []
    for rawres in rawresults:
        for each in rawres.split('</span>'):
            if "l5rfont" in each:
                rawmatches.append(each)
    for each in rawmatches:
        cardid = re.findall('cardid=(\d+)',each)[0]
        cardname = re.findall('class="l5rfont">(.*)',each)[0]
        goodresults.append([cardname, cardid])
    return goodresults

def doSearch(output='names', **kwargs):
    # searchurl = 'http://imperialassembly.com/oracle/dosearch'
    # payload = {"search_13":querystring,
    #            "search_sel_14[]":type,
    #            "search_sel_12[]":clan,
    #            "search_7":"",
    #            "search_15":"",
    #            "search_sel_35[]":cardset,
    #            "search_sel_38[]":"",
    #            "search_sel_10[]":""}
    # r = requests.post(searchurl, data=payload)
    r = doSearchFlex(**kwargs)
    if len(re.findall("jquery.js",r.text.split('</script>')[0])) > 0:
        return getCard(str(re.findall("cardid=(\d+)",r.text)[0]))
    try:
        maxpages = int(re.findall('changepage\(\$\(this\)\);}">of (\d+)',r.text)[0])
    except:
        maxpages = 1

    allresults = []
    print "query returned %s pages." % str(maxpages)
    for page in range(0, maxpages):
        print "working on page  %s." % str(page+1)
        for each in doSearchByPage(page=str(page+1),**kwargs):
            if output == "names":
                allresults.append(str(each[0]).replace('&#149;','-'))
            elif output == "ids":
                allresults.append([str(each[0]).replace('&#149;','-'),str(each[1])])
            elif output == "info":
                allresults.append(getCard(each[1]))

    return allresults
results = doSearch(**opts)
if args.output == "info":
    for each in results:
        print each['title']
        for a in each:
            if a != "title":
                if each[a] != "none":
                    print "---- %s: %s" % (a, each[a])
else:
    for each in results:
        print each
