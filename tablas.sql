create database bd_mama;
use bd_mama;
create table producto (
id_prod varchar(5) primary key not null,
producto varchar(100),
peso decimal(7,3));

create table movimiento(
tipo_mov ENUM('S','E'),
fecha_mov date,
id_prod varchar(5) not null,
cantidad int);