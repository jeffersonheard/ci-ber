Visualization prototypes for CI-BER
###################################

These prototypes consist of a Django app containing two web-based
visualizations and an indexer.  Right now they are in a fairly unpolished
state, as they are prototypes, but it was suggested that they might be useful,
so they are now out on GitHub.  To setup the prototypes, you will need to do
some hacking.  

First of all, you will need IRODS installed to use the indexer.  I have
included sample indices if all you want to do is verify that you can get the
visualizations running, but running the indexer can be accomplished.  You will
need to have IRODS setup and the ICOMMANDS_HOME environment variable set to the
bin/ directory of the icommands client.  Then you will need to modify
documents.py to point to your IRODS repository.  Run documents.py to generate
an input to the scanner then run::
	
	$ ./scan.py documents.json | ./process.py host port num_processes

Once you have indices, copy the dat and idx files created to the app directory
and move the app directory to a working django install and go about the normal
process of configuring app endpoints.  You can simply include() the app.urls
module in your main urls.py under some suitable endpoint.  You will need to
modify views.py to point to the app directory, as some of the paths are also
hardcoded.  My apologies. 


