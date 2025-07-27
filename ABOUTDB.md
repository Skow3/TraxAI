USAGE :
1. Logging in to check bookmarks
2. Signup if for the first time

![[Pasted image 20250727103802.png]]

# DB
```sql
-- USERS Table
CREATE TABLE USERS (
    UID INT PRIMARY KEY,
    PHONE_NUMBER VARCHAR(15),
    NAME VARCHAR(50),
    EMAIL VARCHAR(255),
    TOKEN VARCHAR(255)  // FOR TRAXTELE ONLY
);


-- HOBBIES Table (Each hobby belongs to one user)
CREATE TABLE HOBBIES (
    HID INT PRIMARY KEY,
    UID INT,
    Favs text,
    Timestamp DATETIME,
    FOREIGN KEY (UID) REFERENCES USERS(UID)
);

-- BOOKMARKS Table (Each bookmark belongs to one user)
CREATE TABLE BOOKMARKS (
    BID INT PRIMARY KEY,
    UID INT,
    Location VARCHAR(255),
    Timestamp DATETIME,
    FOREIGN KEY (UID) REFERENCES USERS(UID)
);

```

# INSERTING DEMO DATA

```sql
-- FOR USERS
INSERT INTO USERS (UID, PHONE_NUMBER, EMAIL, NAME) VALUES
(1, '8826314381', 'shivamdav05@gmail.com', 'Shivam Kumar'),
(2, '9863958226', 'purohitkavyaa@gmail.com', 'Kavyaa Purohit'),
(3, '88226314382', 'shiv230102037@iiitmanipur.ac.in', 'Skow');

-- FOR HOBBIES
INSERT INTO HOBBIES (HID, UID, Favs, Timestamp) VALUES
(101, 1, 'Cricket, Football, Kabaddi', '2025-07-20 10:15:00'),
(102, 1, 'Classical Music, Singing, Tabla', '2025-07-21 09:30:00'),
(103, 2, 'Bharatanatyam, Drawing, Reading', '2025-07-22 11:00:00'),
(104, 3, 'Chess, Badminton, Cooking', '2025-07-23 14:45:00');

-- FOR BOOKMARKS 
INSERT INTO BOOKMARKS (BID, UID, Location, Timestamp) VALUES
(201, 1, 'Mumbai', '2025-07-20 17:20:00'),
(202, 2, 'Delhi', '2025-07-21 19:10:00'),
(203, 3, 'Bangalore', '2025-07-22 08:00:00'),
(204, 1, 'Jaipur', '2025-07-23 13:25:00');
```



---
# EXCLUSIVELY FOR TELEGRAM

```sql
CREATE TABLE USERS (
    UID BIGINT PRIMARY KEY,
    PHONE_NUMBER VARCHAR(15),
    NAME VARCHAR(50),
    EMAIL VARCHAR(255),
    TOKEN VARCHAR(64)
);

CREATE TABLE HOBBIES (
    HID INT PRIMARY KEY AUTO_INCREMENT,
    UID BIGINT,
    Favs TEXT,
    Timestamp DATETIME,
    FOREIGN KEY (UID) REFERENCES USERS(UID)
);

CREATE TABLE BOOKMARKS (
    BID INT PRIMARY KEY AUTO_INCREMENT,
    UID BIGINT,
    Location VARCHAR(255),
    Timestamp DATETIME,
    FOREIGN KEY (UID) REFERENCES USERS(UID)
);

```
