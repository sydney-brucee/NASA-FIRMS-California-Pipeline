-- Example queries for the detection table

-- Total detections
SELECT COUNT(*) AS total FROM detections;

-- Detections by intensity
SELECT intensity, COUNT(*) AS count
FROM detections
GROUP BY intensity
ORDER BY count DESC;

-- Daily counts
SELECT DATE(acq_date) AS day, COUNT(*) AS detections
FROM detections
GROUP BY day
ORDER BY day;

-- High FRP detections
SELECT latitude, longitude, acq_date, frp, intensity
FROM detections
WHERE frp > 50
ORDER BY frp DESC
LIMIT 20;