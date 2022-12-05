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


### Known Caveats
1. Integration can not use demisto.executeCommand() [This is a security feature to XSOAR]
2. Integrations can not return/create incidents from DemistoLive


### DemistoLive Interactive (Demisto God Mode)
Use this command to open a live shell interpretter where you can test demisto commands and CommonServerPython Functions in real time.
"python -i sample-automation.py"