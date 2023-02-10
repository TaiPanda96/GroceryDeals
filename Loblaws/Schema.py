from dataclasses import dataclass, asdict, astuple
from Requests.BrowserClass import Selenium
from Cache.GetCache import Cache
from datetime import datetime
import json
import redis 
import pytz

redisClient = redis.Redis(connection_pool=redis.ConnectionPool(host='localhost', port=6379, db=0))
pipeline    = redisClient.pipeline();

@dataclass
class LoblawsItems:
    category: str
    baseUrl:  str
    expire:   str

    def store_cache(self):
        return {'cacheKeyTimeout': 3600,'originalData': asdict(self),'cacheKey': "category:{}:{}".format(self.category,self.baseUrl)}
    
    def store_single_url_cache(self,url):
        self.url = url;
        return Cache.addToCache(self.store_cache())

class Loblaws(Selenium):
      def __init__(self, baseUrl):
        self.baseUrl = baseUrl
        super().__init__(Selenium);
    
      def getAllCategoryUrls(self, promotion = True) -> map:
          soup = self.getHttpChromiumRequestWrapper(self.baseUrl, {
              'xpath': '//*[@id="site-content"]/div/div/div[4]/div',
              'waitTime': 30,
          });
          if len(soup) == 0: return
          return self.storeCategoryURLs(soup,promotion);

      def storeCategoryURLs(self, soup,promotion) -> map:
          """ Parses data and returns in redis friendly save structure"""
          ulSpan = soup.find_all('li');
          links = []
          for i in ulSpan:
              if i.get('class') == ['category-filter-item']:
                  href = i.find('a').get('href');
                  useCategory = href.split('food/')[1].split('/')[0].upper();
                  useBaseUrl = 'https://loblaws.ca' + href
                  links.append({'url': useBaseUrl, 'category': useCategory})
              else: continue ;
        
          try:
            updates = map( lambda x : LoblawsItems(x['category'],x['url'],datetime.strftime(pytz.utc.localize(datetime.now()), '%Y-%m-%d %H:%M:%S.%f')).store_cache(promotion=True), links)
            pipeline.mset({ obj['cacheKey'] : json.dumps(obj) for obj in updates})
            pipeline.execute(raise_on_error=True)
            return True
          except Exception as error:
              print(error)

    

