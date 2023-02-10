CREATE TABLE IF NOT EXISTS "grocery" (
    "productSKU" VARCHAR NOT NULL,
    "productBrand" VARCHAR,
    "productName" VARCHAR,
    "productPageRank" VARCHAR NOT NULL,
    "productUrl" VARCHAR,
    "dealBadge" VARCHAR,
    "loyaltyBadge" VARCHAR,
    "productPrice" NUMERIC,
    "unitQuantity" NUMERIC,
    "unitPrice" NUMERIC,
    "sellPrice" NUMERIC,
    "saved" NUMERIC,
    "image" VARCHAR,
    "promotionDate" TIMESTAMP WITH TIME ZONE NOT NULL,
    "updated" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    PRIMARY KEY ("productSKU")
);