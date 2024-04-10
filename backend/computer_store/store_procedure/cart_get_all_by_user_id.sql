-- author: pakusadewa
-- date  : 9 April 2024
-- change: init SP


-- history
-- author       |  date         | description
-- pakusadewa   |  9 april 2024 | init SP

DELIMITER //
CREATE PROCEDURE cart_get_all_by_user_id(user_id int)
BEGIN
    SELECT
        p.id,
        p.name, 
        p.image_url,
        p.price,
        c.total_order 
    FROM computer_store_productmodel AS p 
    INNER JOIN computer_store_cartmodel AS c ON p.id = c.product_id
    WHERE c.user_id = user_id;
END//
DELIMITER ;