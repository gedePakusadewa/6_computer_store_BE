-- author: pakusadewa
-- date  : 14 May 2024
-- change: init SP


-- history
-- author       |  date         | description
-- pakusadewa   |  14 May 2024  | init SP

DELIMITER //
DROP PROCEDURE IF EXISTS cart_product_update_by_id;
CREATE PROCEDURE cart_product_update_by_id(in_id VARCHAR(32), in_total_order INT)
BEGIN
    UPDATE computer_store_cartmodel
    SET total_order = in_total_order
    WHERE id = in_id;
END//
DELIMITER ;