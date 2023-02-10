from datetime import datetime
import pytz
import re

debug = False


def parseStripFloat(stringElement, returnType='float'):
    stringElement = re.sub('[^a-zA-Z0-9 \n\.]', '', stringElement)
    if type(stringElement) == str and len(stringElement) > 0:
        return float(stringElement) if returnType == 'float' else stringElement
    else:
        return 0 if returnType == 'float' else ''


def standardizeItemResponse(response):
    if response is None:
        return {}
    return {
        'productSKU': response.get('productSKU', ''),
        'productBrand': response.get('productBrand', None),
        'productName': response.get('productName', ''),
        'productPageRank': response.get('productPosition', None),
        'productUrl': response.get('productUrl', None),
        'dealBadge': response.get('dealBadge', None),
        'loyaltyBadge': response.get('loyaltyBadge', None),
        "productPrice": float(response.get('productPrice', 0)),
        'unitQuantity': parseStripFloat(response.get('unitQuantity', ''), 'string'),
        'unitPrice': float(response.get('unitPrice', 0)),
        "sellPrice'": response.get('sellPrice', None),
        "saved": float(response.get('sellPrice', 0)) - float(response.get('productPrice', 0)) if response.get('sellPrice', 0) > 0 else 0,
        "image": response.get('image', ''),
        "promotionDate": response.get('promotionDate', '') if response.get('promotionDate') else pytz.utc.localize(datetime.now())
    }
