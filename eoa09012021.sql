-- MySQL dump 10.13  Distrib 8.0.22, for Linux (x86_64)
--
-- Host: localhost    Database: eoa
-- ------------------------------------------------------
-- Server version	8.0.22-0ubuntu0.20.04.2

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `age_group`
--

DROP TABLE IF EXISTS `age_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `age_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `min_class` int DEFAULT NULL,
  `max_class` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `contest`
--

DROP TABLE IF EXISTS `contest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `contest` (
  `id` int NOT NULL AUTO_INCREMENT,
  `subject_id` int NOT NULL,
  `type_id` int NOT NULL,
  `year_id` int NOT NULL,
  `name` varchar(64) NOT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_subject_idx` (`subject_id`),
  KEY `fk_type_idx` (`type_id`),
  KEY `fk_year_idx` (`year_id`),
  CONSTRAINT `fk_contest_subject` FOREIGN KEY (`subject_id`) REFERENCES `subject` (`id`),
  CONSTRAINT `fk_contest_type` FOREIGN KEY (`type_id`) REFERENCES `type` (`id`),
  CONSTRAINT `fk_contest_year` FOREIGN KEY (`year_id`) REFERENCES `year` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=93 DEFAULT CHARSET=utf8 COMMENT='Üks koos toimuv võistlus - nt. füüsika pkv või keemia lahtine';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `contestant`
--

DROP TABLE IF EXISTS `contestant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `contestant` (
  `id` int NOT NULL AUTO_INCREMENT,
  `subcontest_id` int NOT NULL,
  `person_id` int DEFAULT NULL,
  `age_group_id` int DEFAULT NULL,
  `school_id` int DEFAULT NULL,
  `placement` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_subcontest_idx` (`subcontest_id`),
  KEY `fk_person_idx` (`person_id`),
  KEY `fk_age_group_idx` (`age_group_id`),
  KEY `fk_school_idx` (`school_id`),
  CONSTRAINT `fk_contestant_age_group` FOREIGN KEY (`age_group_id`) REFERENCES `age_group` (`id`),
  CONSTRAINT `fk_contestant_person` FOREIGN KEY (`person_id`) REFERENCES `person` (`id`),
  CONSTRAINT `fk_contestant_school` FOREIGN KEY (`school_id`) REFERENCES `school` (`id`),
  CONSTRAINT `fk_contestant_subcontest` FOREIGN KEY (`subcontest_id`) REFERENCES `subcontest` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8161 DEFAULT CHARSET=utf8 COMMENT='Ühel alamvõistlusel osaleja (seotakse tulemus)\n\nEt inimese omadused (vanusegrupp, kool, juhendajad, ...) võivad tihti muutuda, siis märkida need pigem siia';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `contestant_field`
--

DROP TABLE IF EXISTS `contestant_field`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `contestant_field` (
  `task_id` int NOT NULL,
  `contestant_id` int NOT NULL,
  `entry` varchar(64) NOT NULL,
  PRIMARY KEY (`task_id`,`contestant_id`),
  KEY `fk_contestant_points_1_idx` (`contestant_id`),
  CONSTRAINT `fk_contestant_points_contestant` FOREIGN KEY (`contestant_id`) REFERENCES `contestant` (`id`),
  CONSTRAINT `fk_contestant_points_task` FOREIGN KEY (`task_id`) REFERENCES `subcontest_column` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Ühe võistleja üks väli vastavalt subcontest_column''ile';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mentor`
--

DROP TABLE IF EXISTS `mentor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mentor` (
  `contestant_id` int NOT NULL,
  `mentor_id` int NOT NULL,
  PRIMARY KEY (`contestant_id`,`mentor_id`),
  KEY `fk_mentor_1_idx` (`mentor_id`),
  CONSTRAINT `fk_mentor_contestant` FOREIGN KEY (`contestant_id`) REFERENCES `contestant` (`id`),
  CONSTRAINT `fk_mentor_mentor` FOREIGN KEY (`mentor_id`) REFERENCES `person` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Võistleja juhendaja\n\nPeaks olema eraldi tabel, sest võistlejal ei pruugi juhendajat märgitud olla või võib neid olla mitu';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `person`
--

DROP TABLE IF EXISTS `person`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `person` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `publishable` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4634 DEFAULT CHARSET=utf8 COMMENT='Üks inimene - kui otsustab oma andmed kustutada, saab *siit* nullida\n\nJuhul kui siia satuvad valesti kirjutatud variandid nimedest, saab mõjutatud tabelitest person_id vms järgi ühtseks teha\n\npublishable - kas nime võib välja näidata(!)';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `person_alias`
--

DROP TABLE IF EXISTS `person_alias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `person_alias` (
  `id` int NOT NULL AUTO_INCREMENT,
  `person_id` int NOT NULL,
  `name_template` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name_template`),
  KEY `fk_person_alias_person_idx` (`person_id`),
  CONSTRAINT `fk_person_alias_person` FOREIGN KEY (`person_id`) REFERENCES `person` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `school`
--

DROP TABLE IF EXISTS `school`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `school` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=883 DEFAULT CHARSET=utf8 COMMENT='Üks kool - nt. TRK\n\nHoida tuleks siiski täisnime';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `subcontest`
--

DROP TABLE IF EXISTS `subcontest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subcontest` (
  `id` int NOT NULL AUTO_INCREMENT,
  `contest_id` int NOT NULL,
  `age_group_id` int NOT NULL,
  `name` varchar(64) NOT NULL,
  `tasks_link` varchar(128) DEFAULT NULL,
  `solutions_link` varchar(128) DEFAULT NULL,
  `description` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_contest_idx` (`contest_id`),
  KEY `fk_age_group_idx` (`age_group_id`),
  CONSTRAINT `fk_subcontest_age_group` FOREIGN KEY (`age_group_id`) REFERENCES `age_group` (`id`),
  CONSTRAINT `fk_subcontest_contest` FOREIGN KEY (`contest_id`) REFERENCES `contest` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=284 DEFAULT CHARSET=utf8 COMMENT='Üks eraldi arvestusega võistlus - nt. lahtise noorem rühm, lv 12. klass';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `subcontest_column`
--

DROP TABLE IF EXISTS `subcontest_column`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subcontest_column` (
  `id` int NOT NULL AUTO_INCREMENT,
  `subcontest_id` int NOT NULL,
  `name` varchar(64) NOT NULL,
  `seq_no` int NOT NULL,
  `extra` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_subcontest_idx` (`subcontest_id`),
  CONSTRAINT `fk_task_subcontest` FOREIGN KEY (`subcontest_id`) REFERENCES `subcontest` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2404 DEFAULT CHARSET=utf8 COMMENT='Üks näidatav tulp (ülesanne, kogupunktid, järk) iga võistleja jaoks\n\nseq_no määrab, mitmendana seda tulpa näitama peaks';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `subject`
--

DROP TABLE IF EXISTS `subject`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subject` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8 COMMENT='Õppeaine - nt. füüsika';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `type`
--

DROP TABLE IF EXISTS `type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8 COMMENT='Võistluse tüüp - lahtine, pkv, lv, üleriigiline';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `year`
--

DROP TABLE IF EXISTS `year`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `year` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=55 DEFAULT CHARSET=utf8 COMMENT='Õppeaasta - äkki on kasulik kui tahta sama õppeaasta piirkonna ning lv tulemusi kiiresti näha?';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-01-09 15:37:09
