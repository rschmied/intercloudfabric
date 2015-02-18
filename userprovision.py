#!/usr/bin/env python
#
#
# Copyright (c) 2015, Cisco
#
# Permission to use, copy, modify, and/or distribute this software for
# any purpose with or without fee is hereby granted, provided that the
# above copyright notice and this permission notice appear in all
# copies.
# 
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
# WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
# AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL
# DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR
# PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.
#
# rschmied@cisco.com
#

from __future__ import print_function
import requests, json
import getopt, os, sys, random, string

'''
import logging

# These two lines enable debugging at httplib level (requests->urllib3->http.client)
# You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# The only thing missing will be the response.body which is not logged.
try:
	import http.client as http_client
except ImportError:
	# Python 2
	import httplib as http_client
http_client.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig() 
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
'''


# defined user roles for User Creation API call
'''
User Roles:
Regular, 
GroupAdmin, 
Admin, 
AdminIS, 
AdminComputing, 
AdminStorage, 
AdminNetwork, 
AdminAllPolicy, 
Operator, 
MSPAdmin,
BillingAdmin
'''

debug=0
admin_username = "admin"
admin_password = "somepassword"
base_url = "https://some.server.com:443/app/api/rest"

# fix me on the server side!!!!
requests.packages.urllib3.disable_warnings()


def usage(name, code):
   print('Usage:', name, '[-a, -add]|[-d, --delete] [options] userid', file=sys.stderr)
   print('  -e, --email=emailaddress', file=sys.stderr)
   print('  -f, --firstname=firstname', file=sys.stderr)
   print('  -l, --lastname=lastname', file=sys.stderr)
   sys.exit(code)


def create_password():
	length = 16
	chars = string.ascii_letters + string.digits + '!@#$%^*'
	random.seed = (os.urandom(64))
	return ''.join(random.choice(chars) for i in range(length))


def get_apikey(username, password):
	# get the API key for the admin user
	payload = {'formatType': 'json', 'opName': 'getRESTKey', 'user': username, 'password': password}
	result = requests.get(base_url, params=payload, verify=False)
	if debug>0:
		print(result.status_code)

	# 200 if we got a valid key
	if result.status_code != 200:
		print("can't get API key!")
		return ""
	else:
		return result.json()


def add_user(data):
	api_key=get_apikey(admin_username, admin_password)
	if len(api_key) > 0:
		# create user
		password = create_password()
		headers = {'X-Cloupia-Request-Key': api_key}
		opdata  = {
			'param0': data['userid'],		# username
			'param1': password,				# password
			'param2': data['firstname'],	# first name
			'param3': data['lastname'],		# last name
			'param4': data['email'],		# email address
			'param5': 'Regular',			# user role
			'param6': 'somegroup'		# group name
		}
		payload = {
			'formatType': 'json', 
			'opName': 'userAPIAddUser', 
		#	'opData': json.dumps(opdata, separators=(',', ':')).replace('"', "'")
		#	'opData': json.dumps(opdata, separators=(',', ':'))
			'opData': json.dumps(opdata)
		}
		result = requests.get(base_url, params=payload, headers=headers, verify=False)
		return [result, password]


def delete_user(data):
	api_key=get_apikey(admin_username, admin_password)
	if len(api_key) > 0:
		# delete user
		headers = {'X-Cloupia-Request-Key': api_key}
		opdata  = {
			'param0': data['userid'],		# username
		}
		payload = {
			'formatType': 'json', 
			'opName': 'userAPIDeleteUser', 
		#	'opData': json.dumps(opdata, separators=(',', ':')).replace('"', "'")
		#	'opData': json.dumps(opdata, separators=(',', ':'))
			'opData': json.dumps(opdata)
		}
		result = requests.get(base_url, params=payload, headers=headers, verify=False)
		return result


def main(argv):

	provision = {
		'email': 'noreply@cisco.com',
		'firstname': 'Firstname',
		'lastname': 'Lastname',
		'userid': ""
	}

	try:
		opts, args = getopt.getopt(argv[1:],"ade:f:hl:",["add","delete","email=","first=","help","last="])
	except getopt.GetoptError:
		usage(argv[0], 2)

	for opt, arg in opts:
		if opt in ('-h', '--help'):
			usage(argv[0], 0)
		elif opt in ("-a", "--add"):
			command = 'add'
		elif opt in ("-d", "--delete"):
			command = 'delete'
		elif opt in ("-e", "--email"):
			provision['email'] = arg
		elif opt in ("-f", "--first"):
			provision['firstname'] = arg
		elif opt in ("-l", "--last"):
			provision['lastname'] = arg
		elif opt in ("-u", "--userid"):
			provision['userid'] = arg
	
	# get the userid that we want to create / delete
	try:
		provision['userid'] = args.pop(0)
   	except IndexError:
		usage(argv[0], 2)

	if command == 'add':
		if debug>0:
			print(provision)
		
		result = add_user(provision)
		#
		# FIXME
		# all this replace() stuff is a workaround
		# API call does not return valid JSON
		# it returns a print of the python data structure!
		#
		#print(result[0].json())
		aha=str(result[0].json()).replace("u'", '"')
		aha=aha.replace("'",'"')
		aha=aha.replace("None","null")
		aha=aha.replace("True","true")
		#print(aha)
		data = json.loads(aha)
		#print(data)
		if data['serviceError'] != None:
			print("Error:", data['serviceError'])
		else:
			api_key=get_apikey(provision['userid'], result[1])
			print("*"*45)
			if len(api_key) > 0:
				print("Success!")
				print("User-ID :", provision['userid'])
				print("Password:", result[1])
				print("API Key :", api_key)
			else:
				print("Error retrieving API Key")
			print("*"*45)

	elif command == 'delete':
		if debug>0:
			print(provision)
		result = delete_user(provision)
		#
		# FIXME
		# all this replace() stuff is a workaround
		# API call does not return valid JSON
		# it returns a print of the python data structure!
		#
		#print(result[0].json())
		aha=str(result.json()).replace("u'", '"')
		aha=aha.replace("'",'"')
		aha=aha.replace("None","null")
		aha=aha.replace("True","true")
		#print(aha)
		data = json.loads(aha)
		#print(data)
		print("*"*45)
		if data['serviceError'] != None:
			print("Error:", data['serviceError'])
		else:
			print("Success! User '", provision['userid'], "' has been deleted!", sep='')
		print("*"*45)

	else:		
		usage(argv[0], 2)

if __name__ == "__main__":
   main(sys.argv)

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

