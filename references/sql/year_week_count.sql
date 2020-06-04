/*
 * To use this query effectively, you simply need to adjust the variable that is being used, but also you need to update the "GROUP BY" clause to reflect the reference.
 * Also, as you derrive new queries from this one, set the limit to be low (ie: 100-200 records) so development is fast.  Then eliminate the limit for all rows.
 * Part of this query can be string formatted for new variables to create programatic versions.
 */
SELECT
	"station_id",
	/* 
	 *  The DATE is in a text format and looks like it's dropped the time resolution (easy fix).  We can still work with the data and bin common values.
	 */
	DATE_PART('year',  TO_DATE("DATE", 'YYYY-MM-DD')) AS year, 
	-- DATE_PART('month', TO_DATE("DATE", 'YYYY-MM-DD')) AS month, 
	DATE_PART('week',  TO_DATE("DATE", 'YYYY-MM-DD')) AS week,	
	"HourlyDryBulbTemperature",
	COUNT("HourlyDryBulbTemperature")
	/* 
	 *  From here, you can replace specific attributes to work with for aggregation.
	 */
	-- "HourlyVisibility",
	-- "HourlyPressureChange", 
	-- "HourlyPrecipitation", 
	-- "HourlyPressureTendency", 
	-- "HourlyWetBulbTemperature", 
	-- "HourlyAltimeterSetting", 
	-- "HourlyDryBulbTemperature", 
	-- "HourlySeaLevelPressure", 
	-- "HourlyRelativeHumidity", 
	-- "HourlyWindDirection", 
	-- "HourlyStationPressure", 
	-- "HourlyDewPointTemperature", 
	-- "HourlyWindGustSpeed", 
	-- "HourlyWindSpeed", 
FROM public.lcd_incoming
GROUP BY "station_id", "year", "week", "HourlyDryBulbTemperature" 
LIMIT 100

