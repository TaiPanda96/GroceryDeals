from multiprocessing.pool import ThreadPool
from Requests.BrowserClass import Selenium
from datetime import datetime
from Postgres.GetQuery import getQuery
from Postgres.InsertQuery import insertQuery, updateQuery
from Loblaws.GetItems import parseStripFloat, standardizeItemResponse
import threading
import json
import random 
from Cache.GetCache import Cache, getItemsList
import json
threadLocal = threading.local()

debug = False

def driverInit():
    driver = getattr(threadLocal, 'driver', None);
    if driver is None:
        driver = Selenium.initBrowser();
        if driver:
            setattr(threadLocal, 'driver', driver)

    return driver

def requestImageWrapper(url):
    driver = driverInit();
    soup = Selenium.getHttpChromiumRequestStaticWrapper(url, {
        'xpath': '//*[@id="site-content"]/div/div/div[2]/div[2]/div[1]/div/div[1]/div[2]',
        'waitTime': 30
    }, driver);
    categoryBlock = {
        'cacheKey': "{}:{}:image".format(url, 'refetch'),
        'cacheKeyTimeout': 3600,
        'originalData': {}
    }
    if soup:
        image = soup.find(
            'img', {'class': "responsive-image responsive-image--product-details-page"})
        if image:
            # Assign Image
            imageObj = {"image": image.get('src',''), "productSKU": url.split('/').pop() or ''}
            values   = [tuple(imageObj.values())]
            columns  = ['image']
            if image and debug == True: print('fetched', image)
            return updateQuery('grocery', columns, values, key="productSKU");
        else:
            products = soup.find('div', {"class": "product-image-list product-image-list--product-details-page"})
            if products is None:
                return Cache.addToCache(categoryBlock, True)
            imageSpan = products.find('img', {'class': 'responsive-image responsive-image--product-details-page'})
            if imageSpan is None:
                img = products.find('img')
                if img is None:
                    return Cache.addToCache(categoryBlock, True)
                # Assign Image
                image = imageSpan.get('src', '');
                imageObj = {"image": image, "productSKU": url.split('/').pop() or ''}
                values   = [tuple(imageObj.values())]
                columns  = ['image']
                if image and debug == True: print('fetched', image)
                return updateQuery('grocery', columns, values, key="productSKU");
        
            # Assign Image
            image = imageSpan.get('src', '');
            imageObj = {"image": image, "productSKU": url.split('/').pop() or ''}
            values   = [tuple(imageObj.values())]
            columns  = ['image']
            if image and debug == True: print('fetched', image)
            return updateQuery('grocery', columns, values, key="productSKU")
    else:
        return Cache.addToCache(categoryBlock, True)

def requestWrapper(url):
    driver = driverInit();
    soup   = Selenium.getHttpChromiumRequestStaticWrapper(url, {
        'xpath': '//*[@id="site-content"]/div/div/div[5]/div/div[2]/div[3]',
        'waitTime': 15
    },driver);
    useCategory = url.split('food/')[1].split('/')[0].upper()
    if soup:
        products = soup.find(
            'div', {"class": "product-grid__results__products"})
        productUlArray = products.find_all('li')
        productUlMap = []

        for i in productUlArray:
            productObj = {}
            if i.get('class', '') == ['product-tile-group__list__item']:
                div = i.find('div', {"class": "product-tracking"})
                productLink = i.find('div', {"class": "product-tile__details"})
                sellingPrice = i.find(
                    'div', {"class": "product-prices product-prices--product-tile"})

                comparisonSpan = i.find(
                    'div', {'class': 'product-tile__details__info__section'})
                if div:
                    productSKU = div.get('data-track-products-array', [])
                    if productSKU:
                        product = json.loads(productSKU).pop() if len(
                            json.loads(productSKU)) > 0 else {}
                        productObj = {**product, ** productObj}

                if productLink:
                    link = productLink.find(
                        'a', {"class": "product-tile__details__info__name__link"})
                    section = productLink.find(
                        'div', {"class": "product-badge__icon__expiry product-badge__icon__expiry--multi"})
                    href = link.get('href')
                    if href:
                        productObj = {
                            **{'productUrl': 'https://www.loblaws.ca' + href}, ** productObj}

                    if section:
                        promotionEndDate = section.text or ''
                        if len(promotionEndDate.split(' ')) > 0:
                            promotionEndDate = '2023/' + \
                                promotionEndDate.split(' ').pop()
                            useDate = datetime.strptime(
                                promotionEndDate, '%Y/%m/%d')
                            productObj = {
                                **{'promotionDate': useDate}, ** productObj}

                if sellingPrice:
                    sellPriceSpan = sellingPrice.find('span', {
                                                      'class': "price selling-price-list__item__price selling-price-list__item__price--was-price"})
                    if sellPriceSpan:
                        sellPriceDetailSpan = sellPriceSpan.find(
                            'del', {'class': "price__value selling-price-list__item__price selling-price-list__item__price--was-price__value"}) if sellPriceSpan else ''
                        if len(sellPriceDetailSpan) == 0:
                            return
                        sellPrice = parseStripFloat(
                            sellPriceDetailSpan.text or '', 'float')
                        productObj = {
                            **{'sellPrice': sellPrice}, ** productObj}

                if comparisonSpan:
                    ulSpan = comparisonSpan.find(
                        'ul', {'class': 'comparison-price-list comparison-price-list--product-tile'})
                    ulPriceSpan = ulSpan.find(
                        'span', {'class': 'price__value comparison-price-list__item__price__value'}) or None
                    ulBaseQuantitySpan = ulSpan.find(
                        'span', {'class': 'price__unit comparison-price-list__item__price__unit'}) or None

                    if all([ulPriceSpan, ulBaseQuantitySpan]) is not None:
                        unitPrice = parseStripFloat(ulPriceSpan.text, 'float')
                        unitQuantity = ulBaseQuantitySpan.text
                        productObj = {
                            **{'unitPrice': unitPrice, 'unitQuantity': unitQuantity}, ** productObj}

                if len(productObj.keys()) > 0:
                    productUlMap.append(standardizeItemResponse(productObj))

        if len(productUlMap) == 0:
            categoryBlock = {
                'cacheKey': "{}:{}:refetch".format(useCategory, url),
                'cacheKeyTimeout': 3600,
                'originalData': {}
            }
            Cache.addToCache(categoryBlock, True)

        else:
            update = [tuple(item.values()) for item in productUlMap]
            columns = [
                "productSKU",
                "productBrand",
                "productName",
                "productPageRank",
                "productUrl",
                "dealBadge",
                "loyaltyBadge",
                "productPrice",
                "unitQuantity",
                "unitPrice",
                "sellPrice",
                "saved",
                "image",
                "promotionDate"
            ]
            insertQuery('grocery', columns, update)
            print('Completed update for Loblaws Category: {} at {}'.format(
                useCategory, datetime.now()))

def controller():
    promotion = '?sort=relevance&promotions=Multi-Buy&promotions=Price%20Reduction&promotions=PC%20Points&promotions=$1,$2,$3,$4,$5'
    cache = getItemsList()
    urls = [json.loads(i)['originalData']['baseUrl'] +
            promotion for i in cache]
    ThreadPool(5).map(requestWrapper, urls)

def imageController():
    itemsQuery = """SELECT "productUrl" FROM grocery where LENGTH(image) = 0 ORDER BY updated DESC OFFSET $ LIMIT 20 """
    pageOffSet = random.randint(0, 5)
    itemsToUpdate = getQuery(itemsQuery, [pageOffSet])
    urls = [i['productUrl'] for i in itemsToUpdate];
    ThreadPool(5).map(requestImageWrapper, urls)
