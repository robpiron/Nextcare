-- ============================================================================
-- NEXTCARE HEALTHCARE OPERATING SYSTEM (HOS) - DATABASE SCHEMA
-- MySQL 8.0+ | Engine: InnoDB | Charset: UTF8MB4
-- ============================================================================

CREATE DATABASE IF NOT EXISTS nextcare_db;
USE nextcare_db;

-- ----------------------------------------------------------------------------
-- 1. CORE & INTEROPERABILITY MODULE
-- ----------------------------------------------------------------------------

-- Table: patients (Anagrafica unica paziente)
CREATE TABLE IF NOT EXISTS `patients` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `uuid` VARCHAR(36) NOT NULL UNIQUE,
    `tax_code` VARCHAR(16) NOT NULL UNIQUE, -- Codice Fiscale
    `first_name` VARCHAR(100) NOT NULL,
    `last_name` VARCHAR(100) NOT NULL,
    `birth_date` DATE NOT NULL,
    `gender` ENUM('M', 'F', 'OTHER') NOT NULL,
    `email` VARCHAR(150),
    `phone` VARCHAR(30),
    `address` VARCHAR(255),
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `deleted_at` TIMESTAMP NULL DEFAULT NULL,
    INDEX `idx_patient_search` (`last_name`, `first_name`),
    INDEX `idx_patient_tax_code` (`tax_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: patient_consents (Consensi e conformità GDPR)
CREATE TABLE IF NOT EXISTS `patient_consents` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `patient_id` INT NOT NULL,
    `marketing_consent` TINYINT(1) NOT NULL DEFAULT 0,
    `profiling_consent` TINYINT(1) NOT NULL DEFAULT 0,
    `treatment_consent` TINYINT(1) NOT NULL DEFAULT 1,
    `signed_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`patient_id`) REFERENCES `patients`(`id`) ON DELETE CASCADE,
    UNIQUE INDEX `uq_patient_consent` (`patient_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: staff (Personale sanitario ed amministrativo)
CREATE TABLE IF NOT EXISTS `staff` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `first_name` VARCHAR(100) NOT NULL,
    `last_name` VARCHAR(100) NOT NULL,
    `role` ENUM('doctor', 'nurse', 'technician', 'administrative', 'manager', 'biologo', 'therapist') NOT NULL,
    `email` VARCHAR(150) NOT NULL UNIQUE,
    `phone` VARCHAR(30),
    `active` TINYINT(1) NOT NULL DEFAULT 1,
    `username` VARCHAR(100) UNIQUE NULL,
    `password` VARCHAR(255) NULL,
    `profiles` JSON NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `deleted_at` TIMESTAMP NULL DEFAULT NULL,
    INDEX `idx_staff_role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: audit_logs (Log eventi clinici e amministrativi)
CREATE TABLE IF NOT EXISTS `audit_logs` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `staff_id` INT NULL,
    `action` VARCHAR(100) NOT NULL,
    `table_name` VARCHAR(100) NOT NULL,
    `record_id` INT NULL,
    `details` JSON NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`staff_id`) REFERENCES `staff`(`id`) ON DELETE SET NULL,
    INDEX `idx_audit_action` (`action`),
    INDEX `idx_audit_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ----------------------------------------------------------------------------
-- CLINICS & EQUIPMENT
-- ----------------------------------------------------------------------------

-- Table: clinics (Ambulatori e strutture fisiche)
CREATE TABLE IF NOT EXISTS `clinics` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `location` VARCHAR(150) NOT NULL,
    `capacity` INT DEFAULT 1,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: equipment (Macchinari e strumentazioni cliniche)
CREATE TABLE IF NOT EXISTS `equipment` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `clinic_id` INT NULL,
    `name` VARCHAR(150) NOT NULL,
    `type` VARCHAR(100) NOT NULL,
    `serial_number` VARCHAR(100) NOT NULL UNIQUE,
    `status` ENUM('active', 'maintenance', 'broken', 'retired') NOT NULL DEFAULT 'active',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`clinic_id`) REFERENCES `clinics`(`id`) ON DELETE SET NULL,
    INDEX `idx_equipment_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ----------------------------------------------------------------------------
-- MEDICAL SERVICES MODULE (Centralizza visite ed esami)
-- ----------------------------------------------------------------------------

-- Table: dose_classes (Classi di dose per diagnostica per immagini - D.Lgs. 101/2020)
CREATE TABLE IF NOT EXISTS `dose_classes` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `code` VARCHAR(50) NOT NULL UNIQUE,
    `range_msv` VARCHAR(100) NOT NULL,
    `description` VARCHAR(255) NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: medical_services (Configurazione prestazioni)
CREATE TABLE IF NOT EXISTS `medical_services` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(1000) NOT NULL,
    `type` ENUM('visita', 'lis', 'ris', 'pacchetto') NOT NULL,
    `code` VARCHAR(50) NULL, -- Codice CUR 2024 / ID esame
    `branch` VARCHAR(100) NULL, -- Branca medica (visita, ris)
    `price` DECIMAL(10, 2) NULL, -- Tariffa nomenclatore
    `clinic_id` INT NULL, -- Collegamento ad ambulatorio (visita, ris)
    `equipment_id` INT NULL, -- Collegamento a strumento (ris)
    `sample_type` VARCHAR(100) NULL, -- Tipo provetta (lis)
    `sample_collection_type_id` INT NULL, -- Tipo prelievo (lis)
    `reference_range` VARCHAR(100) NULL, -- Limiti di riferimento (lis)
    `unit` VARCHAR(50) NULL, -- Unità di misura (lis)
    `parameters` JSON NULL, -- Parametri dettagliati (lis)
    `package_items` JSON NULL, -- Prestazioni incluse nel pacchetto
    `alert_note` TEXT NULL, -- Note di allerta/avviso prestazione
    `profit_center` VARCHAR(100) NULL, -- Centro di profitto/ricavo
    `dose_class_id` INT NULL, -- Collegamento a classe di dose (ris)
    `is_microbiology` TINYINT NOT NULL DEFAULT 0, -- Flag microbiologia (lis)
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`clinic_id`) REFERENCES `clinics`(`id`) ON DELETE SET NULL,
    FOREIGN KEY (`equipment_id`) REFERENCES `equipment`(`id`) ON DELETE SET NULL,
    FOREIGN KEY (`sample_collection_type_id`) REFERENCES `sample_collection_types`(`id`) ON DELETE SET NULL,
    FOREIGN KEY (`dose_class_id`) REFERENCES `dose_classes`(`id`) ON DELETE SET NULL,
    INDEX `idx_service_type` (`type`),
    INDEX `idx_service_code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ----------------------------------------------------------------------------
-- 2. CUP (CENTRO UNICO PRENOTAZIONI) MODULE
-- ----------------------------------------------------------------------------

-- Table: doctors (Medici specialisti)
CREATE TABLE IF NOT EXISTS `doctors` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `staff_id` INT NOT NULL,
    `specialization` VARCHAR(150) NOT NULL,
    `visit_duration_minutes` INT DEFAULT 30,
    `active` TINYINT(1) NOT NULL DEFAULT 1,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`staff_id`) REFERENCES `staff`(`id`) ON DELETE CASCADE,
    INDEX `idx_doctor_specialization` (`specialization`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: doctor_agendas (Agende Medici)
CREATE TABLE IF NOT EXISTS `doctor_agendas` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `doctor_id` INT NOT NULL,
    `start_date` DATE NOT NULL,
    `end_date` DATE NOT NULL,
    `active_days` VARCHAR(100) NOT NULL, -- e.g. "Monday,Wednesday"
    `slot_duration_minutes` INT NOT NULL DEFAULT 30,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`doctor_id`) REFERENCES `doctors`(`id`) ON DELETE CASCADE,
    INDEX `idx_agenda_dates` (`start_date`, `end_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: doctor_agenda_services (Servizi gestiti in Agenda)
CREATE TABLE IF NOT EXISTS `doctor_agenda_services` (
    `agenda_id` INT NOT NULL,
    `service_id` INT NOT NULL,
    PRIMARY KEY (`agenda_id`, `service_id`),
    FOREIGN KEY (`agenda_id`) REFERENCES `doctor_agendas`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`service_id`) REFERENCES `medical_services`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: doctor_closures (Chiusure eccezionali e fisse)
CREATE TABLE IF NOT EXISTS `doctor_closures` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `doctor_id` INT NULL, -- NULL per chiusura intero centro
    `start_date` DATE NOT NULL,
    `end_date` DATE NOT NULL,
    `start_time` VARCHAR(8) NULL, -- NULL per tutto il giorno
    `end_time` VARCHAR(8) NULL,   -- NULL per tutto il giorno
    `description` VARCHAR(255) NOT NULL,
    `closure_type` VARCHAR(50) NOT NULL, -- 'exceptional' o 'fixed'
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`doctor_id`) REFERENCES `doctors`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: appointments (Prenotazioni visite ed esami)
CREATE TABLE IF NOT EXISTS `appointments` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `patient_id` INT NOT NULL,
    `doctor_id` INT NULL, -- NULL per esami LIS o senza medico specifico
    `appointment_datetime` DATETIME NOT NULL,
    `status` ENUM('scheduled', 'completed', 'cancelled', 'no_show', 'in_progress') NOT NULL DEFAULT 'scheduled',
    `notes` TEXT,
    `requesting_doctor` VARCHAR(255) NULL, -- Medico richiedente esterno
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`patient_id`) REFERENCES `patients`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`doctor_id`) REFERENCES `doctors`(`id`) ON DELETE SET NULL,
    INDEX `idx_appointment_date` (`appointment_datetime`),
    INDEX `idx_appointment_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: appointment_services (Associazione Molti-a-Molti CUP Prenotazioni)
CREATE TABLE IF NOT EXISTS `appointment_services` (
    `appointment_id` INT NOT NULL,
    `service_id` INT NOT NULL,
    PRIMARY KEY (`appointment_id`, `service_id`),
    FOREIGN KEY (`appointment_id`) REFERENCES `appointments`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`service_id`) REFERENCES `medical_services`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;



-- ----------------------------------------------------------------------------
-- 3. LIS (LABORATORY INFORMATION SYSTEM) MODULE
-- ----------------------------------------------------------------------------

-- Table: lab_samples (Campioni di laboratorio)
CREATE TABLE IF NOT EXISTS `lab_samples` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `patient_id` INT NOT NULL,
    `barcode` VARCHAR(50) NOT NULL UNIQUE,
    `sample_type` VARCHAR(100) NOT NULL,
    `status` ENUM('da prelevare', 'collected', 'received', 'processing', 'to_validate', 'validated', 'completed', 'rejected', 'suspended') NOT NULL DEFAULT 'da prelevare',
    `session_uid` VARCHAR(50) NULL,
    `collected_at` TIMESTAMP NULL DEFAULT NULL,
    `collected_by` INT NULL,
    `report_notes` TEXT NULL, -- Note referto/accettazione campione
    `requesting_doctor` VARCHAR(255) NULL, -- Medico richiedente esterno
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`patient_id`) REFERENCES `patients`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`collected_by`) REFERENCES `staff`(`id`) ON DELETE SET NULL,
    INDEX `idx_sample_status` (`status`),
    INDEX `idx_sample_barcode` (`barcode`),
    INDEX `idx_sample_session` (`session_uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: lab_tests (Esami e analisi cliniche)
CREATE TABLE IF NOT EXISTS `lab_tests` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `sample_id` INT NOT NULL,
    `service_id` INT NOT NULL, -- Collegamento alla prestazione LIS
    `test_name` VARCHAR(150) NOT NULL,
    `result_value` VARCHAR(100) NULL,
    `reference_range` VARCHAR(100) NULL,
    `unit` VARCHAR(50) NULL,
    `status` ENUM('pending', 'completed', 'flagged', 'suspended') NOT NULL DEFAULT 'pending',
    `verified_by` INT NULL,
    `verified_at` TIMESTAMP NULL DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`sample_id`) REFERENCES `lab_samples`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`service_id`) REFERENCES `medical_services`(`id`) ON DELETE RESTRICT,
    FOREIGN KEY (`verified_by`) REFERENCES `staff`(`id`) ON DELETE SET NULL,
    INDEX `idx_test_name` (`test_name`),
    INDEX `idx_test_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ----------------------------------------------------------------------------
-- 4. RIS (RADIOLOGY INFORMATION SYSTEM) MODULE
-- ----------------------------------------------------------------------------

-- Table: radiology_studies (Esami radiologici e referti DICOM)
CREATE TABLE IF NOT EXISTS `radiology_studies` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `patient_id` INT NOT NULL,
    `doctor_id` INT NULL, -- Medico richiedente (se interno)
    `service_id` INT NOT NULL, -- Collegamento alla prestazione RIS
    `study_type` ENUM('XRAY', 'MRI', 'CT', 'ULTRASOUND', 'MAMMOGRAPHY', 'VISIT') NOT NULL,
    `scheduled_at` DATETIME NOT NULL,
    `status` ENUM('scheduled', 'in_progress', 'executed', 'completed', 'cancelled') NOT NULL DEFAULT 'scheduled',
    `dicom_series_uid` VARCHAR(128) NULL,
    `report_text` TEXT NULL,
    `signed_by` INT NULL, -- Radiologo refertatore
    `signed_at` TIMESTAMP NULL DEFAULT NULL,
    `tsrm_id` INT NULL,
    `requesting_doctor` VARCHAR(255) NULL, -- Medico richiedente esterno
    `clinical_query` TEXT NULL,
    `attachment_name` VARCHAR(255) NULL,
    `attachment_data` LONGTEXT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`patient_id`) REFERENCES `patients`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`doctor_id`) REFERENCES `doctors`(`id`) ON DELETE RESTRICT,
    FOREIGN KEY (`service_id`) REFERENCES `medical_services`(`id`) ON DELETE RESTRICT,
    FOREIGN KEY (`signed_by`) REFERENCES `staff`(`id`) ON DELETE SET NULL,
    INDEX `idx_study_type` (`study_type`),
    INDEX `idx_study_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ----------------------------------------------------------------------------
-- 6. ADMISSION & BILLING MODULE
-- ----------------------------------------------------------------------------

-- Table: admissions (Accettazione e Ricoveri)
CREATE TABLE IF NOT EXISTS `admissions` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `patient_id` INT NOT NULL,
    `admission_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `discharge_date` DATETIME NULL DEFAULT NULL,
    `department` VARCHAR(100) NOT NULL,
    `reason` TEXT NOT NULL,
    `status` ENUM('active', 'discharged', 'transferred') NOT NULL DEFAULT 'active',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`patient_id`) REFERENCES `patients`(`id`) ON DELETE CASCADE,
    INDEX `idx_admission_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: price_lists (Listini prezzi)
CREATE TABLE IF NOT EXISTS `price_lists` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: price_list_items (Voci di listino)
CREATE TABLE IF NOT EXISTS `price_list_items` (
    `price_list_id` INT NOT NULL,
    `service_id` INT NOT NULL,
    `price` DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (`price_list_id`, `service_id`),
    FOREIGN KEY (`price_list_id`) REFERENCES `price_lists`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`service_id`) REFERENCES `medical_services`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: insurances (Assicurazioni e convenzioni)
CREATE TABLE IF NOT EXISTS `insurances` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL,
    `price_list_id` INT NULL,
    `billing_mode` VARCHAR(50) NOT NULL,
    FOREIGN KEY (`price_list_id`) REFERENCES `price_lists`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: patient_claims (Pratiche/Coperture assicurative)
CREATE TABLE IF NOT EXISTS `patient_claims` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `patient_id` INT NOT NULL,
    `insurance_id` INT NOT NULL,
    `policy_number` VARCHAR(100) NOT NULL,
    `deductible_value` DECIMAL(10, 2) NOT NULL,
    `deductible_type` VARCHAR(50) NOT NULL,
    `status` VARCHAR(50) NOT NULL DEFAULT 'open',
    FOREIGN KEY (`patient_id`) REFERENCES `patients`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`insurance_id`) REFERENCES `insurances`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: tube_types (Tipi provetta biologica LIS)
CREATE TABLE IF NOT EXISTS `tube_types` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL,
    `suffix` VARCHAR(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: sample_collection_types (Tipi di prelievo biologico LIS)
CREATE TABLE IF NOT EXISTS `sample_collection_types` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: profit_centers (Centri di profitto/ricavo aziendali)
CREATE TABLE IF NOT EXISTS `profit_centers` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL UNIQUE,
    `description` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: sent_emails (Log email inviate)
CREATE TABLE IF NOT EXISTS `sent_emails` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `patient_id` INT NULL,
    `recipient` VARCHAR(255) NOT NULL,
    `event` VARCHAR(100) NOT NULL,
    `subject` VARCHAR(255) NOT NULL,
    `sent_at` DATETIME NOT NULL,
    `status` VARCHAR(50) NOT NULL,
    FOREIGN KEY (`patient_id`) REFERENCES `patients`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: invoices (Fatturazione e convenzioni)
CREATE TABLE IF NOT EXISTS `invoices` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `admission_id` INT NULL, -- NULL per prestazioni esterne (CUP, LIS, RIS)
    `appointment_id` INT NULL, -- Collegamento alla prenotazione CUP
    `sample_id` INT NULL, -- Collegamento al prelievo LIS
    `study_id` INT NULL, -- Collegamento all'esame RIS
    `price_list_id` INT NULL, -- Listino associato alla fattura
    `claim_id` INT NULL, -- Convenzione/pratica associata
    `invoice_number` VARCHAR(50) NOT NULL UNIQUE,
    `issue_date` DATE NOT NULL,
    `subtotal` DECIMAL(10, 2) NULL, -- Totale parziale/lordo
    `discount_value` DECIMAL(10, 2) NULL, -- Valore sconto
    `discount_type` VARCHAR(50) NULL, -- Tipo sconto ('percentage' o 'flat')
    `discount_amount` DECIMAL(10, 2) NULL, -- Importo sconto effettivo
    `insurance_covered_amount` DECIMAL(10, 2) NULL, -- Quota coperta da assicurazione
    `amount_due` DECIMAL(10, 2) NOT NULL, -- Quota a carico paziente (o totale se no ass)
    `amount_paid` DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    `payment_status` ENUM('unpaid', 'partially_paid', 'paid', 'refunded') NOT NULL DEFAULT 'unpaid',
    `payment_method` VARCHAR(50) NULL,
    `paid_at` TIMESTAMP NULL DEFAULT NULL,
    `is_insurance_invoice` TINYINT(1) NOT NULL DEFAULT 0, -- Se è fattura intestata ad assicurazione
    `is_credit_note` TINYINT(1) NOT NULL DEFAULT 0, -- Se è una nota di credito
    `stamp_duty` DECIMAL(10, 2) NOT NULL DEFAULT 0.00, -- Imposta di bollo
    `custom_rates` JSON NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`admission_id`) REFERENCES `admissions`(`id`) ON DELETE RESTRICT,
    FOREIGN KEY (`appointment_id`) REFERENCES `appointments`(`id`) ON DELETE SET NULL,
    FOREIGN KEY (`sample_id`) REFERENCES `lab_samples`(`id`) ON DELETE SET NULL,
    FOREIGN KEY (`study_id`) REFERENCES `radiology_studies`(`id`) ON DELETE SET NULL,
    FOREIGN KEY (`price_list_id`) REFERENCES `price_lists`(`id`) ON DELETE SET NULL,
    FOREIGN KEY (`claim_id`) REFERENCES `patient_claims`(`id`) ON DELETE SET NULL,
    INDEX `idx_invoice_status` (`payment_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: prima_nota_movements (Registro dei movimenti di cassa Prima Nota)
CREATE TABLE IF NOT EXISTS `prima_nota_movements` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `date` DATE NOT NULL,
    `description` VARCHAR(255) NOT NULL,
    `type` ENUM('entrata', 'uscita') NOT NULL,
    `payment_method` VARCHAR(50) NOT NULL,
    `amount` DECIMAL(10, 2) NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ----------------------------------------------------------------------------
-- 7. HRIS (HUMAN RESOURCES INFORMATION SYSTEM) SHIFTS MODULE
-- ----------------------------------------------------------------------------

-- Table: shifts (Turni del personale sanitario)
CREATE TABLE IF NOT EXISTS `shifts` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `staff_id` INT NOT NULL,
    `clinic_id` INT NULL,
    `start_time` DATETIME NOT NULL,
    `end_time` DATETIME NOT NULL,
    `role_assigned` VARCHAR(100) NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`staff_id`) REFERENCES `staff`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`clinic_id`) REFERENCES `clinics`(`id`) ON DELETE SET NULL,
    INDEX `idx_shift_time` (`start_time`, `end_time`),
    CONSTRAINT `chk_shift_times` CHECK (`end_time` > `start_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: system_settings (Impostazioni generali del sistema)
CREATE TABLE IF NOT EXISTS `system_settings` (
    `setting_key` VARCHAR(100) PRIMARY KEY,
    `setting_value` TEXT NOT NULL,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: lis_worksheets (Configurazioni Fogli di lavoro LIS)
CREATE TABLE IF NOT EXISTS `lis_worksheets` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL,
    `service_ids` TEXT NOT NULL, -- JSON array of medical_service IDs
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: lab_reports (Referti e bozze LIS)
CREATE TABLE IF NOT EXISTS `lab_reports` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `session_uid` VARCHAR(50) NOT NULL,
    `status` ENUM('preliminary', 'official') NOT NULL DEFAULT 'preliminary',
    `notes` TEXT NULL,
    `released_at` VARCHAR(50) NULL,
    `released_by` INT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE INDEX `uq_session_uid` (`session_uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: consent_templates (Modelli per consensi informati)
CREATE TABLE IF NOT EXISTS `consent_templates` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(255) NOT NULL,
    `content` TEXT NOT NULL,
    `scope` VARCHAR(50) NOT NULL DEFAULT 'all', -- 'all', 'gender_age', 'by_modality', 'by_doctor'
    `modality` VARCHAR(50) NULL,
    `doctor_id` INT NULL,
    `min_age` INT NULL,
    `max_age` INT NULL,
    `gender` VARCHAR(10) NOT NULL DEFAULT 'all',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`doctor_id`) REFERENCES `doctors`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: lis_microbiology_organisms (Tabella parametrica microrganismi)
CREATE TABLE IF NOT EXISTS `lis_microbiology_organisms` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `code` VARCHAR(50) NOT NULL UNIQUE,
    `name` VARCHAR(255) NOT NULL,
    `active` TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: lis_microbiology_antibiotics (Tabella parametrica antibiotici)
CREATE TABLE IF NOT EXISTS `lis_microbiology_antibiotics` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `code` VARCHAR(50) NOT NULL UNIQUE,
    `name` VARCHAR(255) NOT NULL,
    `active` TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;



-- Table: lis_microbiology_results (Risultati esami microbiologici)
CREATE TABLE IF NOT EXISTS `lis_microbiology_results` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `test_id` INT NOT NULL,
    `is_negative` TINYINT(1) NOT NULL DEFAULT 1,
    `notes` TEXT NULL,
    `germ1_id` INT NULL,
    `germ1_antibiotics` TEXT NULL,
    `germ2_id` INT NULL,
    `germ2_antibiotics` TEXT NULL,
    `germ3_id` INT NULL,
    `germ3_antibiotics` TEXT NULL,
    FOREIGN KEY (`test_id`) REFERENCES `lab_tests`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


