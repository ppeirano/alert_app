CREATE DATABASE IF NOT EXISTS iol_alerts CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE iol_alerts;

-- Reglas de alerta
CREATE TABLE IF NOT EXISTS alert_rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type ENUM('price_level', 'price_pct_change', 'price_abs_change', 'iv_threshold') NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    mercado VARCHAR(10) DEFAULT 'bCBA',
    direction VARCHAR(10) DEFAULT 'any',
    threshold DECIMAL(12,4) NOT NULL,
    underlying VARCHAR(20),
    option_type VARCHAR(4),
    strike DECIMAL(12,2),
    expiry DATE,
    `condition` VARCHAR(10),
    cooldown_minutes INT DEFAULT 60,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Historial de precios
CREATE TABLE IF NOT EXISTS price_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    mercado VARCHAR(10) NOT NULL,
    precio DECIMAL(12,4),
    variacion DECIMAL(8,4),
    apertura DECIMAL(12,4),
    maximo DECIMAL(12,4),
    minimo DECIMAL(12,4),
    cierre_anterior DECIMAL(12,4),
    volumen BIGINT,
    iv DECIMAL(8,4),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol_ts (symbol, timestamp)
) ENGINE=InnoDB;

-- Log de alertas enviadas
CREATE TABLE IF NOT EXISTS alert_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    rule_id INT NOT NULL,
    message TEXT NOT NULL,
    price_at_trigger DECIMAL(12,4),
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rule_id) REFERENCES alert_rules(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Configuracion general
CREATE TABLE IF NOT EXISTS settings (
    key_name VARCHAR(50) PRIMARY KEY,
    value VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

INSERT IGNORE INTO settings (key_name, value) VALUES
    ('iol_username', ''),
    ('iol_password', ''),
    ('telegram_bot_token', ''),
    ('telegram_chat_id', ''),
    ('risk_free_rate', '0.40'),
    ('poll_interval_minutes', '2'),
    ('market_open', '11:00'),
    ('market_close', '17:00');
