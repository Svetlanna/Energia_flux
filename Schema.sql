CREATE DATABASE IF NOT EXISTS `energia_flux`
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

USE `energia_flux`;

-- ---------------------------------------------------------------
-- consommation : historique RTE (cible du modele + colonnes non
-- utilisees comme features, gardees pour l'historique)
-- ---------------------------------------------------------------
CREATE TABLE `consommation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `date_heure` datetime NOT NULL,
  `consommation` float DEFAULT NULL,
  `nucleaire` float DEFAULT NULL,
  `eolien` float DEFAULT NULL,
  `solaire` float DEFAULT NULL,
  `hydraulique` float DEFAULT NULL,
  `taux_co2` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `date_heure` (`date_heure`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ---------------------------------------------------------------
-- meteo : historique Open-Meteo (features temperature/humidite)
-- ---------------------------------------------------------------
CREATE TABLE `meteo` (
  `id` int NOT NULL AUTO_INCREMENT,
  `date_heure` datetime NOT NULL,
  `temperature` float DEFAULT NULL,
  `humidite` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `date_heure` (`date_heure`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ---------------------------------------------------------------
-- modele : tracabilite des versions de modele entraine
-- ---------------------------------------------------------------
CREATE TABLE `modele` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nom_fichier` varchar(255) NOT NULL,
  `date_entrainement` datetime NOT NULL,
  `mae` float DEFAULT NULL,
  `features_json` json DEFAULT NULL,
  `actif` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `nom_fichier` (`nom_fichier`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ---------------------------------------------------------------
-- prediction : log de chaque prediction servie par l'API
-- ---------------------------------------------------------------
CREATE TABLE `prediction` (
  `id` int NOT NULL AUTO_INCREMENT,
  `date_prediction` datetime NOT NULL,
  `heure` int DEFAULT NULL,
  `jour_semaine` int DEFAULT NULL,
  `mois` int DEFAULT NULL,
  `valeur_predite_mw` float NOT NULL,
  `modele_utilise` int NOT NULL,
  `consommation_reelle_observee` float DEFAULT NULL,
  `erreur_absolue` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `modele_utilise` (`modele_utilise`),
  CONSTRAINT `prediction_ibfk_1` FOREIGN KEY (`modele_utilise`) REFERENCES `modele` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ---------------------------------------------------------------
-- region : profil statique par region (fichier du prof)
-- ---------------------------------------------------------------
CREATE TABLE `region` (
  `id` varchar(64) NOT NULL,
  `insee_code` varchar(10) DEFAULT NULL,
  `nom` varchar(100) NOT NULL,
  `population_2023` int DEFAULT NULL,
  `consommation_moyenne_mw_2024` float DEFAULT NULL,
  `pic_illustratif_mw` float DEFAULT NULL,
  `connectee_reseau_continental` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ---------------------------------------------------------------
-- evenement_exceptionnel : anomalies detectees + explication IA
-- ---------------------------------------------------------------
CREATE TABLE `evenement_exceptionnel` (
  `id` int NOT NULL AUTO_INCREMENT,
  `date_jour` date NOT NULL,
  `consommation_moyenne_mw` float DEFAULT NULL,
  `moyenne_mobile_7j_mw` float DEFAULT NULL,
  `ecart_pourcent` float DEFAULT NULL,
  `commentaire_ia` text,
  `cree_le` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;