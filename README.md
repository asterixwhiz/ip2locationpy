
# ip2locationpy

This supporting add-on (SA) for Splunk advanced IP information enrichment using the IP2Location and IP2Proxy databases distributed by IP2Location.  This App was inspired and based on seckit_sa_geolocation developed by Ryan Faircloth.  seckit_sa_geolocation can be found on the Public Splunk github repo https://github.com/splunk/seckit_sa_geolocation and SplunkBase https://splunkbase.splunk.com/app/3022/

Built to work with:

* Linux Host
* IP2Location DB
* IP2Proxy DB

# Installation 

* This application requires Splunk Enterprise or Splunk Enterprise Cloud >=8.0
* This application does not support search head clustering
* Install the IP2Locationpy on each search head
* Navigate to the IP2Locationpy App in the Splunk Web Interface
* Select the configuration tab and update the "main" account with your API token

# USAGE

## Macros

```
| `ip2locationpy(fieldname)`
| `ip2locationpy(fieldname,prefix)`
```

## Example

```
| NOOP | stats count | EVAL src="8.8.4.4" | `ip2locationpy(src)`
```

#Licensing

* Modify this Splunk App code to adheard to any licensing or attribution requirements.