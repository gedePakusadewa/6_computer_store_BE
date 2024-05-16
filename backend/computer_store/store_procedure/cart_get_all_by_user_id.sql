-- author: pakusadewa
-- date  : 9 April 2024
-- change: init SP


-- history
-- author       |  date         | description
-- pakusadewa   |  9 april 2024 | init SP
-- pakusadewa   |  16 May 2024  | add column cart id 

DELIMITER //
DROP PROCEDURE IF EXISTS cart_get_all_by_user_id;
CREATE PROCEDURE cart_get_all_by_user_id(user_id int)
BEGIN
    SELECT
        p.id AS 'id_product',
        p.name, 
        p.image_url,
        p.price,
        c.total_order,
        c.id AS 'id_cart'
    FROM computer_store_productmodel AS p 
    INNER JOIN computer_store_cartmodel AS c ON p.id = c.product_id
    WHERE c.user_id = user_id;
END//
DELIMITER ;