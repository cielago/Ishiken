# Ishiken
A Python Command Line Client for AEG’s [Oracle of the Void](oracleofthevoid.com) l5r card database.

### Dependencies
* Python 2.7+ (developed with Python 2.7.6, not tested yet with any other version)
* Requests (install via `pip install requests`)
* Progressbar (install via `pip install progressbar` or download [here](https://code.google.com/p/python-progressbar/))

### Usage
`ishiken.py [-h] [-t TITLE] [-s SET] [-k KEYWORD] [-l LEGALITY] [-r RARITY] [-x TEXT] [-y TYPE] [-c CLAN] [-o OUTPUT]`

Each of the arguments represents a different search criteria. At least one must be specified besides output. Two different types of criteria: plain text search and variable. Plain text does a search in the field indicated. Variable requires one of a specific set of vars to be passed. Var input validation is forthcoming, but in the mean time if you care enough about l5r to use this, you probably can guess what these should be. If you’re having issues, check Oracle’s dropdowns. 

#### Plain Text Search

Title - plain text search in Card Title field
Keyword - plain text search in Keyword field
Text - plain text search in Card Text field

#### Variables
Set - Set (see dropdown)
Legality - Legality (see dropdown)
Rarity - [Rare, Uncommon, Common, Fixed, Premium, Promo, None]
Type - [Ancestor, Celestial, Clock, Event, Follower, Holding, Item, Other, Personality, Proxy, Region, Ring, Sensei, Spell, Strategy, Stronghold, Territory, Wind]

### Disclaimer
I am not affiliated at all with AEG, I’m just a fan who hates doing anything with the mouse. As this makes requests identically to the website, I do not *believe* this is in any violation of the site’s terms, but I would not bet money on that. 