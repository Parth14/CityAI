# Service A - Worker that waits for activation
import time
from browser_api import BrowserUseActivator

def worker_service():
    activator = BrowserUseActivator()
    
    while True:
        if activator.is_active():
            print("Service is active, performing work...")
            # Do your work here
            time.sleep(5)
        else:
            print("Service inactive, waiting...")
            time.sleep(2)

worker_service()