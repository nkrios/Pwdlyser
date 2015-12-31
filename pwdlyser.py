#! /usr/bin/env python3

''' 
To Do:

* Identify domain admins/admins/etc from an imported list (take admin list, highlight any of those).
* Identify multiple shared passwords.
* Fix -oR reporting stdout output.
* Dollar dollar bill y'all
'''

import sys, os
import argparse
from string import digits
import re
from collections import Counter
from collections import defaultdict

parser = argparse.ArgumentParser(description='Password Analyser')
parser.add_argument('-p','--pass-list',dest='pass_list',help='Enter the path to the list of passwords, either in the format of passwords, or username:password.',required=True)
parser.add_argument('-a','--admin-list',dest='admin_list',help='Enter the path to the list of admin accounts that will be highlighted if they are seen within the password list',required=False)
parser.add_argument('-o','--org-name',dest='org_name',help='Enter the organisation name to identify any users that will be using a variation of the word for their password. Note: False Positives are possible',required=False)
parser.add_argument('-l','--length',dest='min_length',help='Display passwords that do not meet the minimum length',type=int)
parser.add_argument('-A','--all',dest='print_all',help='Print only usernames',action='store_true')
parser.add_argument('-s','--search',dest='basic_search',help='Run a basic search using a keyword. Non-alpha characters will be stripped, i.e. syst3m will become systm (although this will be compared against the same stripped passwords')
parser.add_argument('-oR',dest='output_report',help='Output format set for reporting with "- " prefix',action='store_true',default=False)
parser.add_argument('-c','--common',dest='common_pass',help='Check against list of common passwords',action='store_true',default=False)
parser.add_argument('-f','--freq',dest='freq_anal',help='Perform frequency analysis',required=False,type=int)
parser.add_argument('--exact',dest='exact_search',help='Perform a search using the exact string.')
parser.add_argument('-u','--user',dest='user_search',help='Return usernames that match string (case insensitive)')
#parser.add_argument('--shared',dest='shared_pass',help='Display any reused/shared passwords.',required=False,action='store_true',default=False)
args = parser.parse_args()

pass_list = args.pass_list
admin_list = args.admin_list
organisation = args.org_name
issue_old = None

# Input function
def import_file_to_list(path):
    with open(path) as file:
        out_var = file.read().splitlines()
    return out_var

# Output to STDOUT
def output_pass(username,password,issue):
        
    if args.output_report:
         if (issue is not None):
             print ("\n" + issue + ":")
         print ("- " + username)

    else:
        # Username:Pass
        print (username.ljust(50),end=":".ljust(5),flush=True)
        print (password.ljust(35),end=":".ljust(5),flush=True)
        print (issue)

# Check for inputted min length
def check_min_length(password,min):
    if (len(password) < min) or (password == "*******BLANK-PASS*******"):
        output_pass(user,pwd,"Length < " + str(args.min_length))

def check_user_search(user,password,term):
    if term.lower() in user.lower():
        output_pass(user,password,"Username Search: " + term)

def check_exact_search(user,password,term):
    if term in password:
        output_pass(user,password,"Term " + term + " in password")

# Check for org name (reused code from below, laziness)
def check_org_name(user,password,org):
    x = 0
    pwd_unleet = password
    leet_list = reverse_leet_speak()
    for line in leet_list:
        if "," in line:
            char_change = line.split(",")
        else:
            continue
        try:
            pwd_unleet = (pwd_unleet.replace(char_change[0],char_change[1])).lower()
            search = org.lower()
        except:
            continue
    if (search in pwd_unleet): # and (x == 0):
        output_pass(user,password,"Variation of org name " + org)
        #x += 1

# Imports leet config file and processes
def reverse_leet_speak():
    with open("pwd_leet.conf") as leetconf:
        leet_list = leetconf.read().splitlines()
    return leet_list

# Checks for variation of input based upon removal of leetspeak
def check_basic_search(user,password):
    x = 0
    pwd_unleet = password
    leet_list = reverse_leet_speak()
    for line in leet_list:
        if "," in line:
            char_change = line.split(",")
        else:
            continue
        try:
            pwd_unleet = (pwd_unleet.replace(char_change[0],char_change[1])).lower()
            search = args.basic_search.lower()
        except:
            continue
    if (search in pwd_unleet): # and (x == 0):
        output_pass(user,password,"Variation of " + args.basic_search)
        #x += 1

# Common password check from import list - List can be appended to
def check_common_pass(user,password):
    x = 0
    out_issue = ""
    leet_list = reverse_leet_speak()
    pwd_unleet = password

    # Import common passwords
    with open ("pwd_common.conf") as passcommon:
        pass_list = passcommon.read().splitlines()

    # Loop through common passwords list
    for common in pass_list:
        common = common.lower()

        # Loop through each leet_speak change in imported list
        for line in leet_list:
            char_change = line.split(",")

            # Amend each 
            try:
                if char_change[0] in password:
                     pwd_unleet = (pwd_unleet.replace(char_change[0],char_change[1])).lower()
            except:
                continue

        if (common in pwd_unleet) and (x == 0):
            out_issue = "Variation of " + common
            output_pass(user,password,out_issue)
            x += 1

# output and delimit input list
def delimit_list(list):
    list = import_file_to_list(list)
    out_list = []
    for list_entry in list:
        out_list.append(list_entry.split(":"))
    try:
        sorted_list = sorted(out_list, key=lambda x: x[1])
    except:
        sys.exit("ERROR: Cannot delimit list. Ensure format is Username:Password.")
    return (sorted_list)

# Perform frequency analysis for [num]
def check_frequency_analysis(full_list,length):
    z = 0
    pwd_list = []
    words = Counter()

    for pwd in full_list:
        x = pwd[1]
        if x == "":
            x = "*******BLANK-PASS*******"
        pwd_list.append(x)

    words.update(pwd_list)
    wordfreq = (words.most_common())

    for pair in wordfreq:
        if z < length:
            output_pass(pair[0],str(pair[1]),"")
            z += 1

''' 
#def check_shared_pass(full_list):
#    z = 0
#    pwd_list = []
#    words = Counter()

    for pwd in full_list:
        x = pwd[1]
        if x == "":
            x = "*******BLANK-PASS*******"
        pwd_list.append(x)

    words.update(pwd_list)
    wordfreq = (words.most_common())

    comp_list = []
    for pair in wordfreq:
        if z < 10:
            comp_list.append(pair)
            z += 1
    for dup in sorted(list_duplicates(full_list)):
        print (dup)


def list_duplicates(seq):
    tally = defaultdict(list)
    for i,item in enumerate(seq):
        tally[item].append(i)
    return ((key,locs) for key,locs in tally.items() 
                            if len(locs)>1)


#    print (comp_list)

#    seen = set(full_list)
#    uniq = []
#    for q in comp_list:
#        if q[1] not in seen:
#            uniq.append(q)
#            seen.add(q)


#    for l in uniq:
#        output_pass(l[0],str(l[1]),"")
   
'''
 
# Run main stuff
if __name__ == "__main__":

    # Retrieve list
    full_list = (delimit_list(pass_list))
    y = 0

    if args.freq_anal is None:
     
        # Headers
        output_pass("-" * 30,"-" * 30,"-" * 30)
        output_pass("Username","Password","Description")
        output_pass("-" * 30,"-" * 30,"-" * 30)
 
    # Cycle through output list
    for item in full_list:
        # removed above code as pointless to use only passwords
        user = item[0]
        pwd = item[1]
        if pwd == "":
            pwd = "*******BLANK-PASS*******"

        # Print everything regardless
        if args.print_all:
            output_pass(user,pwd,"Not Analysed")
            continue # Skip analysis functions below

        # Check Min Length
        if (args.min_length is not None):
            issue_old = None
            check_min_length(pwd,args.min_length)

        # Check if Org name (or slight variation) is in list
        if organisation is not None:
            issue_old = None
            check_org_name(user,pwd,organisation)

        # Basic search             
        if args.basic_search is not None:
            check_basic_search(user,pwd)

        # Common Passwords
        if args.common_pass is True:
            check_common_pass(user,pwd)

        if args.exact_search is not None:
            check_exact_search(user,pwd,args.exact_search)

        if args.user_search is not None:
            check_user_search(user,pwd,args.user_search)

#    if args.shared_pass:
#        check_shared_pass(full_list)
 
    if args.freq_anal is not None:
        output_pass("-" * 30,"-" * 30,"")
        output_pass("Password","Frequency","")
        output_pass("-" * 30,"-" * 30,"")
        
        check_frequency_analysis(full_list,args.freq_anal)
