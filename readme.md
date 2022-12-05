## Demisto Live

---

Demisto Live is an [unoffical/unsupported] extension of the Demisto class that supports running the Demisto class and other demisto functions locally in an IDE. 


### Configuration
Use the d_live.json file to configure Demisto Live. You can also put configurations environment variables. It is high recommended that you put the API key and Server URL in the environment variables.

You MUST specify an incident, this provides an entry point to pass commands into XSOAR. It will also load the incident data and, if enabled, will post the script results to this incident

| Configuration      | Description |
| ----------- | ----------- |
| API_KEY      | API Key aquire from Settings -> Integrations -> API Key      |
| SERVER_URL   | XSOAR Server URL in https://xxxxxxxxxxx.demisto.com format   |
| INCIDENT_ID  | Incident ID that Demisto Live should load data, post commands, and post results to|
| CACHE_FILE_NAME | If CACHE_CONTEXT is enabled, this is where the Context will be cached between script runs|
|CACHE_CONTEXT | true/false - Whether to load the context from XSOAR on each load, or to cache it locally. (Can save 5-10 seconds between script runs)|
| POST_RESULTS | Post results to the incident specified in INCIDENT_ID. Results will always print to the local IDE |
| ARGS | Args in an object format to pass to the Demisto class |
| PARAMS | Params in an object format to pass to the Demisto class |
| RETRY_COUNT | How many retries to attempt when awaiting a response from a command to XSOAR (Default: 5)|
| RETRY_COUNT | How long to await retries when connecting to XSOAR. (Default: 0.5 seconds)|
| IS_INTEGRATION | true/false - Set the Demisto class to integration mode| 
| VERIFY_SSL | true/false - Validate SSL Certificate when connecting to XSOAR

### How it works
When a demisto method is call, i.e. demisto.executeCommand(), it is posted to an XSOAR incident as a command:
```
!py script=`return_results(demisto.executeCommand(<params>))`
```

Demisto Live then polls for the results of the command, waiting for the results entry to be posted to the incidents. After the entry is received, DemistoLive unpacks it and passes back the results the same as they would come from the Demisto Class.

### Import Scheme
Because the CommonServerPython file is a Monolith and there are various checks for 'demisto' in the script, it has to be imported twice and in a bizarre string of imports. 

The files import order is marked in the prefix of the file, with _0_demistomock.py being the base. If you need to update the CommonServerPython scripts, you can simply copy/paste over the existing CommonServerPython code, just leaving in place the imports on line 1 of each file.

### Known Caveats
1. Integration can not use demisto.executeCommand() [This is a security feature to XSOAR]
2. Integrations can not return/create incidents from DemistoLive


### DemistoLive Interactive (Demisto God Mode)
Use this command to open a live shell interpretter where you can test demisto commands and CommonServerPython Functions in real time.
"python -i sample-automation.py"