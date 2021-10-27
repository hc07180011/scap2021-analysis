-- 技術面仔會不會都沒有用API
SELECT *
FROM   `responds`
WHERE  `Q` LIKE '%技術面%'
AND    `A` NOT LIKE '%完全沒聽過%'
AND    `A` NOT LIKE '%實際寫過程式串接 API 執行交易%';