-- author: pakusadewa
-- date  : 10 Mei 2024
-- change: init SP


-- history
-- author       |  date         | description
-- pakusadewa   |  10 Mei 2024   | init SP

DELIMITER //
DROP PROCEDURE IF EXISTS demo_user_delete_all_data;
CREATE PROCEDURE demo_user_delete_all_data(in_username VARCHAR(100))
BEGIN
	DECLARE var_user_id INT DEFAULT 0;
		
	SELECT id FROM auth_user WHERE username = in_username INTO var_user_id;

	CREATE TEMPORARY TABLE purchasing_detail_id_table
    SELECT purchasing_detail_id
    FROM computer_store_purchasingmodel
    WHERE user_id = var_user_id;
    
	DELETE FROM  computer_store_purchasingmodel
	WHERE user_id = var_user_id;

	DELETE FROM computer_store_purchasingdetailmodel
	WHERE id IN (SELECT purchasing_detail_id FROM purchasing_detail_id_table);

	DROP TABLE purchasing_detail_id_table;
END//
DELIMITER ;