
USE tennis_analytics;

-- ==========================================
-- SECTION A: COMPETITIONS (Queries 1–7)
-- ==========================================

-- 1. Display all competitions
SELECT *
FROM competitions;

-- 2. Count total competitions
SELECT COUNT(*) AS total_competitions
FROM competitions;

-- 3. Count competitions by gender
SELECT gender, COUNT(*) AS total
FROM competitions
GROUP BY gender
ORDER BY total DESC;

-- 4. Count competitions by type
SELECT competition_type, COUNT(*) AS total
FROM competitions
GROUP BY competition_type
ORDER BY total DESC;

-- 5. Show competitions with their category names
SELECT c.competition_name, c.competition_type,
       c.gender, cat.category_name
FROM competitions c
LEFT JOIN categories cat
    ON c.category_id = cat.category_id
ORDER BY c.competition_name;

-- 6. Find the top 10 categories with the most competitions
SELECT cat.category_name, COUNT(c.competition_id) AS total
FROM categories cat
LEFT JOIN competitions c
    ON cat.category_id = c.category_id
GROUP BY cat.category_id, cat.category_name
ORDER BY total DESC
LIMIT 10;

-- 7. Find competitions whose names contain "Davis"
SELECT competition_id, competition_name, gender
FROM competitions
WHERE competition_name LIKE '%Davis%'
ORDER BY competition_name;


-- ==========================================
-- SECTION B: COMPLEXES AND VENUES (Queries 8–14)
-- ==========================================

-- 8. Display all complexes
SELECT *
FROM complexes;

-- 9. Count total complexes
SELECT COUNT(*) AS total_complexes
FROM complexes;

-- 10. Display all venues with their complex names
SELECT v.venue_name, v.city_name, v.country_name,
       c.complex_name
FROM venues v
LEFT JOIN complexes c
    ON v.complex_id = c.complex_id
ORDER BY v.venue_name;

-- 11. Find the top 10 countries with the most venues
SELECT country_name, COUNT(*) AS total_venues
FROM venues
WHERE country_name IS NOT NULL
GROUP BY country_name
ORDER BY total_venues DESC
LIMIT 10;

-- 12. Count venues in each city
SELECT city_name, COUNT(*) AS total_venues
FROM venues
WHERE city_name IS NOT NULL
GROUP BY city_name
ORDER BY total_venues DESC
LIMIT 20;

-- 13. Find complexes with the most venues
SELECT c.complex_name, COUNT(v.venue_id) AS total_venues
FROM complexes c
LEFT JOIN venues v
    ON c.complex_id = v.complex_id
GROUP BY c.complex_id, c.complex_name
ORDER BY total_venues DESC
LIMIT 10;

-- 14. Search for venues in a particular country
-- Replace 'Australia' with another country if desired
SELECT venue_name, city_name, country_name
FROM venues
WHERE country_name = 'Australia'
ORDER BY city_name, venue_name;


-- ==========================================
-- SECTION C: COMPETITORS AND RANKINGS (Queries 15–20)
-- ==========================================

-- 15. Display the top 10 ranked competitors
SELECT cr.rank_position, c.competitor_name,
       cr.points, cr.competitions_played
FROM competitor_rankings cr
JOIN competitors c
    ON cr.competitor_id = c.competitor_id
ORDER BY cr.rank_position ASC
LIMIT 10;

-- 16. Count competitors by country
SELECT country, COUNT(*) AS total_competitors
FROM competitors
WHERE country IS NOT NULL
GROUP BY country
ORDER BY total_competitors DESC
LIMIT 10;

-- 17. Find competitors with the highest ranking points
SELECT c.competitor_name, cr.rank_position, cr.points
FROM competitor_rankings cr
JOIN competitors c
    ON cr.competitor_id = c.competitor_id
ORDER BY cr.points DESC
LIMIT 10;

-- 18. Find competitors who played the most competitions
SELECT c.competitor_name, cr.competitions_played,
       cr.rank_position
FROM competitor_rankings cr
JOIN competitors c
    ON cr.competitor_id = c.competitor_id
ORDER BY cr.competitions_played DESC
LIMIT 10;

-- 19. Show ranking information by ranking group and gender
SELECT ranking_type_name, gender,
       COUNT(*) AS ranked_competitors,
       AVG(points) AS average_points
FROM competitor_rankings
GROUP BY ranking_type_name, gender
ORDER BY ranking_type_name, gender;

-- 20. Search for a competitor by name
-- Replace 'Novak' with any name you want to search
SELECT c.competitor_name, c.country,
       cr.rank_position, cr.points
FROM competitors c
LEFT JOIN competitor_rankings cr
    ON c.competitor_id = cr.competitor_id
WHERE c.competitor_name LIKE '%Novak%'
ORDER BY cr.rank_position;
