-- Conecte-se ao Database2
USE Database2;
GO

-- Criação da tabela de log
CREATE TABLE LogTable (
    ID INT PRIMARY KEY,
    ID_DADOS INT NULL,
    Hostname VARCHAR(255) DEFAULT HOST_NAME() NULL,
    Appname VARCHAR(255) DEFAULT APP_NAME() NULL,
    Data_hora DATETIME DEFAULT GETDATE() NULL,
    Tipo CHAR(1),
    Enviado CHAR(1) NULL
);
