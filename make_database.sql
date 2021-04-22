DROP DATABASE if exists Store;

CREATE DATABASE Store;
go

USE Store
go


CREATE TABLE Games
(
    game_id int NOT NULL PRIMARY KEY,
    game_name varchar(100) NOT NULL,
    release_date date NOT NULL,
    price money NOT NULL,
    score decimal NOT NULL,
);

CREATE TABLE Orders
(
    order_id int NOT NULL IDENTITY(1,1) PRIMARY KEY,
    order_date date NOT NULL,
    game_id int NOT NULL,
    net_amount money NOT NULL,
    discount decimal NULL,
    gross_amount money NOT NULL,
    FOREIGN KEY (game_id) REFERENCES Games (game_id) ON DELETE CASCADE
);


INSERT into Games 
VALUES
    (1, 'Wiedźmin', '2015-06-15', 150, 100),
    (2, 'Mass Effect 1', '2006-07-10', 200, 70),
    (3, 'Mass Effect 2', '2009-07-10', 200, 96),
    (4, 'Mass Effect 3', '2010-07-10', 200, 101),
    (5, 'Cyberpunk', '2020-12-10', 190, 40),
    (6, 'Civilization VI', '2021-02-10', 300, 90);


INSERT into Orders (order_date, game_id, net_amount, discount, gross_amount)
VALUES
    ('2021-04-10', 3, 190, NULL, 234),
    ('2021-04-11', 4, 300, NULL, 369),
    ('2021-04-12', 1, 150, 30, 148),
    ('2021-04-12', 2, 200, 40, 197),
    ('2021-04-13', 2, 200, 40, 197);

SET IDENTITY_INSERT Orders ON;
