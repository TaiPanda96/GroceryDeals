import datetime
import pycron

from Loblaws.ItemsController import imageController, controller

cronJobContainer = {
    'groceryItems': {
        'startMessage': 'Starting Grocery Item Fetch By Category Cron',
        'function': controller
    },
    'itemImages': {
        'startMessage': 'Starting Product Image Backfill Cron',
        'function': imageController
    },

}

def cronJobInit():
    if pycron.is_now('*/5 * * * *') == True:
        print(cronJobContainer['groceryItems']['startMessage']);
        cronJobContainer['groceryItems']['function']();
        print('Cron Job Grocery Item Fetch By Category Completed at time: ', datetime.datetime.now(), '');

    elif pycron.is_now('*/10 * * * *') == True:
        print(cronJobContainer['itemImages']['startMessage']);
        cronJobContainer['itemImages']['function']()
        print('Cron Job Product Image Backfill Completed at time: ', datetime.datetime.now(), '');

    else: return None;