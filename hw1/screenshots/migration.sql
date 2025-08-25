CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 98d697f6181a

CREATE TABLE `Locations` (
    `LocationID` BIGINT NOT NULL AUTO_INCREMENT, 
    `Country` VARCHAR(50) NOT NULL, 
    PRIMARY KEY (`LocationID`), 
    UNIQUE (`Country`)
);

CREATE TABLE `Interests` (
    `InterestID` BIGINT NOT NULL AUTO_INCREMENT, 
    `Field` VARCHAR(20) NOT NULL, 
    PRIMARY KEY (`InterestID`), 
    UNIQUE (`Field`)
);

CREATE TABLE `Users` (
    `UserID` BIGINT NOT NULL AUTO_INCREMENT, 
    `Age` INTEGER NOT NULL, 
    `Gender` ENUM('Male','Female','Non_Binary') NOT NULL, 
    `LocationID` BIGINT, 
    `SignupDate` DATE, 
    PRIMARY KEY (`UserID`), 
    FOREIGN KEY(`LocationID`) REFERENCES `Locations` (`LocationID`) ON DELETE CASCADE
);

CREATE TABLE `UsersInterests` (
    `UserID` BIGINT NOT NULL, 
    `InterestID` BIGINT NOT NULL, 
    PRIMARY KEY (`UserID`, `InterestID`), 
    FOREIGN KEY(`UserID`) REFERENCES `Users` (`UserID`) ON DELETE CASCADE, 
    FOREIGN KEY(`InterestID`) REFERENCES `Interests` (`InterestID`) ON DELETE CASCADE
);

CREATE TABLE `Campaigns` (
    `CampaignID` BIGINT NOT NULL AUTO_INCREMENT, 
    `CampaignName` VARCHAR(30) NOT NULL, 
    `AdvertiserName` VARCHAR(50) NOT NULL, 
    `CampaignStartDate` DATE NOT NULL, 
    `CampaignEndDate` DATE NOT NULL, 
    `AdSlotSize` VARCHAR(11) NOT NULL, 
    `Budget` FLOAT NOT NULL, 
    `RemainingBudget` FLOAT NOT NULL, 
    `TargetAgeMin` INTEGER NOT NULL, 
    `TargetAgeMax` INTEGER NOT NULL, 
    `TargetInterestID` BIGINT NOT NULL, 
    `TargetLocationID` BIGINT NOT NULL, 
    PRIMARY KEY (`CampaignID`), 
    FOREIGN KEY(`TargetInterestID`) REFERENCES `Interests` (`InterestID`) ON DELETE CASCADE, 
    FOREIGN KEY(`TargetLocationID`) REFERENCES `Locations` (`LocationID`) ON DELETE CASCADE
);

CREATE TABLE `AdEvents` (
    `EventID` CHAR(32) NOT NULL, 
    `UserID` BIGINT, 
    `CampaignID` BIGINT, 
    `Timestamp` DATETIME NOT NULL, 
    `Device` VARCHAR(20) NOT NULL, 
    `BidAmount` FLOAT NOT NULL, 
    `AdCost` FLOAT NOT NULL, 
    `WasClicked` BOOL NOT NULL, 
    `ClickTimestamp` DATETIME, 
    `AdRevenue` FLOAT NOT NULL, 
    PRIMARY KEY (`EventID`), 
    FOREIGN KEY(`UserID`) REFERENCES `Users` (`UserID`) ON DELETE CASCADE, 
    FOREIGN KEY(`CampaignID`) REFERENCES `Campaigns` (`CampaignID`) ON DELETE CASCADE
);

INSERT INTO alembic_version (version_num) VALUES ('98d697f6181a');

