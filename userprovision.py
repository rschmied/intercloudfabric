#!/usr/bin/env python
#
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
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
import logging
import pprint



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

debug = 0
verify_ssl = True
admin_username = "admin"
admin_password = "somepassword"
base_url = "https://some.server.com:443/app/api/rest"
admin_apikey = ''


EXIT_FAIL=2
EXIT_SUCCESS=0


def usage(name, code):
	print('Usage:', name, '[options] add | delete userid', file=sys.stderr)
	print('  -d, --debug', file=sys.stderr)
	print('  -e, --email=emailaddress', file=sys.stderr)
	print('  -f, --firstname=firstname', file=sys.stderr)
	print('  -h, --help', file=sys.stderr)
	print('  -j, --json', file=sys.stderr)
	print('  -l, --lastname=lastname', file=sys.stderr)
	print('  -n, --no-ssl-verify', file=sys.stderr)
	return code


def create_password():
	length = 16
	chars = string.ascii_letters + string.digits + '!@#$%^*'
	random.seed = (os.urandom(64))
	return ''.join(random.choice(chars) for i in range(length))


def get_apikey(username, password):
	success = True; e = ''

	# get the API key for the admin user
	payload = {'formatType': 'json', 'opName': 'getRESTKey', 'user': username, 'password': password}
	try:
		result = requests.get(base_url, params=payload, verify=verify_ssl)
	except requests.exceptions.SSLError as e:
		success = False
	
	# 200 if we got a valid key
	if not success or result.status_code != 200:
		print(e, file=sys.stderr)
		return ''
	else:
		if debug:
			print(result.status_code, file=sys.stderr)
		return result.json()


def add_group(groupname):
	# create group
	headers = {'X-Cloupia-Request-Key': admin_apikey}
	opdata  = {
		'param0': groupname,			# Name
		'param1': '',					# Description
		'param2': '',					# First Name
		'param3': '',					# Last Name
		'param4': 'no-reply@cisco.com'	# Contact Email 
	}
	payload = {
		'formatType': 'json', 
		'opName': 'userAPIAddGroup', 
		'opData': json.dumps(opdata)
	}
	result = requests.get(base_url, params=payload, headers=headers, verify=verify_ssl)
	return result


def add_user(data):
	# create user
	password = create_password()
	headers = {'X-Cloupia-Request-Key': admin_apikey}
	opdata  = {
		'param0': data['userid'],			# username
		'param1': password,					# password
		'param2': data['firstname'],		# first name
		'param3': data['lastname'],			# last name
		'param4': data['email'],			# email address
		'param5': 'Regular',				# user role
		'param6': 'Default Group'			# group name
	#	'param6': 'group-'+data['userid']	# group name
	}
	payload = {
		'formatType': 'json', 
		'opName': 'userAPIAddUser', 
	#	'opData': json.dumps(opdata, separators=(',', ':')).replace('"', "'")
	#	'opData': json.dumps(opdata, separators=(',', ':'))
		'opData': json.dumps(opdata)
	}
	if debug:
		print(opdata, file=sys.stderr)
	result = requests.get(base_url, params=payload, headers=headers, verify=verify_ssl)
	return [result, password]


def show_vms_for_user(api_key):
	headers = {'X-Cloupia-Request-Key': api_key}
	#payload = {'formatType': 'json',
	payload = {
		'opName': 'Intercloud:userAPIGetAllVms'
	}
	result = requests.get(base_url, params=payload, headers=headers, verify=verify_ssl)
	pp = pprint.PrettyPrinter(indent=2)
	pp.pprint(result.json())
	

def delete_user(data):
	# show VMs (if any)
	# show_vms_for_user(api_key)

	# delete user
	headers = {'X-Cloupia-Request-Key': admin_apikey}
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
	result = requests.get(base_url, params=payload, headers=headers, verify=verify_ssl)
	return result


def enable_logging():
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


def fix_json_result(data):
	#
	# FIXME
	# all this replace() stuff is a workaround
	# API call does not return valid JSON
	# it returns a print of the python data structure!
	#
	if debug:
		print(data, file=sys.stderr)
	temp = str(data).replace("u'", '"')
	temp = temp.replace("'",'"')
	temp = temp.replace("None","null")
	temp = temp.replace("True","true")
	if debug:
		print(temp, file=sys.stderr)
	return temp


def print_result(result):
	print("*"*45)
	if result['success']:
		print("Success!")
		print("User-ID :", result['userid'])
		print("Password:", result['password'])
		print("API Key :", result['apikey'])
	else:
		print("Error:", result['error'])
	print("*"*45)


def main(argv):

	global debug, verify_ssl, admin_apikey

	provision = {
		'email': 'noreply@cisco.com',
		'firstname': 'Firstname',
		'lastname': 'Lastname',
		'userid': ""
	}
	jsonoutput = False


	opresult  = {
		'success': False,   # success of operation (Boolean)
		'userid': '',       # user-id (as supplied)
		'password': '',     # created password for user (empty for delete operation)
		'apikey': '',       # created API key for user (empty for delete operation)
		'error': None		# returned error, if any
	}


	try:
		opts, args = getopt.gnu_getopt(argv[1:],"de:f:hjl:n",["debug","email=","first=","help","json","last=","no-ssl-verify"])
	except getopt.GetoptError:
		return usage(argv[0], EXIT_FAIL)


	for opt, arg in opts:
		if opt in ('-h', '--help'):
			return usage(argv[0], 0)
		elif opt in ("-d", "--debug"):
			debug = True
			enable_logging()
		elif opt in ("-e", "--email"):
			provision['email'] = arg
		elif opt in ("-f", "--first"):
			provision['firstname'] = arg
		elif opt in ("-l", "--last"):
			provision['lastname'] = arg
		elif opt in ("-j", "--json"):
			jsonoutput = True
		elif opt in ("-n", "--no-ssl-verify"):
			# fix me on the server side!!!!
			requests.packages.urllib3.disable_warnings()
			verify_ssl = False			
	
	# get the command that we need to execute
	try:
		command = args.pop(0)
	except IndexError:
		return usage(argv[0], EXIT_FAIL)
	if not command in [ 'add', 'delete' ]:
		return usage(argv[0], EXIT_FAIL)

	# get the userid we should use
	try:
		provision['userid'] = args.pop(0)
	except IndexError:
		return usage(argv[0], EXIT_FAIL)

	# retrieve the admin API key
	admin_apikey = get_apikey(admin_username, admin_password)
	if len(admin_apikey) == 0:
		return EXIT_FAIL

	if command == 'add':
		# result = add_group('group-'+provision['userid'])
		result = add_user(provision)
		data = json.loads(fix_json_result(result[0].json()))
		opresult['success']  = (data['serviceError'] == None)
		opresult['userid']   = provision['userid']
		opresult['password'] = result[1]
		opresult['error']    = data['serviceError']
		if opresult['success']:
			opresult['apikey'] = get_apikey(opresult['userid'], opresult['password'])
		
	elif command == 'delete':
		# result = delete_group('group-'+provision['userid'])
		result = delete_user(provision)
		data = json.loads(fix_json_result(result.json()))
		opresult['success']  = (data['serviceError'] == None)
		opresult['userid']   = provision['userid']
		opresult['error']    = data['serviceError']

	# print result
	if jsonoutput:
		print(json.dumps(opresult))
	else:
		print_result(opresult)

	# make exit status happy
	if opresult['success']:
		return EXIT_SUCCESS
	else:
		return EXIT_FAIL

if __name__ == "__main__":
   sys.exit(main(sys.argv))
