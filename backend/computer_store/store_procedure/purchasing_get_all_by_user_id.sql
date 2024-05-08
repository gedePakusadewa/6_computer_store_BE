-- author: pakusadewa
-- date  : 8 May 2024
-- change: init SP


-- history
-- author       |  date         | description
-- pakusadewa   |  8 May 2024   | init SP

DELIMITER //
DROP PROCEDURE IF EXISTS purchasing_get_all_by_user_id;
CREATE PROCEDURE purchasing_get_all_by_user_id(in_user_id int)
BEGIN
    SELECT 
        pur.created_date,
        pro.image_url,
        pro.name,
        pud.price,
        pud.quantity,
        pud.total_price    
    FROM computer_store_purchasingmodel AS pur
    INNER JOIN computer_store_purchasingdetailmodel AS pud on pur.purchasing_detail_id = pud.id
    INNER JOIN computer_store_productmodel AS pro on pud.product_id = pro.id
    WHERE user_id = in_user_id
    ORDER BY pur.created_date;
END //
DELIMITER ;