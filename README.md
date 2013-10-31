twitter-graph
=============

A tool written in python to extract a twitter user's social graph.

twitter-graph allows you to build a social graph by extracting a twitter user's friend(following) list and friends' friend list. A user followed by more than 5 users in the network is included in the output. Output file is in json format for visualisation using d3.js.

The tool has a self-limiting feature to limit the number of API calls per 15 minute to prevent your app from being black listed. 


Installation
------------


* Copy all files to a directory:  

 * `$ git clone https://github.com/joyanujoy/twitter-graph.git`  

* Obtain an API key by registering a twitter app at dev.twitter.com. Update settings.json file with your app name, consumer key and consumer secret.

* Install Kenneth Reitz's HTTP requests library.
 * `$ pip install requests` or    
 * `$ easy_install requests`

* to run
 * `$ python graph.py settings.json <twitter screen name>`
 * e.g `$ python graph.py settings.json TelegrahLondon`

Due to API restrictions it can make only ~15 API calls per 15 minutes to retrieve friend/ids. It will need a few hours to run against a popular twitter account. e.g 1.5 hours to extract my network from a friend list of 100.

* Output is a json file graph.json in the below format. See the sample file in repository. Degree is the indegree of a graph node .ie the number of followers within the network.
 * 
   ` {`  
    `    "nodes" : [  `
    `                {"name": Name1, "scr_name": Screen Name1, "degree": Degree},`     
    `                {"name": Name2, "scr_name": Screen Name2, "degree": Degree},`    
    `            ],`    
    `    "links" : [`    
    `                {"source": index of source, "target": index of target},`      
    `                {"source": index of source, "target": index of target}`      
    `            ]  `     
    ` }`     

* To view a sample d3.js visualisation run:
 * `$ python -m SimpleHTTPServer 8080`
 * `Point your browser to http://127.0.0.1:8080/graph.html`

graph.html is adapted from Mike Bostock and Scott Murray's d3.js examples. I intend to modify it further once I have learned a bit more about d3.js. See the TODO file
