import requests
import re
import sys
import argparse
from progressbar import Counter, ProgressBar, SimpleProgress

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--title", help="title")
parser.add_argument("-s", "--set", help="set")
parser.add_argument("-k", "--keyword", help="keyword")
parser.add_argument("-l", "--legality", help="legality")
parser.add_argument("-r", "--rarity", help="rarity")
parser.add_argument("-x", "--text", help="card text")
parser.add_argument("-y", "--type", help="card type")
parser.add_argument("-c", "--clan", help="clan")
parser.add_argument("-o", "--output", help="output type", default="info")
args = parser.parse_args()
opts = vars(args)

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
    #text
    try:
        cardinfo['text'] = str(re.sub('<[^<]+?>', '',
                                  getcard.text.split('Printed Text</div></td><td class="cardlisting mechanics"><div class="shadowdatacurrent" style="">')[1].split('</div>')[0].replace('<b>',' - ')))
    except:
        cardinfo['text'] = "extraction failed. please file a bug with your search query"

    return cardinfo

def doSearchFlex(page=1, **kwargs):
    searchurl = 'http://imperialassembly.com/oracle/dosearch'
    template = {"search_13":"title",
               "search_sel_14[]":"type",
               "search_sel_12[]":"clan",
               "search_7":"keyword",
               "search_15":"text",
               "search_sel_35[]":"set",
               "search_sel_38[]":"rarity",
               "search_sel_10[]":"legality"}
    payload = {}
    for arg in dict(kwargs):
        for sarg in template:
            if template[sarg] == arg:
                payload[sarg] = dict(kwargs)[arg]
    payload['page'] = page
    r = requests.post(searchurl, data=payload)
    return r

def doSearchByPage(page, **kwargs):
    r = doSearchFlex(page, **kwargs)
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
    r = doSearchFlex(**kwargs)
    if len(re.findall("jquery.js",r.text.split('</script>')[0])) > 0:
        return getCard(str(re.findall("cardid=(\d+)",r.text)[0]))
    try:
        maxpages = int(re.findall('changepage\(\$\(this\)\);}">of (\d+)',r.text)[0])
    except:
        maxpages = 1

    allresults = []
    print "query returned %s pages." % str(maxpages)
    pbar = ProgressBar(widgets=[SimpleProgress()], maxval=maxpages).start()
    for page in range(0, maxpages):
        pbar.update(page + 1)
        for each in doSearchByPage(page=str(page+1),**kwargs):
            if output == "names":
                allresults.append(str(each[0]).replace('&#149;','-'))
            elif output == "ids":
                allresults.append([str(each[0]).replace('&#149;','-'),str(each[1])])
            elif output == "info":
                allresults.append(getCard(each[1]))
    pbar.finish()
    return allresults

def newrares(setname):
    cel = ['Thunderous Acclaim','Twenty Festivals','The New Order','A Line in the Sand','The Coming Storm',
           'Ivory Edition','Aftermath','Gates of Chaos','Torn Asunder','Honor & Treachery','Seeds of Decay',
           'The Shadow\'s Embrace','Embers of War','Emperor Edition']
    uniques = []
    data = doSearch(set=setname, rarity="Rare", keyword="shugenja", output="info")
    for each in data:
        filteredsets = []
        rel = cel[:cel.index(setname)]
        print rel
        print each['sets']
        for s in each['sets']:
            if s not in rel:
                filteredsets.append(s)
        print s
        if len(filteredsets) > 1:
            if each['soulof'] == "none":
                uniques.append(each['title'])
    print setname
    print "total: ", len(data)
    print "new rares: ", len(uniques)

def main():
    if args.output not in ['names','ids','info']:
        print "invalid output specified"
        sys.exit(1)

    argcounter = 0
    for each in opts:
        if opts[each] is not None:
            argcounter += 1

    if argcounter < 2:
        print "You must supply at least one search criteria"
        parser.print_help()
        sys.exit(1)

    results = doSearch(**opts)
    if args.output == "info":
        if type(results) != list:
            results = [results]
        for each in results:
            print each['title']
            for a in each:
                if a != "title":
                    if each[a] != "none":
                        print "---- %s: %s" % (a, each[a])
            print ""
    else:
        for each in results:
            print each

if __name__ == "__main__":
    main()