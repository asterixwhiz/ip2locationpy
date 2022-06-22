# Welcome

This supporting add-on (SA) for Splunk advanced IP information enrichment using the IP2Location and IP2Proxy databases distributed by IP2Location.  This App is based on seckit_sa_geolocation developed by Ryan Faircloth found on the Public Splunk github https://github.com/splunk/seckit_sa_geolocation.

Built to work with:

* Linux Host
* IP2Location DB
* IP2Proxy DB

# Installation 

* This application requires Splunk Enterprise or Splunk Enterprise Cloud >=8.0
* This application does not support search head clustering
* Install the IP2Locationpy on each search head
* Navigate to the IP2Locationpy in the Splunk Web Interface
* Select the configuration and update the "main" account API token generated for your IP2Location account.

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