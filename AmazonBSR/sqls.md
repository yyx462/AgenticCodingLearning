

```
WITH base_names AS (  
    -- 1. Get the distinct names as a standard column  
    SELECT DISTINCT name  
    FROM amazon_tmp.toolant_Jan_bsr_new  
    ARRAY JOIN bsr_rank_name AS name  
),  
base_names_array AS (  
    -- 2. Convert to an array specifically for the hasAny() function  
    SELECT groupArray(name) AS arr  
    FROM base_names  
)  
SELECT  
    rank_name, max(rank_index) AS max_target_bsr  
FROM amazon_us.product_item  
-- 3. Parallel ARRAY JOIN: unrolls the arrays index-by-index so they stay paired  
ARRAY JOIN  
    `bsr.product_rank_name` AS rank_name,  
    `bsr.product_rank_index` AS rank_index  
WHERE create_time > '2026-02-01'  
  -- 4. Pre-filter rows that contain our target names (Massive performance boost)  
  AND hasAny(`bsr.product_rank_name`, (SELECT arr FROM base_names_array))  
  -- 5. Filter the unnested rows to ONLY the names we care about before aggregating  
  AND rank_name IN (SELECT name FROM base_names)  
GROUP BY rank_name;
```