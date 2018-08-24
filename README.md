# https://www.google.com/search?client=safari&rls=en&q=prerequisite&ie=UTF-8&oe=UTF-

# Prerequisite

To use blah.<mydomain> for ddns, <mydomain> should be registered to cloudflare

# Usage 

## Native

```
pip install requests

export CF_EMAIL=<your_cloudflare_email> 
export CF_APIKEY=<your_cloudflare_apikey> 
export CF_DDNS_DOMAIN=<domain_for_ddns> 

python ddns.py
```

## Docker

```
docker run -e CF_EMAIL=<your_cloudflare_email>   \
           -e CF_APIKEY=<your_cloudflare_apikey> \
           -e CF_DDNS_DOMAIN=<domain_for_ddns>   \
           -d tee0125/cloudflare-ddns
```
