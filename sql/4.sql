-- 非 API 交易者但會交易的用戶輪廓
SELECT *
FROM   `responds`
WHERE  `A` NOT LIKE '%完全沒聽過%'
AND    `A` NOT LIKE '%實際寫過程式串接 API 執行交易%'
AND    `N` NOT LIKE '%無進行投資%';