SELECT "productSKU", "productUrl", "productBrand" 
FROM grocery 
WHERE TO_CHAR(updated,'YYYY-MM-DD') > '2023-02-08'
GROUP by "productBrand","productSKU","productUrl"
ORDER by "productBrand" DESC