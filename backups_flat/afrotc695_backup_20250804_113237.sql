-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: cascznjx_afrotc_recruit
-- ------------------------------------------------------
-- Server version	8.0.43

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
-- Table structure for table `activity_log`
--

DROP TABLE IF EXISTS `activity_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `activity_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `username` varchar(80) NOT NULL,
  `action` varchar(100) NOT NULL,
  `table_name` varchar(50) DEFAULT NULL,
  `record_id` int DEFAULT NULL,
  `record_description` varchar(200) DEFAULT NULL,
  `details` text,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` varchar(500) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `activity_log_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `activity_log`
--

LOCK TABLES `activity_log` WRITE;
/*!40000 ALTER TABLE `activity_log` DISABLE KEYS */;
INSERT INTO `activity_log` VALUES (1,1,'admin','LOGIN',NULL,NULL,NULL,'User admin logged in successfully','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36','2025-08-04 15:19:09'),(2,1,'admin','LOGOUT',NULL,NULL,NULL,'User admin logged out','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36','2025-08-04 07:06:49'),(3,1,'admin','LOGIN',NULL,NULL,NULL,'User admin logged in successfully','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36','2025-08-04 07:07:12'),(4,1,'admin','LOGOUT',NULL,NULL,NULL,'User admin logged out','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36','2025-08-04 05:07:11'),(5,1,'admin','LOGIN',NULL,NULL,NULL,'User admin logged in successfully','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36','2025-08-04 05:07:17'),(6,1,'admin','BACKUP','database',NULL,'Database backed up to afrotc695_backup_20250804_004033.db','Backup created at backups\\afrotc695_backup_20250804_004033.db','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36','2025-08-04 07:40:34'),(7,1,'admin','DELETE_BACKUP','database',NULL,'Deleted backup: afrotc695_backup_20250803_215524.db',NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36','2025-08-04 07:40:49'),(8,1,'admin','DELETE_BACKUP','database',NULL,'Deleted backup: afrotc695_backup_20250803_220856.db',NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36','2025-08-04 07:40:54'),(9,1,'admin','CREATE','user',2,'Created user: Recruiter Simpson',NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36','2025-08-04 08:10:34'),(10,1,'admin','EXPORT','university_contact',NULL,'Contacts Export','Exported 12 contacts to PDF','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36','2025-08-04 08:11:49'),(11,1,'admin','EXPORT','cadet',NULL,'Cadet Export','Exported 19 cadet members to EXCEL','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36','2025-08-04 08:14:42'),(12,1,'admin','EXPORT','cadet',NULL,'Cadet Export','Exported 19 cadet members to PDF','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36','2025-08-04 08:18:45'),(13,1,'admin','CREATE','potential_recruit',1,'Recruit: John Smith','Added new recruit from Sammamish High School','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36','2025-08-04 15:31:38'),(14,1,'admin','CREATE','potential_recruit',2,'Recruit: John Smith','Added new recruit from Sammamish High School','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36','2025-08-04 15:34:38'),(15,1,'admin','CREATE','recruitment_document',1,'Document: AFROTC Application for Scholarship',NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36','2025-08-04 15:36:34'),(16,1,'admin','DELETE','recruitment_document',1,'Document: AFROTC Application for Scholarship',NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36','2025-08-04 15:39:34'),(17,1,'admin','CREATE','recruitment_document',2,'Document: AFROTC Scholarship Application for High School Students',NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36','2025-08-04 15:45:12'),(18,1,'admin','DELETE','recruitment_document',2,'Document: AFROTC Scholarship Application for High School Students',NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36','2025-08-04 15:45:23'),(19,1,'admin','CREATE','recruitment_document',3,'Document: Scholarship Application for AFROTC',NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36','2025-08-04 15:45:46'),(20,1,'admin','BACKUP','database',NULL,'Database backed up to afrotc695_backup_20250804_091235.sql','Backup created at backups\\afrotc695_backup_20250804_091235.sql','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36','2025-08-04 16:12:36'),(21,1,'admin','CREATE','recruitment_event',1,'Event: Sammamish School Visit on 2025-09-04','Added new recruitment event of type: campus_visit','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36','2025-08-04 18:06:28'),(22,1,'admin','UPDATE','potential_recruit',1,'Recruit: Sara Smith','Updated recruit. Changes: School: Sammamish High School → Eastlake High School','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36','2025-08-04 18:21:34'),(23,1,'admin','UPDATE','potential_recruit',1,'Recruit: Sara Smith','Updated recruit. Changes: General update','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36','2025-08-04 18:21:46');
/*!40000 ALTER TABLE `activity_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cadet`
--

DROP TABLE IF EXISTS `cadet`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cadet` (
  `id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `email` varchar(120) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `major` varchar(100) NOT NULL,
  `graduation_year` int NOT NULL,
  `cadet_rank` varchar(50) NOT NULL,
  `hometown` varchar(100) DEFAULT NULL,
  `officer_interest` varchar(100) DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `unenrollment_reason` text,
  `unenrollment_date` date DEFAULT NULL,
  `gpa` float DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cadet`
--

LOCK TABLES `cadet` WRITE;
/*!40000 ALTER TABLE `cadet` DISABLE KEYS */;
INSERT INTO `cadet` VALUES (1,'Aviv','Brill','brill28@up.edu','5108153687','Biochemistry',2028,'C/3C','Sammamish, WA','Non-Rated','active','',NULL,3.8,'2025-08-04 04:43:33','2025-08-04 04:43:33'),(2,'John','Smith','john.smith@up.edu','555-0101','Computer Science',2026,'C/2d Lt','Portland, OR','Rated','graduated',NULL,NULL,3.8,'2025-08-04 07:50:19','2025-08-04 07:50:19'),(3,'Sarah','Johnson','sarah.johnson@up.edu','555-0102','Engineering',2026,'C/2d Lt','Seattle, WA','Non-Rated','graduated',NULL,NULL,3.9,'2025-08-04 07:50:19','2025-08-04 07:50:19'),(4,'Mike','Davis','mike.davis@up.edu','555-0103','Physics',2026,'C/2d Lt','Eugene, OR','Rated','graduated',NULL,NULL,3.7,'2025-08-04 07:50:19','2025-08-04 07:50:19'),(5,'Emily','Wilson','emily.wilson@up.edu','555-0201','Biology',2027,'C/1st Lt','Spokane, WA','Rated','active',NULL,NULL,3.6,'2025-08-04 07:50:19','2025-08-04 07:50:19'),(6,'David','Brown','david.brown@up.edu','555-0202','Chemistry',2027,'C/1st Lt','Tacoma, WA','Non-Rated','active',NULL,NULL,3.5,'2025-08-04 07:50:19','2025-08-04 07:50:19'),(7,'Lisa','Garcia','lisa.garcia@up.edu','555-0203','Mathematics',2027,'C/1st Lt','Vancouver, WA','Rated','inactive',NULL,NULL,3.2,'2025-08-04 07:50:19','2025-08-04 07:50:19'),(8,'Tom','Miller','tom.miller@up.edu','555-0204','Psychology',2027,'C/1st Lt','Salem, OR','Non-Rated','inactive',NULL,NULL,2.8,'2025-08-04 07:50:19','2025-08-04 07:50:19'),(9,'Jessica','Taylor','jessica.taylor@up.edu','555-0301','Business',2028,'C/Capt','Bend, OR','Rated','active',NULL,NULL,3.7,'2025-08-04 07:50:19','2025-08-04 07:50:19'),(10,'Ryan','Anderson','ryan.anderson@up.edu','555-0302','Economics',2028,'C/Capt','Medford, OR','Non-Rated','active',NULL,NULL,3.4,'2025-08-04 07:50:19','2025-08-04 07:50:19'),(11,'Amanda','Thomas','amanda.thomas@up.edu','555-0303','Political Science',2028,'C/Capt','Corvallis, OR','Rated','active',NULL,NULL,3.8,'2025-08-04 07:50:19','2025-08-04 07:50:19'),(12,'Chris','Jackson','chris.jackson@up.edu','555-0304','History',2028,'C/Capt','Olympia, WA','Non-Rated','inactive',NULL,NULL,2.9,'2025-08-04 07:50:19','2025-08-04 07:50:19'),(13,'Rachel','White','rachel.white@up.edu','555-0305','English',2028,'C/Capt','Everett, WA','Rated','inactive',NULL,NULL,3.1,'2025-08-04 07:50:19','2025-08-04 07:50:19'),(14,'Kevin','Harris','kevin.harris@up.edu','555-0401','Computer Engineering',2029,'C/3C','Bellevue, WA','Rated','active',NULL,NULL,3.9,'2025-08-04 07:50:19','2025-08-04 07:50:19'),(15,'Nicole','Clark','nicole.clark@up.edu','555-0402','Mechanical Engineering',2029,'C/3C','Kirkland, WA','Non-Rated','active',NULL,NULL,3.6,'2025-08-04 07:50:19','2025-08-04 07:50:19'),(16,'Alex','Lewis','alex.lewis@up.edu','555-0403','Electrical Engineering',2029,'C/3C','Redmond, WA','Rated','active',NULL,NULL,3.7,'2025-08-04 07:50:19','2025-08-04 07:50:19'),(17,'Megan','Robinson','megan.robinson@up.edu','555-0404','Civil Engineering',2029,'C/3C','Issaquah, WA','Non-Rated','active',NULL,NULL,3.5,'2025-08-04 07:50:19','2025-08-04 07:50:19'),(18,'Daniel','Walker','daniel.walker@up.edu','555-0405','Aerospace Engineering',2029,'C/3C','Sammamish, WA','Rated','active',NULL,NULL,3.8,'2025-08-04 07:50:19','2025-08-04 07:50:19'),(19,'Sophie','Hall','sophie.hall@up.edu','555-0406','Chemical Engineering',2029,'C/3C','Woodinville, WA','Non-Rated','inactive',NULL,NULL,2.7,'2025-08-04 07:50:19','2025-08-04 07:50:19');
/*!40000 ALTER TABLE `cadet` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `external_link`
--

DROP TABLE IF EXISTS `external_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `external_link` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `url` varchar(500) NOT NULL,
  `description` text,
  `category` varchar(50) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `sort_order` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `external_link`
--

LOCK TABLES `external_link` WRITE;
/*!40000 ALTER TABLE `external_link` DISABLE KEYS */;
INSERT INTO `external_link` VALUES (1,'AFROTC Official Website','https://www.afrotc.com/','Official Air Force ROTC website with information about the program, scholarships, and careers.','official',1,1,'2025-08-04 08:12:49','2025-08-04 08:12:49'),(2,'University of Portland AFROTC','https://www.up.edu/afrotc/','AFROTC Detachment 695 at University of Portland - local program information and contact details.','official',1,2,'2025-08-04 08:12:49','2025-08-04 08:12:49'),(3,'U.S. Air Force','https://www.af.mil/','Official U.S. Air Force website with information about careers, missions, and news.','official',1,3,'2025-08-04 08:12:49','2025-08-04 08:12:49'),(4,'U.S. Space Force','https://www.spaceforce.mil/','Official U.S. Space Force website with information about space operations and careers.','official',1,4,'2025-08-04 08:12:49','2025-08-04 08:12:49'),(5,'The Holm Center','https://www.airuniversity.af.edu/Holm-Center/','Air University Holm Center for Officer Accessions and Citizen Development.','official',1,5,'2025-08-04 08:12:49','2025-08-04 08:12:49');
/*!40000 ALTER TABLE `external_link` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `password_history`
--

DROP TABLE IF EXISTS `password_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `password_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `password_hash` varchar(120) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `password_history_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `password_history`
--

LOCK TABLES `password_history` WRITE;
/*!40000 ALTER TABLE `password_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `password_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `potential_recruit`
--

DROP TABLE IF EXISTS `potential_recruit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `potential_recruit` (
  `id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `email` varchar(120) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `major` varchar(100) DEFAULT NULL,
  `current_school` varchar(100) NOT NULL,
  `school_type` varchar(20) NOT NULL,
  `high_school_graduation_year` int DEFAULT NULL,
  `expected_college_graduation_year` int DEFAULT NULL,
  `gpa` float DEFAULT NULL,
  `sat_score` int DEFAULT NULL,
  `act_score` int DEFAULT NULL,
  `interests` text,
  `notes` text,
  `status` varchar(20) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `potential_recruit`
--

LOCK TABLES `potential_recruit` WRITE;
/*!40000 ALTER TABLE `potential_recruit` DISABLE KEYS */;
INSERT INTO `potential_recruit` VALUES (1,'Sara','Smith','sara@email.com','','Engineering','Eastlake High School','high_school',2027,2029,3.5,1200,NULL,'','','prospective','2025-08-04 15:31:38','2025-08-04 18:21:46'),(2,'John','Smith','john@email.com','','Engineering','Sammamish High School','high_school',2027,2029,3.5,1200,NULL,'','','prospective','2025-08-04 15:34:38','2025-08-04 15:34:38');
/*!40000 ALTER TABLE `potential_recruit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recruitment_document`
--

DROP TABLE IF EXISTS `recruitment_document`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recruitment_document` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `description` text,
  `filename` varchar(255) NOT NULL,
  `original_filename` varchar(255) NOT NULL,
  `file_size` int DEFAULT NULL,
  `file_type` varchar(50) DEFAULT NULL,
  `category` varchar(50) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `sort_order` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recruitment_document`
--

LOCK TABLES `recruitment_document` WRITE;
/*!40000 ALTER TABLE `recruitment_document` DISABLE KEYS */;
INSERT INTO `recruitment_document` VALUES (3,'Scholarship Application for AFROTC','','d0e97453f5db476b92807b2345d3ec44_1.-AY26-27_HSSP_Applicant_Guide-Signed.pdf','1.-AY26-27_HSSP_Applicant_Guide-Signed.pdf',606987,'pdf','forms',1,0,'2025-08-04 15:45:46','2025-08-04 15:45:46');
/*!40000 ALTER TABLE `recruitment_document` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recruitment_event`
--

DROP TABLE IF EXISTS `recruitment_event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recruitment_event` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `description` text,
  `event_date` date NOT NULL,
  `start_time` time DEFAULT NULL,
  `end_time` time DEFAULT NULL,
  `location` varchar(200) DEFAULT NULL,
  `university_id` int DEFAULT NULL,
  `event_type` varchar(50) NOT NULL,
  `status` varchar(20) DEFAULT NULL,
  `attendees_count` int DEFAULT NULL,
  `notes` text,
  `created_at` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `university_id` (`university_id`),
  CONSTRAINT `recruitment_event_ibfk_1` FOREIGN KEY (`university_id`) REFERENCES `university_contact` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recruitment_event`
--

LOCK TABLES `recruitment_event` WRITE;
/*!40000 ALTER TABLE `recruitment_event` DISABLE KEYS */;
INSERT INTO `recruitment_event` VALUES (1,'Sammamish School Visit','','2025-09-04','15:22:00','17:08:00','',NULL,'campus_visit','scheduled',0,'','2025-08-04 18:06:28','2025-08-04 18:06:28');
/*!40000 ALTER TABLE `recruitment_event` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `university_contact`
--

DROP TABLE IF EXISTS `university_contact`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `university_contact` (
  `id` int NOT NULL AUTO_INCREMENT,
  `university_name` varchar(100) NOT NULL,
  `contact_name` varchar(100) NOT NULL,
  `contact_title` varchar(100) DEFAULT NULL,
  `email` varchar(120) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `address` text,
  `notes` text,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `university_contact`
--

LOCK TABLES `university_contact` WRITE;
/*!40000 ALTER TABLE `university_contact` DISABLE KEYS */;
INSERT INTO `university_contact` VALUES (1,'Bishop Blanchet High School','Admissions Office',NULL,'admissions@bishopblanchet.org','(206) 527-3990','8200 Wallingford Ave N, Seattle, WA 98103','Catholic high school in Seattle - Imported from Jesuit and Catholic High Schools document',1,'2025-08-04 04:41:28','2025-08-04 04:41:28'),(2,'Eastside Catholic School','Admissions Office',NULL,'admissions@eastsidecatholic.org','(425) 295-3000','232 228th Ave SE, Sammamish, WA 98074','Catholic high school in Sammamish - Imported from Jesuit and Catholic High Schools document',1,'2025-08-04 04:41:28','2025-08-04 04:41:28'),(3,'Holy Names Academy','Admissions Office',NULL,'admissions@holynames-sea.org','(206) 323-4272','728 21st Ave E, Seattle, WA 98112','Catholic girls\' high school in Seattle - Imported from Jesuit and Catholic High Schools document',1,'2025-08-04 04:41:28','2025-08-04 04:41:28'),(4,'Kennedy Catholic High School','Admissions Office',NULL,'admissions@kennedyhs.org','(206) 246-0500','140 S 140th St, Burien, WA 98168','Catholic high school in Burien - Imported from Jesuit and Catholic High Schools document',1,'2025-08-04 04:41:28','2025-08-04 04:41:28'),(5,'O\'Dea High School','Admissions Office',NULL,'admissions@odea.org','(206) 622-7151','802 Terry Ave, Seattle, WA 98104','Catholic boys\' high school in Seattle - Imported from Jesuit and Catholic High Schools document',1,'2025-08-04 04:41:28','2025-08-04 04:41:28'),(6,'Seattle Preparatory School','Admissions Office',NULL,'admissions@seaprep.org','(206) 324-0400','2400 11th Ave E, Seattle, WA 98102','Jesuit high school in Seattle - Imported from Jesuit and Catholic High Schools document',1,'2025-08-04 04:41:28','2025-08-04 04:41:28'),(7,'Blanchet Catholic School','Admissions Office',NULL,'admissions@blanchetcatholicschool.com','(503) 391-2639','4373 Market St NE, Salem, OR 97301','Catholic high school in Salem, OR - Imported from Jesuit and Catholic High Schools document',1,'2025-08-04 04:41:28','2025-08-04 04:41:28'),(8,'Central Catholic High School','Admissions Office',NULL,'admissions@centralcatholichigh.org','(503) 235-3138','2401 SE Stark St, Portland, OR 97214','Catholic high school in Portland - Imported from Jesuit and Catholic High Schools document',1,'2025-08-04 04:41:28','2025-08-04 04:41:28'),(9,'Jesuit High School','Admissions Office',NULL,'admissions@jesuitportland.org','(503) 291-5423','9000 SW Beaverton-Hillsdale Hwy, Portland, OR 97225','Jesuit high school in Portland - Imported from Jesuit and Catholic High Schools document',1,'2025-08-04 04:41:28','2025-08-04 04:41:28'),(10,'La Salle Catholic College Preparatory','Admissions Office',NULL,'admissions@lsprep.org','(503) 659-4155','11999 SE Fuller Rd, Milwaukie, OR 97222','Catholic high school in Milwaukie - Imported from Jesuit and Catholic High Schools document',1,'2025-08-04 04:41:28','2025-08-04 04:41:28'),(11,'St. Mary\'s Academy','Admissions Office',NULL,'admissions@stmaryspdx.org','(503) 228-8306','1615 SW 5th Ave, Portland, OR 97201','Catholic girls\' high school in Portland - Imported from Jesuit and Catholic High Schools document',1,'2025-08-04 04:41:28','2025-08-04 04:41:28'),(12,'Valley Catholic School','Admissions Office',NULL,'admissions@valleycatholic.org','(503) 649-5511','4275 SW 148th Ave, Beaverton, OR 97007','Catholic high school in Beaverton - Imported from Jesuit and Catholic High Schools document',1,'2025-08-04 04:41:28','2025-08-04 04:41:28');
/*!40000 ALTER TABLE `university_contact` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(80) NOT NULL,
  `email` varchar(120) NOT NULL,
  `password_hash` varchar(120) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `role` varchar(20) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `is_locked` tinyint(1) DEFAULT NULL,
  `password_changed_at` datetime DEFAULT NULL,
  `password_expires_at` datetime DEFAULT NULL,
  `force_password_change` tinyint(1) DEFAULT NULL,
  `secret_question` varchar(200) NOT NULL,
  `secret_answer_hash` varchar(120) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'admin','admin@afrotc695.com','pbkdf2:sha256:600000$WBJP9XcOZ3BNm5fp$6c747b6192498ba5365a7cf8f2502a42b8e4d9bbc745b9d60dc3c833dd8b1f4a','Admin','User',NULL,'admin',1,0,'2025-08-04 15:17:54',NULL,0,'What is your favorite color?','pbkdf2:sha256:600000$0OWZ1VGstIPLg3C0$98cfe3c4695c52590ee4ca7e1ecdef94e18e2df5c7168c3befcccbad22c9cc16','2025-08-04 15:17:54','2025-08-04 15:17:54');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'cascznjx_afrotc_recruit'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-04 11:32:37
