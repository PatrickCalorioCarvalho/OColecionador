IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'OColecionadorDataBase')
BEGIN
    CREATE DATABASE OColecionadorDataBase;
END
GO
IF NOT EXISTS (SELECT name FROM sys.server_principals WHERE name = N'OColecionadorUser')
BEGIN
    CREATE LOGIN OColecionadorUser WITH PASSWORD = 'OColecionador@2025';
END
GO
USE OColecionadorDataBase;
GO
IF NOT EXISTS (SELECT name FROM sys.database_principals WHERE name = N'OColecionadorUser')
BEGIN
    CREATE USER OColecionadorUser FOR LOGIN OColecionadorUser;
END
GO
ALTER ROLE db_owner ADD MEMBER OColecionadorUser;
GO