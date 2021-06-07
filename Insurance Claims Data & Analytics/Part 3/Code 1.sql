CREATE DATABASE ICDA;
USE ICDA;
CREATE TABLE `vtinp16_upd` (
    `hnum2` text DEFAULT NULL,
    `ATYPE` INT DEFAULT NULL,
    `asour` INT DEFAULT NULL,
    `intage` INT DEFAULT NULL,
    `TXTZIP` TEXT,
    `sex` INT DEFAULT NULL,
    `dstat` INT DEFAULT NULL,
    `PPAY` INT DEFAULT NULL,
    `CHRGS` DOUBLE DEFAULT NULL,
    `DX1` TEXT,
    `DX2` TEXT,
    `DX3` TEXT,
    `DX4` TEXT,
    `DX5` TEXT,
    `DX6` TEXT,
    `DX7` TEXT,
    `DX8` TEXT,
    `DX9` TEXT,
    `DX10` TEXT,
    `DX11` TEXT,
    `DX12` TEXT,
    `DX13` TEXT,
    `DX14` TEXT,
    `DX15` TEXT,
    `DX16` TEXT,
    `DX17` TEXT,
    `DX18` TEXT,
    `DX19` TEXT,
    `DX20` TEXT,
    `PX1` TEXT,
    `PX2` TEXT,
    `PX3` TEXT,
    `PX4` TEXT,
    `PX5` TEXT,
    `PX6` TEXT,
    `PX7` TEXT,
    `PX8` TEXT,
    `PX9` TEXT,
    `PX10` TEXT,
    `PX11` TEXT,
    `PX12` TEXT,
    `PX13` TEXT,
    `PX14` TEXT,
    `PX15` TEXT,
    `PX16` TEXT,
    `PX17` TEXT,
    `PX18` TEXT,
    `PX19` TEXT,
    `PX20` TEXT,
    `ECODE1` TEXT,
    `ECODE2` TEXT,
    `ECODE3` TEXT,
    `hsa` text DEFAULT NULL,
    `pdays` INT DEFAULT NULL,
    `ccsdx` INT DEFAULT NULL,
    `ccsdxgrp` INT DEFAULT NULL,
    `CCSPX` TEXT,
    `CCSPXGRP` TEXT,
    `ccsppx` TEXT,
    `ccsppxgrp` TEXT,
    `ccsproc` TEXT,
    `ccsprocgrp` TEXT,
    `DY` INT DEFAULT NULL,
    `RECNO` INT DEFAULT NULL,
    `BTYPE` INT DEFAULT NULL,
    `ERFLAG` INT DEFAULT NULL,
    `cah` INT DEFAULT NULL,
    `vtres` INT DEFAULT NULL,
    `OBSFLAG` INT DEFAULT NULL,
    `AFLAG` INT DEFAULT NULL,
    `UNIQ` INT DEFAULT NULL,
    `ADMID_QTR` INT DEFAULT NULL,
    `DISCD_QTR` INT DEFAULT NULL,
    `CHRGS_HCIA` DOUBLE DEFAULT NULL,
    `SCUD` TEXT,
    `DRG` INT DEFAULT NULL,
    `MDC` INT DEFAULT NULL,
    `sdf` INT DEFAULT NULL,
    `GROUPER` INT DEFAULT NULL
)  ENGINE=MYISAM DEFAULT CHARSET=UTF8MB4 COLLATE = UTF8MB4_0900_AI_CI;

# Importing data from the CVS file
LOAD DATA INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\vtinp16_upd.csv' 
INTO TABLE    vtinp16_upd
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\r\n' ignore 1 lines;

CREATE TABLE `vtrevcode16` (
    `dy` INT DEFAULT NULL,
    `hnum2` INT DEFAULT NULL,
    `DISCD_QTR` INT DEFAULT NULL,
    `BTYPE` INT DEFAULT NULL,
    `Uniq` INT DEFAULT NULL,
    `REVCODE` INT DEFAULT NULL,
    `REVCHRGS` INT DEFAULT NULL,
    `REVUNITS` INT DEFAULT NULL,
    `CPT` TEXT,
    `PCCR` INT DEFAULT NULL,
    `PRIMARY_CPT` INT DEFAULT NULL,
    `SFLAG` INT DEFAULT NULL,
    `ccsproc` TEXT,
    `ccsprocgrp` TEXT
)  ENGINE=MYISAM DEFAULT CHARSET=UTF8MB4 COLLATE = UTF8MB4_0900_AI_CI;

# Importing data from the CVS file
LOAD DATA INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\vtrevcode16.txt' 
INTO TABLE    vtrevcode16
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\r\n' ignore 1 lines;

# Selecting only important DRG from 20 to 977 (inclusive)
drop temporary table vtinp_16_s;
Create temporary table vtinp_16_s
Select * from vtinp16_upd where drg between 20 and 977;
Select count(distinct(DRG)) from vtinp_16_s; #702 DRG

# filtering the revcodes with charges less than 100 usd 
create temporary table vtrevcode16_filtered;
select * from vtrevcode16
where REVCHRGS>100;
select count(*) from vtrevcode16_filtered; #3,828,913

# linking the two filtered tables
drop temporary table if exists vtinp_rev;
Create temporary table vtinp_rev
select a.REVCHRGS,a.PCCR,a.UNIQ ,b.DRG
from vtrevcode16_filtered as a join vtinp_16_s as b
on a.UNIQ=b.UNIQ; #553,125

# Summing all the charges by the PCCR categories

Create temporary table PCCR_Revcharge
Select UNIQ, DRG, PCCR, Sum(REVCHRGS) as REVCHRGS
From vtinp_rev 
Group By UNIQ, DRG, PCCR; #420,390 rows

select * from PCCR_Revcharge;

# Transfering data to excel for further processing
SELECT * FROM PCCR_Revcharge
INTO OUTFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\PCCR_Revcharge.csv'
FIELDS ENCLOSED BY '"'
TERMINATED BY ';'
ESCAPED BY '"'
LINES TERMINATED BY '\r\n';

