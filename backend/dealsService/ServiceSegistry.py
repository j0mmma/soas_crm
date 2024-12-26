import requests

class ServiceRegistry:
    def __init__(self, name, version, url, registry_url="http://localhost:5002"):
        self.name = name
        self.version = version
        self.url = url
        self.registry_url = registry_url

    def register_service(self):
        """Register or update the service in the registry using the registry API."""
        try:
            payload = {
                "name": self.name,
                "version": self.version,
                "url": self.url,
            }
            response = requests.post(f"{self.registry_url}/services/register", json=payload)
            if response.status_code == 200:
                print(f"Service '{self.name}' registered successfully.")
                return True
            else:
                print(f"Failed to register service: {response.json()}")
                return False
        except requests.RequestException as e:
            print(f"Error registering service: {e}")
            return False

    def deregister_service(self):
        """Deregister the service from the registry using the registry API."""
        try:
            response = requests.post(f"{self.registry_url}/services/deregister/{self.name}")
            if response.status_code == 200:
                print(f"Service '{self.name}' deregistered successfully.")
                return True
            elif response.status_code == 404:
                print(f"Service '{self.name}' not found in the registry.")
                return False
            else:
                print(f"Failed to deregister service: {response.json()}")
                return False
        except requests.RequestException as e:
            print(f"Error deregistering service: {e}")
            return False
