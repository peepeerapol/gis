/*CREATE TABLE*/
CREATE TABLE AirPollutionPM25 ( 
    country             varchar(50),     
    city                varchar(50),      
    years               int,
    Pm25                float,
    latitude            float,
    longitude           float,
    populations         int,
    wbinc16_text        varchar(50),
    Region              varchar(50),
    conc_pm25           varchar(50),
    color_pm25          varchar(50) );


/*GeomFromText*/
alter table AirPollutionPM25 
add geom as geography::STGeomFromText('POINT('+convert(varchar(20),longitude)+' '+convert(varchar(20),latitude)+')',4326)
