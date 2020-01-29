import requests, json, time, os, arrow, timeit
from datetime import datetime
from requests_oauthlib import OAuth1
from calendar import monthrange
from datetime import date
from dateutil import relativedelta
from tqdm import tqdm
from colorama import Fore

def saveTranscripts(pCount,pResult,year,month,interactionType):
    folders = os.getcwd()+"/main-folder/"+accountNo+"/"+interactionType+"/"+str(year)+"/"+str(month)
    # Create target Directory if don't exist
    if not os.path.exists(folders):
        logs.write("\n==>Folders successfully created!")
        os.makedirs(folders)
    
    file = open(os.getcwd()+"/main-folder/"+accountNo+"/"+interactionType+"/"+str(year)+"/"+str(month)+"/"+str(pCount)+
                    "-"+accountNo+"-"+str(year)+"-"+str(month)+".json", "w")
    file.write(json.dumps(pResult, sort_keys=True, indent=2))

def getTranscipts(pDateFrom,pDateTo,url,year,month,contentToRetrieve,interactionType):
    body = {
        "interactive":True,
        "ended":True,
        "start": {
            "from":pDateFrom,
            "to":pDateTo
        }
    }

    if bool(contentToRetrieve):
        if interactionType == "messaging":
            body.update({"contentToRetrieve": [x for x in contentToRetrieve]})
            logs.write("\n==>ONLY these content parameters will be retrieved: "+str(contentToRetrieve))
        else:
            logs.write("\n==>ContentToRetrieve only works with Messaging!\n")
    else:
        logs.write("\n==>ContentToRetrieve not set by user!\n")
   
    noOfLoops = 1
    firstTime = True
    count = 0
    pbar = tqdm(total = 100)
    pbar.set_description("Month Progress")
    pbar.bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.RED, Fore.RESET)
    while count < noOfLoops:
        response = requests.post(url, headers=headers, json=body, auth=oauth)
        result = response.json()
        try:                                                #Try getting the tracnscripts count, if error then print response and break loop
            transcriptsCount = result["_metadata"]["count"]
        except:
            logs.write("\n#######=>Error getting transcripts count: "+str(result)+"\n")
            pbar.write("\nError getting transcripts count: "+str(result)+"\n")
            break
        
        if transcriptsCount < 1:
            logs.write("\n==>No transcripts found for "+str(month)+"/"+str(year))
            break
        try:                                            #Try getting the next url for the api call, if error then just pass
            url = result["_metadata"]["next"]["href"]   #The last api call will not have the next url so it will throw an error
        except:
            pass

        if interactionType == "chat":
            if bool(result["interactionHistoryRecords"]): # if result has no records then dont save transcripts
                saveTranscripts(count,result,year,month,interactionType)
            else:
                logs.write("\n==>No data found in the interactionHistoryRecords array at count "+str(count)+": \n"+str(result)+"\n")
        else:
            if bool(result["conversationHistoryRecords"]): # if result has no records then dont save transcripts
                saveTranscripts(count,result,year,month,interactionType)
            else:
                logs.write("\n==>No data found in the conversationHistoryRecords array at count"+str(count)+": \n"+str(result)+"\n")

        if firstTime:
            logs.write("\n==>Transcripts Count: "+str(transcriptsCount)+ " Date: "+str(month)+"/"+str(year))
            pbar.write("\n--Transcripts Count: "+str(transcriptsCount)+ " Date: "+str(month)+"/"+str(year)+ " "+interactionType.upper())
            noOfLoops = transcriptsCount // 100
            remainder = transcriptsCount % 100
            if remainder > 0:     # if remainder is more than 0 then increment numder of loops to save the last batch of transcripts 
                noOfLoops+=1
            firstTime = False

        if count > noOfLoops/2.5:  # Change bar color as it progresses
            if count > noOfLoops/1.15:
                pbar.bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Fore.RESET)
            else:
                pbar.bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.YELLOW, Fore.RESET)

        count+=1
        
        try:
            pbar.update(100/noOfLoops)
        except ZeroDivisionError:
            pass

    try:
        file.close()
        pbar.close()
    except:
        pass


def startTranscripts(startDate,endDate,contentToRetrieve,interactionType):
    
    p13MonthsInMs = (13 * 30.5 * 24 * 60 * 60 * 1000) - 58*60*60*1000 # Minus 1 day to start from the next day
    # If user input blank, create end date and start date
    if endDate == "":
        today = date.today()
        todaysDate = today.strftime("%d/%m/%Y %H:%M:%S")
        endDate = today.strftime("%d/%m/%Y %H:%M:%S")
        todayDateInMs = datetime.strptime(str(todaysDate),'%d/%m/%Y %H:%M:%S').timestamp() * 1000
        logs.write("\n==>End Date: "+endDate)
    else:
        todayDateInMs = datetime.strptime(endDate,"%d/%m/%Y %H:%M:%S").timestamp() * 1000
        logs.write("\n==>End Date: "+endDate)

    if startDate == "":
        startDateInMs = todayDateInMs - p13MonthsInMs
        startDate = datetime.fromtimestamp(startDateInMs / 1000).strftime('%d/%m/%Y %H:%M:%S') # startDateInMs / 1000 to convert to seconds
        logs.write("\n==>Start Date: "+startDate)
    else:
        logs.write("\n==>Start Date: "+startDate)

    seconds = startDate[17:]
    minute = startDate[14:16]
    hour = startDate[11:13]
    day = int(startDate[0:2])
    month = int(startDate[3:5])
    year = int(startDate[6:10])
    firstTime2 = True

    date1 = datetime.strptime(startDate, '%d/%m/%Y %H:%M:%S')
    date2 = datetime.strptime(endDate, '%d/%m/%Y %H:%M:%S')
    diff = relativedelta.relativedelta(date2, date1)
    numberOfMonths = (diff.years*12) + diff.months + 1 #+1 to get the last month
    logs.write("\n==>Number of months: "+str(numberOfMonths))
    if numberOfMonths > 13:
        print("\n==?Start date is more then 13 months back. Max 13 months!")
        print("\n==>Exiting program...")
        logs.write("\n==>Start date is more then 13 months back. Max 13 months!")
        logs.write("\n==>Exiting program...")
        lastDayMonth = monthrange(year,month)[1]
        exit()

    # Start looping for the number of months, max 13 months
    for _ in range(numberOfMonths):
        lastDayMonth = monthrange(year,month)[1]

        dateFrom = (datetime.strptime(str(day)+"/"+str(month)+"/"+str(year)+" "+hour+":"+minute+":"+seconds,'%d/%m/%Y %H:%M:%S').timestamp() * 1000) + 1*60*60*1000 # plus 1 hour to GMT
        dateTo = datetime.strptime(str(lastDayMonth)+"/"+str(month)+"/"+str(year)+" 23:58:59",'%d/%m/%Y %H:%M:%S').timestamp() * 1000

        logs.write("\n==>Date From: "+str(dateFrom))
        logs.write("\n==>Date To: "+str(dateTo))

        # Get transcripts for the month provided
        getTranscipts(dateFrom,dateTo,url,year,month,contentToRetrieve,interactionType)
        logs.write("\n==>Month "+str(month)+" COMPLETED!\n")

        if firstTime2:
            day = 1
            seconds = "00"
            minute = "00"
            hour = "00"
            firstTime2 = False

        if month == 12:
            year+=1
            month = 1
        else:
            month+=1
        

#####################---STARTS HERE---##############################
start = timeit.default_timer()
interactionTypeListLength = 0

logs = open("logs.txt", "w")

f = open("accounts.json", "r")
data = json.load(f)
accounts = data['accounts']
for x in accounts:
    interactionType = x["interactionType"]
    accountNo = x["accountNo"]
    startDate = x["startDate"]
    endDate = x["endDate"]
    app_key = x["app_key"]
    secret = x["secret"]
    access_token = x["access_token"]
    access_token_secret = x["access_token_secret"]
    contentToRetrieve = x["contentToRetrieve"]

    logs.write("\n*********Beginning Export for the next Account:***********\n")
    logs.write("\n==>Interaction Type: "+interactionType)
    logs.write("\n==>Account No: "+accountNo)
    logs.write("\n==>Start Date: "+startDate)
    logs.write("\n==>End Date: "+endDate)
    logs.write("\n==>Content to Retrieve: "+str(contentToRetrieve)+"\n\n")

    domainUrls = []
    paths = []
    interactionTypeList = []

    if interactionType == 'chat': # Set the correct domain and path depending on user input
        domainUrl = "http://api.liveperson.net/api/account/"+accountNo+"/service/engHistDomain/baseURI.json?version=1.0"
        path = "/interaction_history/api/account/"+accountNo+"/interactions/search?limit=100&sort=start:asc"
        domainUrls.append(domainUrl)
        paths.append(path)
        interactionTypeList.append("chat")
    elif interactionType == 'messaging':
        domainUrl = "http://api.liveperson.net/api/account/"+accountNo+"/service/msgHist/baseURI.json?version=1.0"
        path = "/messaging_history/api/account/"+accountNo+"/conversations/search?limit=100&sort=start:asc"
        domainUrls.append(domainUrl)
        paths.append(path)
        interactionTypeList.append("messaging")
    elif interactionType == "":
        domainUrl = "http://api.liveperson.net/api/account/"+accountNo+"/service/engHistDomain/baseURI.json?version=1.0"
        path = "/interaction_history/api/account/"+accountNo+"/interactions/search?limit=100&sort=start:asc"
        domainUrl2 = "http://api.liveperson.net/api/account/"+accountNo+"/service/msgHist/baseURI.json?version=1.0"
        path2 = "/messaging_history/api/account/"+accountNo+"/conversations/search?limit=100&sort=start:asc"
        domainUrls.append(domainUrl)
        domainUrls.append(domainUrl2)
        paths.append(path)
        paths.append(path2)
        interactionTypeList.append("chat")
        interactionTypeList.append("messaging")

    headers = {"content-type": "application/json"}
    oauth = OAuth1(app_key,
                client_secret=secret,
                resource_owner_key=access_token,
                resource_owner_secret=access_token_secret
    )

    interactionTypeListLength = len(interactionTypeList)
    for domainUrl, path, interaction in zip(domainUrls, paths,interactionTypeList):
        interactionType = interaction
        domainResponse = requests.get(domainUrl)
        logs.write("\n----"+interactionType+" Export Started!----\n")
        try:                                            #Try getting the baseURI, if error then print error and exit program
            baseURI = domainResponse.json()["baseURI"]
        except:
            print("\n==>Error: "+str(domainResponse.json())+"\n")
            logs.write("\n#######=>Error: "+str(domainResponse.json())+"\n")
            exit()

        logs.write("\n==>"+interactionType+" URI: "+baseURI+" path: "+path+"\n")

        url = "https://"+baseURI+path
        startTranscripts(startDate,endDate,contentToRetrieve,interactionType)
        logs.write("\n----"+interactionType+" Export Completed!-----\n")
try:
    stop = timeit.default_timer()
    TimeTaken = stop - start
    logs.write("\n\n==>Time: "+ str(TimeTaken)+" seconds\n") 
    logs.write("\n\n************* Export Completed! THE END! *************")
    logs.close()
except:
    pass