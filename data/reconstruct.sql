CREATE DATABASE `mini_project`;


USE `mini_project`;


CREATE TABLE `products` (
id INT NOT NULL auto_increment,
name VARCHAR(100) NOT NULL,
price DECIMAL(5,2) NOT NULL,
PRIMARY KEY (id)
);


CREATE TABLE `couriers` (
id INT NOT NULL auto_increment,
name VARCHAR(100) NOT NULL,
phone VARCHAR(15) NOT NULL,
PRIMARY KEY (id)
);


CREATE TABLE `orders` (
id INT NOT NULL auto_increment,
name VARCHAR(100) NOT NULL,
address VARCHAR(100) NOT NULL,
area VARCHAR(100) NOT NULL,
phone VARCHAR(15) NOT NULL,
courier INT,
status INT NOT NULL,
basket INT,
PRIMARY KEY (id)
);


CREATE TABLE `basket` (
order_id INT NOT NULL,
item INT NOT NULL,
quantity INT NOT NULL
);


CREATE TABLE `status`(
id INT NOT NULL auto_increment,
name VARCHAR(20) NOT NULL,
style VARCHAR(20) NOT NULL,
PRIMARY KEY (id)
);

/* Load Products Table*/
INSERT INTO `products` 
    (id, name, price)
VALUES
    (1,"smoked salmon & scrambled eggs",3.99),
    (2,"big breakfast",4.99),
    (3,"halloumi breakfast",4.99),
    (4,"super scrambled eggs",3.99),
    (5,"eggs & bacon",2.99),
    (6,"bitesize breakfast",2.99),
    (7,"smashed avacado",2.5),
    (8,"breakfast omlette",2.5),
    (9,"breakfast baguette",2.99),
    (10,"breakfast sandwich",2.99),
    (11,"toast & topping",1.5),
    (12,"scottish oat porridge",0.99),
    (13,"toasted teacake & butter",1.5),
    (14,"fish fingers",2.99),
    (15,"kids sausage and mash",2.99),
    (16,"chicken nuggets",2.99),
    (17,"pasta bolognese",2.99),
    (18,"mac & cheese",2.99),
    (19,"cheese & tomato pizza",2.99),
    (20,"crunchy veg sticks",0.79),
    (21,"1/2 jacket potato",1.5),
    (22,"hot chicken baguette",3.99),
    (23,"omlette",2.5),
    (24,"sweet potato fries",1.49),
    (25,"chips",1.49),
    (26,"jacket potato",2.5),
    (27,"soup of the day",2.5),
    (28,"fresh salmon fillet",4.99),
    (29,"spicy bean burger",4.99),
    (30,"bigger breakfast",5.99),
    (31,"bigger halloumi breakfast",5.99),
    (32,"sweet potato katsu curry",4.99),
    (33,"steak and red wine gravy pie",5.5),
    (34,"hand battered fish and chips",5.99),
    (35,"sausage and mash",4.99),
    (36,"cottage pie",4.99),
    (37,"beef lasagne",4.99),
    (38,"mediterranean vegetable lasagne",4.99),
    (39,"latte",2.15),
    (40,"flavoured latte",2.35),
    (41,"cappuccino",2.0),
    (42,"americano",2.15),
    (43,"flat white",2.15),
    (44,"cortado",2.15),
    (45,"mocha",2.15),
    (46,"esspresso",1.99),
    (47,"filter coffee",1.5),
    (48,"chai latte",1.99),
    (49,"hot chocolate",2.15),
    (50,"flavoured hot chocolate",2.35),
    (51,"luxury hot chocolate",2.75),
    (52,"tea",0.99),
    (53,"speciality tea",1.15),
    (54,"iced latte",2.15),
    (55,"frappe",2.75),
    (56,"smoothie",3.5),
    (57,"babyccino",0.5),
    (58,"milk",0.5),
    (59,"pepsi",1.35),
    (60,"pepsi max",1.35),
    (61,"j20 raspberry",1.5),
    (62,"j20 orange",1.5),
    (63,"fruit shoot",0.99),
    (64,"water",0.8),
    (65,"sprite",1.35),
    (66,"apple pie",1.99),
    (67,"ice cream",1.5),
    (68,"sticky toffee pudding",1.99),
    (69,"tiramissu",2.5),
    (70,"butter portion",0.5),
    (71,"honey",0.5),
    (72,"kettle crisps",0.85);


INSERT INTO `couriers`
    (id, name, phone)
VALUES
    (1,"gary",07088047684),
    (2,"michelle",07003658602),
    (3,"paul",07080263774),
    (4,"michael",07972946358),
    (5,"stephanie",07905979618),
    (6,"roger",07739623215),
    (7,"william",07988805560),
    (8,"christine",07981783894),
    (9,"dawn",07737855293),
    (10,"mark",07737855293),
    (11,"glen",07835203237),
    (12,"jemma",07863505523),
    (13,"miller",07851986768);


INSERT INTO `orders`
    (id, name, address, area, phone, courier, status, basket)
VALUES
    (1, "rebecca k ingram","128 north promenade","hr18pa","07033918495", NULL, 1, 1),
    (2, "niamh l mahmood","140 thompsons lane","ph28wn","07031221095", 6, 1, 2),
    (3, "declan j lane","102 newmarket road","de562ad","07705692817", 1, 2, 3);


INSERT INTO `status`
    (name, style)
VALUES
    ("pending", "Blue"),
    ("accepted", "Cyan"),
    ("preparing", "Yellow"),
    ("dispatched", "Green"),
    ("cancelled", "Red"),
    ("delivered", "White");