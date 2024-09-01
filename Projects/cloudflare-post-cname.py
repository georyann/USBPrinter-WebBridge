import requests
import json

class CloudFlareDDNSUpdater:
    def __init__(self, auth_email, auth_key, zone_name, record_name, cname_target):
        self.headers = {
            "X-Auth-Email": auth_email,
            "X-Auth-Key": auth_key,
            "Content-Type": "application/json",
        }
        self.zone_name = zone_name
        self.record_name = record_name
        self.cname_target = cname_target
        self.zone_id = self.get_zone_id()
        self.update_cname_record()

    def login_verify(self):
        url = "https://api.cloudflare.com/client/v4/user/"
        res = requests.get(url=url, headers=self.headers)
        data = res.json()

        if not data["success"]:
            print(data["errors"])
            raise Exception("User verification failed")
        else:
            print(f"[+] User {data['result']['username']} verified successfully")

    def get_zone_id(self):
        url = "https://api.cloudflare.com/client/v4/zones"
        res = requests.get(url=url, headers=self.headers)
        data = res.json()

        if not data["success"]:
            print(data["errors"])
            raise Exception("Fetching zones failed")

        for zone in data["result"]:
            if zone["name"] == self.zone_name:
                print(f"[+] Zone ID for {self.zone_name} is {zone['id']}")
                return zone["id"]

        raise Exception(f"Zone {self.zone_name} not found")

    def get_record_id(self):
        url = f"https://api.cloudflare.com/client/v4/zones/{self.zone_id}/dns_records"
        res = requests.get(url=url, headers=self.headers)
        data = res.json()

        if not data["success"]:
            print(data["errors"])
            raise Exception("Fetching DNS records failed")

        for record in data["result"]:
            if record["name"] == self.record_name and record["type"] == "CNAME":
                print(f"[+] Record ID for {self.record_name} is {record['id']}")
                return record["id"]

        return None

    def update_cname_record(self):
        record_id = self.get_record_id()

        if record_id:
            url = f"https://api.cloudflare.com/client/v4/zones/{self.zone_id}/dns_records/{record_id}"
            method = "PUT"
        else:
            url = f"https://api.cloudflare.com/client/v4/zones/{self.zone_id}/dns_records"
            method = "POST"

        data = {
            "type": "CNAME",
            "name": self.record_name,
            "content": self.cname_target,
            "ttl": 1,  # Set TTL to automatic
            "proxied": False
        }

        res = requests.request(method, url, headers=self.headers, data=json.dumps(data))
        result = res.json()

        if result["success"]:
            if record_id:
                print(f"[+] CNAME record {self.record_name} updated successfully")
            else:
                print(f"[+] CNAME record {self.record_name} created successfully")
        else:
            print(result["errors"])
            raise Exception("Updating/Creating CNAME record failed")

if __name__ == "__main__":
    # Replace these variables with your own Cloudflare details and desired CNAME settings
    AUTH_EMAIL = ""
    AUTH_KEY = ""
    ZONE_NAME = ""  # Your domain baidu.com
    RECORD_NAME = ""  # The subdomain you want to update a.baidu.com
    CNAME_TARGET = ""  # The target of the CNAME record

    updater = CloudFlareDDNSUpdater(AUTH_EMAIL, AUTH_KEY, ZONE_NAME, RECORD_NAME, CNAME_TARGET)
