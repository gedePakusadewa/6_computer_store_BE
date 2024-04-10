-- author: pakusadewa
-- date  : 9 April 2024
-- change: init SP


-- history
-- author       |  date         | description
-- pakusadewa   |  9 april 2024 | init SP

DELIMITER //
DROP PROCEDURE IF EXISTS product_get_product_by_search;
CREATE PROCEDURE product_get_product_by_search(keywords varchar(100))
BEGIN
    SELECT
        *
    FROM 
        computer_store_productmodel
    WHERE
        name LIKE CONCAT('%', keywords, '%');
END //
DELIMITER ;