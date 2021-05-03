/*Step 5 a */
/*Given a <year_input> from the user, visualize all the city points of all countries*/
SELECT county,city,pm25,latitude,longitude 
FROM master.dbo.AirPollutionPM25 WHERE years = 2013

/* Step 5 b */
/* 50 Visualize the 50 closest city points to Bangkok */
SELECT TOP 50 county,city,latitude,longitude, Distance FROM 
(
    SELECT county ,city ,latitude,longitude, (ABS(NL.Latitude - 13.74622118) + ABS(NL.Longitude - 100.5544779)) / 2  as Distance 
    FROM AirPollutionPM25 AS NL
    WHERE (NL.Latitude IS NOT NULL) AND (NL.Longitude IS NOT NULL) 
	AND city != 'Bangkok'
	) AS D1 
ORDER BY Distance


/* Step 5 c */
/* Visualize all the city points of Thailand’s neighboring countries in 2018.*/
/*
DECLARE @g geography
select * from AirPollutionPM25 as a
where a.geom.MakeValid().STTouches(@g) = 1

select * from AirPollutionPM25 as a
where a.county in ('Thailand') AND a.years = 2016
*/
SELECT TOP 40 county,city,pm25,latitude,longitude, Distance FROM 
(SELECT county ,city,pm25,latitude,longitude, (ABS(NL.Latitude - 13.74622118) + ABS(NL.Longitude - 100.5544779)) / 2  as Distance 
FROM AirPollutionPM25 AS NL WHERE (NL.Latitude IS NOT NULL) AND (NL.Longitude IS NOT NULL) AND county != 'Thailand') 
AS D1  ORDER BY Distance for JSON PATH 

/* Step 5 d */
/*Visualize the four points of MBR covering all city points in Thailand in 2009.*/
select city,pm25,latitude,longitude,years from dbo.AirPollutionPM25 where county = 'Thailand' and years = 2014

/* Step 5 e */
/*Visualize all city points of countries having the highest no. of city points in 2011.*/
select county,city,pm25,latitude,longitude,years FROM dbo.AirPollutionPM25 WHERE county in(select county FROM dbo.AirPollutionPM25 WHERE years = 2011 AND pm25 in ( select Max(pm25) FROM dbo.AirPollutionPM25 where years = 2011)) order by pm25 desc


/* Step 5 f */
/*Given a <year_input> from the user, visualize all the city points which are
considered as “low income” (as specified in column wbinc16_text).*/
SELECT county,city,pm25,latitude,longitude FROM master.dbo.AirPollutionPM25 
WHERE years = 2013 AND wbinc16_text = 'Low income'