import time 
from Loblaws.ItemsController import controller, imageController, requestImageWrapper
from CronJobs.Controller import cronJobInit
if __name__ == "__main__":
    start = time.time();
    imageController();
    endtime = time.time();
    print('Execution time in ms', endtime - start)