from imports import *
from src.main.service import Service as Prometheus_Client

def initialize(module, config):
    print("=" * 60)
    print(f"Configuring {module}\n")
  
    #
    #$ PROMETHEUS
    #
    if module == "PROMETHEUS":
        if config['HOST'] in LOCALHOST_ADDRESSES:
            Prometheus_Client.initialize(
                "Mansa (Prometheus)",
                int(config['PORT']),
            )
        
            time.sleep(2)

    #
    #$ Connection Test
    #
    if module == "PROMETHEUS":
        try:
            start_time = time.time()
            response = requests.get(f"http://{config['HOST']}:{config['PORT']}/health", timeout=5)
            latency = (time.time() - start_time) * 1000

            if response.status_code == 200:
                print(f"Mansa ({module}) connected to http://{config['HOST']}:{config['PORT']}! ({latency:.2f}ms)")
            else: print(f"Mansa ({module}) returned status {response.status_code}")
                                
        except requests.exceptions.Timeout:
            print(f"Mansa ({module}) connection timeout (5s)")
        except requests.exceptions.ConnectionError:
            print(f"Cannot connect to Mansa ({module}) to http://{config['HOST']}:{config['PORT']}")
        except Exception as e:
            print(f"Mansa ({module}) connection failed: {e}")

    print("=" * 60, "\n")

if __name__ == "__main__":
    #$ STOCKS_API connection test
    start_time = time.time()
    response = requests.get(f"http://{Config.STOCKS_API['HOST']}:{Config.STOCKS_API['PORT']}/health", timeout=5)
    latency = (time.time() - start_time) * 1000

    if response.status_code == 200:
        print(f"Mansa (Stocks API) connected to http://{Config.STOCKS_API['HOST']}:{Config.STOCKS_API['PORT']}! ({latency:.2f}ms)")
    else: print(f"Mansa (Stocks API) returned status {response.status_code}")

    if Config.PROMETHEUS['ENABLED'] == "TRUE":
        initialize("PROMETHEUS", Config.PROMETHEUS)

    while True: time.sleep(1)