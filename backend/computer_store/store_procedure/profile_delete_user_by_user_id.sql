-- author: pakusadewa
-- date  : 29 April 2024
-- change: init SP


-- history
-- author       |  date         | description
-- pakusadewa   |  29 april 2024 | init SP

DELIMITER //
DROP PROCEDURE IF EXISTS profile_delete_user_by_user_id;
CREATE PROCEDURE profile_delete_user_by_user_id(user_id int)
BEGIN
    DELETE FROM computer_store_cartmodel
    where user_id = user_id;      
END //
DELIMITER ;