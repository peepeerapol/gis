use master


/* ข้อ 4 a */
SELECT county,city FROM master.dbo.AirPollutionPM25
WHERE pm25 > 50 AND years = 2015 
ORDER BY county


/* ข้อ 4 b */
SELECT county, AVG(pm25) AS AVGpm25 FROM master.dbo.AirPollutionPM25
Group by county
ORDER by AVGpm25 DESC


/* ข้อ 4 c */
/* in route cal_historical | ex. county = 'Germany' */
SELECT years,city,pm25 FROM dbo.AirPollutionPM25 
WHERE county = 'Germany' ORDER BY years,city

/* ข้อ 4 d */
/* route cal_affected | ex. years = 2013 AND color_pm25 = 'darkred' */
SELECT SUM(populations) as total_pop FROM dbo.AirPollutionPM25 
WHERE years = 2013 AND color_pm25 = 'darkred'