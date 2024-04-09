-- author: pakusadewa
-- date  : 4 April 2024
-- change: init function


-- history
-- author       |  date         | description
-- pakusadewa   |  4 april 2024 | create function to get product by search value


CREATE OR REPLACE FUNCTION product_get_product_by_search(t_search varchar)

RETURNS TABLE(t_id bigint, t_name varchar, t_image_url varchar, price int, created_by varchar, created_date date, modified_date date, star_review int)

LANGUAGE "plpgsql"
AS $$
BEGIN 
    return query 
        SELECT
            *
        FROM 
            public.computer_store_productmodel
        WHERE
            name ILIKE '%' || t_search || '%';
end;
$$ 