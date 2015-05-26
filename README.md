# README
These scripts are examples for API usage with the [Intercloud Fabric](http://www.cisco.com/go/intercloud) Controller. For additional information see this [document](https://communities.cisco.com/community/developer/networking/cloud-and-systems-management/intercloud-fabric/blog/2015/01/23/getting-start-with-intercloud-fabric-apis).

See the `LICENSE.TXT` for licensing information.

# Files
Here's a list of the files and what they do.

* `userprovision.py` Sample script that adds and deletes users to a Intercloud Fabric Director. At least one the commands 'add' or 'delete' plus a username must be given on the command line. Base URL (controller address) and administrative credentials must be configured within the script. The script will print the userid, the password and the API key if the user creation was successful.
* If no additional option is given, the output is human readable, SSL verification is enabled  and no debug output is generated. These can be controlled via additional options. 


		$ ./userprovision.py --no-ssl-verify add demouser
		*********************************************
		Success!
		User-ID : demouser
		Password: WSB^UY@utzUYb$y$
		API Key : 351D885FB3B745FA9006D2D5D3D0CB8A
		*********************************************
	    $
	    $ ./userprovision.py --no-ssl-verify delete demouser
		*********************************************
		Success!
		User-ID : demouser
		Password: 
		API Key : 
		*********************************************
		$ 
		$ ./userprovision.py 
		Usage: ./userprovision.py [options] add | delete userid
		  -d, --debug
		  -e, --email=emailaddress
		  -f, --firstname=firstname
		  -h, --help
		  -j, --json
		  -l, --lastname=lastname
		  -n, --no-ssl-verify
		$ 

* Additional debug output can be generated using the `--debug` option. If the server has a self signed cert that can't be verified, the `--no-ssl-verify` option is required, otherwise the script will receive an SSL exception.
 
* `README.md` this file.
