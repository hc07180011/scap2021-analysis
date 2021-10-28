-- 21-40歲 + 注重效率 + 有台股交易需求
SELECT *
FROM   responds
WHERE  (`X` = '21-30歲' OR `X` = '31-40歲')
AND    `D` LIKE '%能省去大量觀盤及執行交易的時間%'
AND    `N` LIKE '%台股市場%';