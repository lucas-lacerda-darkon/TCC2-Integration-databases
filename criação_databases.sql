-- Criação do Database 1
CREATE DATABASE Database1;
GO

USE Database1;
GO

-- Criação da tabela "dados" no Database 1
CREATE TABLE dados (
    id INT PRIMARY KEY IDENTITY(1,1),
    texto1 VARCHAR(150),
    numeric1 NUMERIC(15),
    data_hora DATETIME DEFAULT GETDATE(),
    enviado CHAR(1) CHECK (enviado IN ('S', 'P', 'E')),
    hostname VARCHAR(255) NULL, -- Aceita valores NULL
    appname VARCHAR(255) NULL,  -- Aceita valores NULL
    rowversion ROWVERSION
);

-- Criação do Database 2
CREATE DATABASE Database2;
GO

USE Database2;
GO

-- Criação da tabela "dados" no Database 2 (mesma estrutura)
CREATE TABLE dados (
    id INT PRIMARY KEY IDENTITY(1,1),
    texto1 VARCHAR(150),
    numeric1 NUMERIC(15),
    data_hora DATETIME DEFAULT GETDATE(),
    enviado CHAR(1) CHECK (enviado IN ('S', 'P', 'E')),
    hostname VARCHAR(255) NULL, -- Aceita valores NULL
    appname VARCHAR(255) NULL,  -- Aceita valores NULL
    rowversion ROWVERSION
);
