-- Analytics views for the detections table

-- Daily summary
CREATE VIEW IF NOT EXISTS daily_summary AS
SELECT
    DATE(acq_date) AS day,
    COUNT(*) AS detections,
    ROUND(AVG(frp), 2) AS avg_frp,
    ROUND(MAX(frp), 2) AS max_frp,
    ROUND(AVG(bright_ti4), 2) AS avg_brightness
FROM detections
GROUP BY day
ORDER BY day;

-- Intensity breakdown
CREATE VIEW IF NOT EXISTS intensity_summary AS
SELECT
    intensity,
    COUNT(*) AS detections,
    ROUND(AVG(frp), 2) AS avg_frp,
    ROUND(MAX(frp), 2) AS max_frp
FROM detections
GROUP BY intensity
ORDER BY detections DESC;

-- High FRP detections (FRP > 50)
CREATE VIEW IF NOT EXISTS high_frp AS
SELECT
    latitude,
    longitude,
    acq_date,
    acq_time,
    satellite,
    frp,
    bright_ti4,
    intensity
FROM detections
WHERE frp > 50
ORDER BY frp DESC;

-- Satellite comparison
CREATE VIEW IF NOT EXISTS satellite_summary AS
SELECT
    satellite,
    COUNT(*) AS detections,
    ROUND(AVG(frp), 2) AS avg_frp,
    ROUND(MAX(frp), 2) AS max_frp
FROM detections
GROUP BY satellite
ORDER BY detections DESC;