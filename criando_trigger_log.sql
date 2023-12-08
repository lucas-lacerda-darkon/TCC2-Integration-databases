-- Conecte-se ao Database1
USE Database2;
GO

-- Cria��o da trigger na tabela dados1
CREATE TRIGGER TriggerLog
ON dados
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    DECLARE @Tipo CHAR(1);
    DECLARE @Enviado CHAR(1);

    IF EXISTS (SELECT * FROM INSERTED) AND EXISTS (SELECT * FROM DELETED)
        SET @Tipo = 'U'; -- Atualiza��o
    ELSE IF EXISTS (SELECT * FROM INSERTED)
        SET @Tipo = 'I'; -- Inser��o
    ELSE IF EXISTS (SELECT * FROM DELETED)
        SET @Tipo = 'D'; -- Exclus�o

    -- Obt�m o ID da �ltima inser��o na tabela de log
    DECLARE @LogID INT;
    SELECT @LogID = MAX(ID) + 1 FROM LogTable;

    -- Insere o registro na tabela de log
    INSERT INTO LogTable (ID, ID_DADOS, Tipo, Enviado)
    VALUES (@LogID, (SELECT ID FROM INSERTED), @Tipo, (SELECT enviado FROM INSERTED));
END;
