# README
These scripts are examples for API usage with the [Intercloud Fabric](http://www.cisco.com/go/intercloud) Controller. For additional information see this [document](https://communities.cisco.com/community/developer/networking/cloud-and-systems-management/intercloud-fabric/blog/2015/01/23/getting-start-with-intercloud-fabric-apis).

See the `LICENSE.TXT` for licensing information.

# Files
Here's a list of the files and what they do.

* `userprovision.py` Sample script that adds and deletes users to a Intercloud Fabric Director. At least '-a / --add' or '-d / --delete' plus a username must be given on the command line. Base URL (controller address) and administrative credentials must be configured within the script. The script will print the userid, the password and the API key if the user creation was successful.
* `README.md` this file.
