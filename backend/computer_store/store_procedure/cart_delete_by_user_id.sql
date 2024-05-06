-- author: pakusadewa
-- date  : 6 Mei 2024
-- change: init SP


-- history
-- author       |  date         | description
-- pakusadewa   |  6 Mei 2024   | init SP

DELIMITER //
DROP PROCEDURE IF EXISTS cart_delete_by_user_id;
CREATE PROCEDURE cart_delete_by_user_id(id int)
BEGIN
    DELETE FROM computer_store_cartmodel WHERE user_id = id;    
END//
DELIMITER ;