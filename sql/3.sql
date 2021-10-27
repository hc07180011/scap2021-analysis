-- portfolio manager 是否有需求
SELECT *
FROM   `responds`
WHERE  `M` = '是'
AND    `A` NOT LIKE '%完全沒聽過%';