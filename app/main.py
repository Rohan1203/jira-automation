import argparse
from service.operation import *
import values as Values
import logging as log

parser = argparse.ArgumentParser()
parser.add_argument("-ticket", "--ticket", help="Ticket ID of the Jira Issue", required=True)
parser.add_argument("-token", "--token", help="Auth token", required=True)
parser.add_argument("-username", "--username", help="Username of the ticket", required=False)

args = parser.parse_args()

ticket = args.ticket
header = {'content-type': 'application/json', 'Authorization': 'Basic {}'.format(args.token)}
Values.my_headers = header

# print("[{}]".format(ticket))
# print("[{}]".format(header))

def main(ticket, header):
    worklog = getWorkLog(ticket, header)
    if(getDestinationProjectId(ticket, header) is not None):
        pushWorklogs(worklog, getDestinationProjectId(ticket, header), header)
    else:
        log.warning("Master ticket not available!")
        log.warning("Skipping the ticket [{}]!".format(ticket))
        #pushWorklogs(worklog, "CUS-31", header)

        

if __name__ == "__main__":
    start_time = time.time()
    main(ticket, header)
    print("--- Processed in %.4f seconds ---" % (time.time() - start_time))


