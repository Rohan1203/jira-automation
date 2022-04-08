import requests
import json
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-st", "--source_ticket", help="Source Ticket ID of the Jira Issue", required=True)
parser.add_argument("-t", "--token", help="Auth token", required=True)
parser.add_argument("-dt", "--destination_ticket", help="Destination Ticket ID of the Jira Issue", required=True)

args = parser.parse_args()

global op_date
my_headers = {'content-type': 'application/json', 'Authorization' : "Basic {}".format(args.token)}
# auth = ('username', 'password')
source_url = "https://jira.rakuten-it.com/jira/rest/api/2/issue/{}".format(args.source_ticket)

# Source Operation
try:
    response = requests.get(source_url, headers = my_headers)
    #, auth=auth
except:
    raise Exception("Error while consuming the API, Cause: check the api with credentials")

#creating a temp file for storing the json response
with open('response_source.json', 'w') as outfile:
    json.dump(response.json(), outfile, sort_keys=True, indent=4)
    outfile.close()

description = response.json()["fields"]["description"]
if(description == None):
    print("Description is Null")
else:
    description_list = description.split("|")
    for i in range(0, len(description_list)):
        if(description_list[i] == "*Operation Date*"):
            if(description_list[i+1] != ""):
                op_date = description_list[i+1]
                print("Operation Date : ", op_date)

                print('Updating the Due Date..!')
                time.sleep(2)

                destination_url = "https://jira.rakuten-it.com/jira/rest/api/2/issue/{}".format(args.destination_ticket)
                payload = json.dumps({'fields':{'duedate':op_date}})

                print(payload)

                #Destination Operation
                try:
                    response_put = requests.put(destination_url, data=(payload), headers = my_headers)
                    print(response_put)
                except:
                    raise Exception("Error while consuming the API, Cause: check the api with credentials")
            else:
                print("Operation Date is not been assigned..!")
        # else:
        #     print("Operation Date is is not been assigned..!")