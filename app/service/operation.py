import requests
import time
import json
from os import path
import ast

from requests.sessions import extract_cookies_to_jar
import values as Values
import logging as log

global source_started_time, source_comment, source_time_spend

def callApi(ticket, token):
    my_headers = {'content-type': 'application/json', 'Authorization' : "Basic {}".format(token)}
    # auth = ('username', 'password')
    source_url = "https://jira.rakuten-it.com/jira/rest/api/2/issue/{}".format(ticket)

    try:
        response = requests.get(source_url, headers = my_headers)
        #, auth=auth
        apiResponse = response.json()
    except:
        raise Exception("Error while consuming the API, Cause: check the api with credentials")
    
    return apiResponse

#### completed in other scenario #####
# def getAllOpenIsuues(source_url, my_headers):
#     try:
#         response = requests.get(source_url, headers = my_headers)
#         print(response.json())
#     except:
#         raise Exception("Error while consuming the API, Cause: check the api with credentials")
    
#     issues = response.json()["issues"]
    
#     file = open("open-ticket.txt", "w")
#     for i in range(0, len(issues)):  
#         keys = issues[i]["key"]
#         file.write(keys + '\n')
#     file.close()

#### completed in other scenario #####
### function to check if the file containing list of tickets exists ###
# def checkFileInRepoAndGetTheList():
#     if path.exists(Values.filename):
#         file = open(Values.filename, "r")
#         lines = file.readlines()
#         # Strips the newline character
#         ticket = []
#         for line in lines:
#             ticket.append(line.strip())
#             # print(ticket)
#             # time.sleep(1)
#     return ticket


def getDestinationProjectId(ticket, token):
    source_url = "https://jira.rakuten-it.com/jira/rest/api/2/issue/{}".format(ticket)
    try:
        response = requests.get(source_url, headers = token)
    except:
        raise Exception("Error while consuming the API, Cause: check the api with credentials")

    SWRSREOPE_TICKET = response.json()["fields"]["customfield_29801"]
    if (SWRSREOPE_TICKET is not None):
        return SWRSREOPE_TICKET
    else:
        return None
        


def getWorkLog(ticket, headers):
    # auth = ('username', 'password')
    source_url = "https://jira.rakuten-it.com/jira/rest/api/2/issue/{}".format(ticket)

    # Source Operation
    try:
        response = requests.get(source_url, headers = headers)
        print(response)
    except:
        raise Exception("Error while consuming the API, Cause: check the api with credentials")

    worklogs = response.json()["fields"]["worklog"]["worklogs"]
    
    return worklogs



# check id of exsting worklog - edit it
def pushWorklogs(source_worklog, destination_ticket, my_headers):
    if(len(source_worklog) == 0):
        print("WorkLog is null..!")
    else:
        #worklog = response.json()
        destination_url = "https://jira.rakuten-it.com/jira/rest/api/2/issue/{}/worklog".format(destination_ticket)
        dest_url_pull = "https://jira.rakuten-it.com/jira/rest/api/2/issue/{}".format(destination_ticket)
        try:
            response = requests.get(dest_url_pull, headers = my_headers)
        except:
            raise Exception("Error while consuming the API, Cause: check the api with credentials")
        dest_worklog = response.json()["fields"]["worklog"]["worklogs"]

        wl_list1 = []
        wl_list2 = []

        for i in range(len(source_worklog)):
            payload = json.dumps({
                    'comment': source_worklog[i]['comment'],
                    'started': source_worklog[i]['started'],
                    'timeSpentSeconds': source_worklog[i]['timeSpentSeconds'],
                })
            wl_list1.append(ast.literal_eval(payload))

        
        for j in range(len(dest_worklog)):
            payload = json.dumps({
                    'comment': dest_worklog[j]['comment'],
                    'started': dest_worklog[j]['started'],
                    'timeSpentSeconds': dest_worklog[j]['timeSpentSeconds'],
                })

            wl_list2.append(ast.literal_eval(payload))

        dict_set1 = set(frozenset(d.items()) for d in wl_list1)
        dict_set2 = set(frozenset (d.items()) for d in wl_list2)

        # print(dict_set1 - dict_set2)
        result = dict_set1 - dict_set2

        if(len(result) == 0):
            print("Worklog is already updated!")
        else:
            value_back = [dict(s) for s in result]

            for i in range(len(value_back)):
                payload = json.dumps({
                    "comment": value_back[i]["comment"],
                    "started": value_back[i]["started"],
                    "timeSpentSeconds": value_back[i]["timeSpentSeconds"],
                })

                print("Updating the WorkLog..!")
                time.sleep(1)
                #Destination Operation
                try:
                    response_post = requests.post(destination_url, data=(payload), headers = my_headers)
                    print(response_post)
                except:
                    raise Exception("Error while consuming the API, Cause: check the api with credentials")

'''
one problem is the started date being same on some ticket if it's getting create within one minute

"created": "2021-10-08T14:52:31.580+0900",
"updated": "2021-10-08T14:52:31.580+0900",
"started": "2021-10-08T11:22:24.822+0900",

there is a chance that i can take created or updated date and convert the timestamp to IST(as those are in JST) to compare with the started time in the destination
but a problem is this may not work for all the time(only will work for first time) as started timestamp will be changed(some seconds will be removed)

have to look into update case as:
when logging a new worklog
for the first time the [started] time of the worklog is being with complete timestamp and
if i'm updating in the worklog then started date is being same but the timestamp seems to be changed.(some seconds and milliseconds getting changed)
eg:
    new
    2021-10-07T16:26:24.673+0900     2021-10-08T09:23:24.424+0900
    updated
    2021-10-07T16:26:00.000+0900     2021-10-08T09:23:00.000+0900

in this case what i can do
i can trim the timestamp to match only hours and seconds with the complete date:
                   source(started)                             destination(started)
=>new          2021-10-07T16:26:24.673+0900                2021-10-07T16:26:24.673+0900
=>updated      2021-10-07T16:26:00.000+0900

so=>           trim(started)=>2021-10-07T16:26     ===     trim(started)=>2021-10-07T16:26  (one way)


in destination : there may be a chance other user may have the same updated time So, i can take the user context(assignee) with comment and log hours


test1:
new
2021-10-07T16:26:24.673+0900
updated
2021-10-07T16:26:00.000+0900
2021-10-07T16:26:00.000+0900
2021-10-07T16:26:00.000+0900

test2:
new:
2021-10-07T17:15:44.387+0900
updated:
2021-10-07T17:15:00.000+0900
'''

'''Before submitting the worklogs the automation need to look into all open issues, 
    where to get open issues the automation needs a user context [token].
    Where i have hardcoded mine to test.
    
    Problem is when actual auutomation will run, who will be the responsible for the above as it is the intial step.
        '''
'''
the worklog will be submitted only the ticket which assignee is the same user of which token is getting retrieved
'''



'''

TEMP-1 (feature)
    -> Temp-2 (task)
        -> Temp-3  (sub-task)


Read the data of timesheet(work-log) from python from 4 different groups

If issue type= new feature

Make a new table :
    Take issue keys one by one:
{call the API and get the result:
From the result get the issue links inside contains
For each link in the contains call the api
From tempo calculate the sum pf hours   


123 -> retrieving worklog -

'''