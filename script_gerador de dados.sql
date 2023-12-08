USE Database1;
GO

DECLARE @Counter INT = 1;

-- Loop para inserir 1 milhão de linhas
WHILE @Counter <= 1000000
BEGIN
    INSERT INTO dados (texto1, numeric1, enviado, hostname, appname)
    VALUES ('registro: ' + CAST(@Counter AS VARCHAR), @Counter, 'S', NULL, NULL);

    SET @Counter = @Counter + 1;
END;
