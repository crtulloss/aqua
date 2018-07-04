# emailer.py
# CRT
# created 7/4/2018
# last updated 7/4/2018
# sends email updates to Caleb when we leave or enter home homeZone

import requests
import aquaGSM

emailPublicURL = 'https://script.google.com/macros/s/AKfycbz9xFG3ACYZnis7YjntrSthrKfY68TDuKjMrnL2Gc5SXulm378/exec'

def sendEmail(home):
    # open the cell connection
    aquaGSM.openPPPD()
    # have the WebApp send an email
    baseString = emailPublicURL + '?home='
    if (home):
        requests.get(baseString  + 'true')
    else:
        requests.get(baseString + 'false')
    # close the connection
    aquaGSM.closePPPD()
