Create database Proyecto

CREATE TABLE Personas (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    Nombre NVARCHAR(50) NOT NULL,
    Apellido NVARCHAR(50) NOT NULL,
    Telefono NVARCHAR(20) UNIQUE NOT NULL,
    CorreoElectronico NVARCHAR(100) NULL
);

CREATE TABLE Contrato (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    PersonaID INT FOREIGN KEY REFERENCES Personas(ID),
    TipoContrato NVARCHAR(50), -- Ejemplo: "Alquilando departamento"
    FechaInicio DATE,
    FechaFin DATE
);

CREATE TABLE Usuarios (
		ID INT IDENTITY(1,1) PRIMARY KEY,
    Usuario NVARCHAR(50) UNIQUE NOT NULL,
    Contrasena NVARCHAR(100) NOT NULL -- La contraseña debe guardarse encriptada
);
