import requests
import re

import os
import json
import time


ipsites = ('http://ipecho.net/plain',
           'http://ipinfo.io/ip')

class Ddns(object):
    def __init__(self):
        self.ready = False

        self.ipsites_idx = 0
        self.apibase ="https://api.cloudflare.com/client/v4"

        try:
            self.email = os.environ['CF_EMAIL']
            self.key = os.environ['CF_APIKEY']
            self.domain = os.environ['CF_DDNS_DOMAIN']
        except:
            print("Parameter is missing")
            print("")
            print("CF_EMAIL: cloudflare email address")
            print("CF_APIKEY: cloudflare apikey")
            print("CF_DDNS_DOMAIN: ddns domain for ddns")

            return

        self.get_zone_id()
        try:
            self.get_arecord_id()
        except:
            self.create_arecord()

        self.ready = True

    def get_zone_id(self):
        url = "%s/zones?status=active" % (self.apibase)

        headers = {}
        headers['X-Auth-Email'] = self.email
        headers['X-Auth-Key'] = self.key
        headers['Content-Type'] = 'application/json'
    
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            raise Exception('Zone ID retrival failed')
    
        results = r.json()
        if not results['success']:
            raise Exception('Zone ID retrival failed')
    
        for zone in results['result']:
            match = re.match('.*'+zone['name']+'$', self.domain)
            if match is not None:
                self.zone_id = zone['id']
                return
    
        raise Exception('Zone ID retrival failed')
    
    def get_arecord_id(self):
        url = "%s/zones/%s/dns_records?type=A&name=%s"%(self.apibase, self.zone_id, self.domain)
    
        headers = {}
        headers['X-Auth-Email'] = self.email
        headers['X-Auth-Key'] = self.key
        headers['Content-Type'] = 'application/json'
    
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            raise Exception('A Record ID retrival failed')
    
        results = r.json()
        if not results['success']:
            raise Exception('A Record ID retrival failed')
    
        for zone in results['result']:
            self.arecord_id = zone['id']
            return
    
        raise Exception('A Record ID retrival failed')
    
    def get_ip(self):
        url = "%s/zones/%s/dns_records/%s" % (self.apibase, self.zone_id, self.arecord_id)

        headers = {}
        headers['X-Auth-Email'] = self.email
        headers['X-Auth-Key'] = self.key
        headers['Content-Type'] = 'application/json'
    
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            return None
    
        results = r.json()
        if not results['success']:
            return None
    
        return results['result']['content']
    
    def create_arecord(self):
        url = "%s/zones/%s/dns_records" % (self.apibase, self.zone_id)
    
        headers = {}
        headers['X-Auth-Email'] = self.email
        headers['X-Auth-Key'] = self.key
        headers['Content-Type'] = 'application/json'
    
        data = {}
        data['type'] = 'A'
        data['name'] = self.domain
        data['content'] = '127.0.0.1'

        r = requests.post(url, headers=headers, data=json.dumps(data))

        results = r.json()
        if r.status_code != 200:
            raise Exception('A Record creation failed')

        self.arecord_id = results['result']['id']

    def update_ip(self, ip):
        url = "%s/zones/%s/dns_records/%s" % (self.apibase, self.zone_id, self.arecord_id)
    
        headers = {}
        headers['X-Auth-Email'] = self.email
        headers['X-Auth-Key'] = self.key
        headers['Content-Type'] = 'application/json'
    
        data = {}
        data['type'] = 'A'
        data['name'] = self.domain + '.'
        data['content'] = ip 
    
        r = requests.put(url, headers=headers, data=json.dumps(data))
        if r.status_code != 200:
            return False
    
        return True
    
    def get_public_ip(self):
        url = ipsites[self.ipsites_idx]
        self.ipsites_idx = (self.ipsites_idx + 1) % len(ipsites)

        r = requests.get(url)

        if r.status_code != 200:
            return None

        return r.text.strip()

    def run(self):
        if not self.ready:
            return

        old_ip = self.get_ip()
        print("previous ip was " + old_ip)

        while True:
            ip = self.get_public_ip()

            if old_ip != ip and ip is not None:
                print("ip changed to " + ip + " try to update...")

                if self.update_ip(ip):
                    print("success")
                    old_ip = ip
                else:
                    print("failed")

            time.sleep(60)


if __name__ == "__main__":
    ddns = Ddns()
    ddns.run()
