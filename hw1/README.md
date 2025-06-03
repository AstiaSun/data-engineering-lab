### 1. DDL scripts
**Users** table was normalised and redundant fields were removed:
```commandline
data-loader-1  | 2025-06-03 21:40:16,071 INFO sqlalchemy.engine.Engine 
data-loader-1  | CREATE TABLE `Users` (
data-loader-1  |        `UserID` BIGINT NOT NULL AUTO_INCREMENT, 
data-loader-1  |        `Age` INTEGER NOT NULL, 
data-loader-1  |        `Gender` ENUM('Male','Female','Non_Binary') NOT NULL, 
data-loader-1  |        `Location` VARCHAR(30) NOT NULL, 
data-loader-1  |        PRIMARY KEY (`UserID`)
data-loader-1  | )
data-loader-1  |
data-loader-1  |
data-loader-1  | 2025-06-03 21:40:16,074 INFO sqlalchemy.engine.Engine [no key 0.00003s] {}
data-loader-1  | 2025-06-03 21:40:16,078 INFO sqlalchemy.engine.Engine
data-loader-1  | CREATE TABLE `UsersInterests` (
data-loader-1  |        `UserID` BIGINT NOT NULL,
data-loader-1  |        `Interest` VARCHAR(20) NOT NULL,
data-loader-1  |        PRIMARY KEY (`UserID`, `Interest`),
data-loader-1  |        FOREIGN KEY(`UserID`) REFERENCES `Users` (`UserID`)
data-loader-1  | )
data-loader-1  |
```
There's no extra table for interests, because creating one for only one field seems redundant.

In **Campaigns** field TargetCriteria was parsed and split into separate columns to structure the data:
```commandline
data-loader-1  | 2025-06-03 21:40:16,071 INFO sqlalchemy.engine.Engine [no key 0.00003s] {}
data-loader-1  | 2025-06-03 21:40:16,074 INFO sqlalchemy.engine.Engine
data-loader-1  | CREATE TABLE `Campaigns` (
data-loader-1  |        `CampaignID` BIGINT NOT NULL AUTO_INCREMENT,
data-loader-1  |        `AdvertiserName` VARCHAR(50) NOT NULL,
data-loader-1  |        `CampaignName` VARCHAR(30) NOT NULL,
data-loader-1  |        `CampaignStartDate` DATE NOT NULL,
data-loader-1  |        `CampaignEndDate` DATE NOT NULL,
data-loader-1  |        `AdSlotSize` VARCHAR(11) NOT NULL,
data-loader-1  |        `Budget` FLOAT NOT NULL,
data-loader-1  |        `RemainingBudget` FLOAT NOT NULL,
data-loader-1  |        `TargetAgeMin` INTEGER NOT NULL,
data-loader-1  |        `TargetAgeMax` INTEGER NOT NULL,
data-loader-1  |        `TargetInterest` VARCHAR(15) NOT NULL,
data-loader-1  |        `TargetLocation` VARCHAR(50) NOT NULL,
data-loader-1  |        PRIMARY KEY (`CampaignID`)
data-loader-1  | )
```

Redundant data was removed from `AdEvents` and `CampaignID` was set instead od duplicated campaign data:
```commandline
data-loader-1  | 2025-06-03 21:40:16,078 INFO sqlalchemy.engine.Engine [no key 0.00006s] {}
data-loader-1  | 2025-06-03 21:40:16,082 INFO sqlalchemy.engine.Engine
data-loader-1  | CREATE TABLE `AdEvents` (
data-loader-1  |        `EventID` CHAR(32) NOT NULL,
data-loader-1  |        `CampaignID` BIGINT NOT NULL,
data-loader-1  |        `UserID` BIGINT NOT NULL,
data-loader-1  |        `Timestamp` DATETIME NOT NULL,
data-loader-1  |        `Device` VARCHAR(10) NOT NULL,
data-loader-1  |        `BidAmount` FLOAT NOT NULL,
data-loader-1  |        `AdCost` FLOAT NOT NULL,
data-loader-1  |        `WasClicked` BOOL NOT NULL,
data-loader-1  |        `ClickTimestamp` DATETIME,
data-loader-1  |        `AdRevenue` FLOAT NOT NULL,
data-loader-1  |        PRIMARY KEY (`EventID`),
data-loader-1  |        FOREIGN KEY(`CampaignID`) REFERENCES `Campaigns` (`CampaignID`),
data-loader-1  |        FOREIGN KEY(`UserID`) REFERENCES `Users` (`UserID`)
data-loader-1  | )

```

### 2. Screenshots of data in DB

Screenshots can be found [here](./screenshots)