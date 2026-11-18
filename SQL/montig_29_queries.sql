/* =====================================================================
   Montig - Social Media & Productivity
   Five-Dashboard Business Intelligence Plan: 29 SQL queries
   Table   : social_media_vs_productivity (29,863 records, 19 features)
   Dialect : SQL Server
   Note    : numeric columns are tinyint, so averages are cast to FLOAT.
   ===================================================================== */


/* =====================================================================
   DASHBOARD 01 - Social Media Usage Overview
   ===================================================================== */

-- D1-Q1 | EASY | How does preferred social media platform vary across job types?
-- Finding: Instagram is top in 6 of 7 job types; Students prefer TikTok (39.5%).
SELECT
    job_type,
    social_platform_preference,
    COUNT(*) AS user_count
FROM social_media_vs_productivity
GROUP BY job_type, social_platform_preference
ORDER BY job_type, user_count DESC;
GO

-- D1-Q2 | EASY | How does the number of notifications differ between users of different preferred platforms?
-- Finding: TikTok users get 78.27 a day, Facebook users only 48.56.
SELECT
    social_platform_preference,
    COUNT(*) AS total_users,
    ROUND(AVG(CAST(number_of_notifications AS FLOAT)), 2) AS avg_notifications
FROM social_media_vs_productivity
GROUP BY social_platform_preference
ORDER BY avg_notifications DESC;
GO

-- D1-Q3 | MEDIUM | Which job types combine high daily social media time with high notification exposure?
-- Finding: Only Student passes both filters (3.29 hrs, 82.11 notifications).
SELECT
    job_type,
    ROUND(AVG(CAST(daily_social_media_time AS FLOAT)), 2) AS avg_daily_social_media_time,
    ROUND(AVG(CAST(number_of_notifications AS FLOAT)), 2) AS avg_notifications
FROM social_media_vs_productivity
GROUP BY job_type
HAVING AVG(CAST(daily_social_media_time AS FLOAT)) > (SELECT AVG(CAST(daily_social_media_time AS FLOAT)) FROM social_media_vs_productivity)
   AND AVG(CAST(number_of_notifications AS FLOAT)) > (SELECT AVG(CAST(number_of_notifications AS FLOAT)) FROM social_media_vs_productivity)
ORDER BY avg_daily_social_media_time DESC;
GO

-- D1-Q4 | MEDIUM | How does preferred platform usage differ across age groups?
-- Finding: TikTok under 25, Instagram at 25-40, Facebook at 41-55 and above 55.
WITH SegmentedData AS (
    SELECT
        social_platform_preference,
        CASE
            WHEN age < 25 THEN 'Under 25'
            WHEN age BETWEEN 25 AND 40 THEN '25-40'
            WHEN age BETWEEN 41 AND 55 THEN '41-55'
            ELSE 'Above 55'
        END AS age_group
    FROM social_media_vs_productivity
)
SELECT
    age_group,
    social_platform_preference,
    COUNT(*) AS user_count
FROM SegmentedData
GROUP BY
    age_group,
    social_platform_preference
ORDER BY age_group, user_count DESC;
GO

-- D1-Q5 | MEDIUM | How does social media time compare between users with low, medium and high notification exposure?
-- Finding: High-exposure users spend 3.81 hrs, over 3x the 1.14 hrs of the low group.
WITH SegmentedData AS (
    SELECT
        daily_social_media_time,
        CASE
            WHEN number_of_notifications < 40 THEN 'Low (<40)'
            WHEN number_of_notifications BETWEEN 40 AND 80 THEN 'Medium (40-80)'
            ELSE 'High (>80)'
        END AS notification_exposure_level
    FROM social_media_vs_productivity
)
SELECT
    notification_exposure_level,
    COUNT(*) AS total_users,
    ROUND(AVG(CAST(daily_social_media_time AS FLOAT)), 2) AS avg_daily_social_media_time
FROM SegmentedData
GROUP BY notification_exposure_level
ORDER BY avg_daily_social_media_time DESC;
GO


/* =====================================================================
   DASHBOARD 02 - Productivity & Work Performance
   ===================================================================== */

-- D2-Q1 | EASY | How does productivity score vary across job types?
-- Finding: Unemployed highest (7.24), Student lowest (6.22).
SELECT
    job_type,
    COUNT(*) AS total_users,
    ROUND(AVG(CAST(actual_productivity_score AS FLOAT)), 2) AS avg_productivity_score
FROM social_media_vs_productivity
GROUP BY job_type
ORDER BY avg_productivity_score DESC;
GO

-- D2-Q2 | EASY | How does productivity differ between users with different daily work-hour ranges?
-- Finding: Productivity falls as work hours rise: 7.22 under 6 hrs to 5.50 above 10 hrs.
SELECT
    work_hours_range,
    COUNT(*) AS total_users,
    ROUND(AVG(CAST(actual_productivity_score AS FLOAT)), 2) AS avg_productivity_score
FROM (
    SELECT
        actual_productivity_score,
        CASE
            WHEN work_hours_per_day < 6 THEN 'Short (<6 hrs)'
            WHEN work_hours_per_day BETWEEN 6 AND 8 THEN 'Standard (6-8 hrs)'
            WHEN work_hours_per_day > 8 AND work_hours_per_day <= 10 THEN 'Long (8-10 hrs)'
            ELSE 'Very Long (>10 hrs)'
        END AS work_hours_range
    FROM social_media_vs_productivity
) AS t
GROUP BY work_hours_range
ORDER BY avg_productivity_score DESC;
GO

-- D2-Q3 | MEDIUM | How does productivity change across daily coffee consumption levels?
-- Finding: Coffee barely moves productivity, but heavy drinkers (4+ cups) work 8.71 hrs vs 6.43.
SELECT
    coffee_level,
    COUNT(*) AS total_users,
    ROUND(AVG(CAST(actual_productivity_score AS FLOAT)), 2) AS avg_productivity,
    ROUND(AVG(CAST(work_hours_per_day AS FLOAT)), 2) AS avg_work_hours
FROM (
    SELECT
        actual_productivity_score,
        work_hours_per_day,
        CASE
            WHEN coffee_consumption_per_day = 0 THEN 'No Coffee (0 cups)'
            WHEN coffee_consumption_per_day BETWEEN 1 AND 2 THEN 'Light (1-2 cups)'
            WHEN coffee_consumption_per_day = 3 THEN 'Moderate (3 cups)'
            ELSE 'Heavy (4+ cups)'
        END AS coffee_level
    FROM social_media_vs_productivity
) AS t
GROUP BY coffee_level
ORDER BY avg_productivity DESC;
GO

-- D2-Q4 | MEDIUM | How does productivity change across different levels of daily social media use?
-- Finding: 7.74 under 2 hrs, 6.35 for 2-4 hrs, 4.37 above 4 hrs.
SELECT
    social_media_level,
    COUNT(*) AS total_users,
    ROUND(AVG(CAST(actual_productivity_score AS FLOAT)), 2) AS avg_productivity
FROM (
    SELECT
        actual_productivity_score,
        CASE
            WHEN daily_social_media_time < 2 THEN 'Low (<2 hrs)'
            WHEN daily_social_media_time BETWEEN 2 AND 4 THEN 'Moderate (2-4 hrs)'
            ELSE 'High (>4 hrs)'
        END AS social_media_level
    FROM social_media_vs_productivity
) AS t
GROUP BY social_media_level
ORDER BY avg_productivity DESC;
GO

-- D2-Q5 | MEDIUM | How do work hours and productivity compare across age groups?
-- Finding: Under 25 least productive (6.26); above 55 most (7.03) with fewest work hours (6.32).
SELECT
    age_group,
    COUNT(*) AS total_users,
    ROUND(AVG(CAST(work_hours_per_day AS FLOAT)), 2) AS avg_work_hours,
    ROUND(AVG(CAST(actual_productivity_score AS FLOAT)), 2) AS avg_productivity
FROM (
    SELECT
        work_hours_per_day,
        actual_productivity_score,
        CASE
            WHEN age < 25 THEN 'Under 25'
            WHEN age BETWEEN 25 AND 40 THEN '25-40'
            WHEN age BETWEEN 41 AND 55 THEN '41-55'
            ELSE 'Above 55'
        END AS age_group
    FROM social_media_vs_productivity
) AS t
GROUP BY age_group
ORDER BY avg_productivity DESC;
GO

-- D2-Q6 | HARD | Which job type has the strongest productivity profile when social media time, work hours and productivity are analyzed together?
-- Finding: Unemployed strongest (2.43 productivity per work hour); Health weakest (0.76).
SELECT
    job_type,
    ROUND(AVG(CAST(actual_productivity_score AS FLOAT)), 2) AS avg_productivity,
    ROUND(AVG(CAST(daily_social_media_time AS FLOAT)), 2) AS avg_social_media_time,
    ROUND(AVG(CAST(work_hours_per_day AS FLOAT)), 2) AS avg_work_hours,
    ROUND(AVG(actual_productivity_score / NULLIF(CAST(work_hours_per_day AS FLOAT), 0)), 2) AS productivity_per_work_hour,
    ROUND(AVG(actual_productivity_score / NULLIF(CAST(daily_social_media_time AS FLOAT), 0)), 2) AS productivity_per_sm_hour
FROM social_media_vs_productivity
GROUP BY job_type
ORDER BY productivity_per_work_hour DESC, avg_productivity DESC;
GO


/* =====================================================================
   DASHBOARD 03 - Wellbeing, Sleep & Burnout
   ===================================================================== */

-- D3-Q1 | EASY | How does burnout frequency vary across job types?
-- Finding: Health has the most burnout days (3.28); Unemployed the fewest (1.51).
SELECT
    job_type,
    COUNT(*) AS total_users,
    ROUND(AVG(CAST(days_feeling_burnout_per_month AS FLOAT)), 2) AS avg_burnout_days
FROM social_media_vs_productivity
GROUP BY job_type
ORDER BY avg_burnout_days DESC;
GO

-- D3-Q2 | EASY | How does sleep duration differ across age groups?
-- Finding: Sleep is almost the same in every age group: 7.31 to 7.43 hrs.
SELECT
    age_group,
    COUNT(*) AS total_users,
    ROUND(AVG(CAST(sleep_hours AS FLOAT)), 2) AS avg_sleep_hours
FROM (
    SELECT
        sleep_hours,
        CASE
            WHEN age < 25 THEN 'Under 25'
            WHEN age BETWEEN 25 AND 40 THEN '25-40'
            WHEN age BETWEEN 41 AND 55 THEN '41-55'
            ELSE 'Above 55'
        END AS age_group
    FROM social_media_vs_productivity
) AS t
GROUP BY age_group
ORDER BY avg_sleep_hours DESC;
GO

-- D3-Q3 | MEDIUM | How do sleep duration and stress level differ across daily coffee consumption levels?
-- Finding: Stress rises from 3.04 (none) to 3.88 (4+ cups); sleep dips from 7.43 to 7.30 hrs.
SELECT
    coffee_level,
    COUNT(*) AS total_users,
    ROUND(AVG(CAST(sleep_hours AS FLOAT)), 2) AS avg_sleep_hours,
    ROUND(AVG(CAST(stress_level AS FLOAT)), 2) AS avg_stress_level
FROM (
    SELECT
        sleep_hours,
        stress_level,
        CASE
            WHEN coffee_consumption_per_day = 0 THEN 'No Coffee (0 cups)'
            WHEN coffee_consumption_per_day BETWEEN 1 AND 2 THEN 'Light (1-2 cups)'
            WHEN coffee_consumption_per_day = 3 THEN 'Moderate (3 cups)'
            ELSE 'Heavy (4+ cups)'
        END AS coffee_level
    FROM social_media_vs_productivity
) AS t
GROUP BY coffee_level
ORDER BY avg_sleep_hours DESC;
GO

-- D3-Q4 | MEDIUM | How does job satisfaction differ across burnout-frequency groups?
-- Finding: Satisfaction falls as burnout rises: 8.03 (none) to 7.09 (7+ days).
SELECT
    burnout_group,
    COUNT(*) AS total_users,
    ROUND(AVG(CAST(job_satisfaction_score AS FLOAT)), 2) AS avg_job_satisfaction
FROM (
    SELECT
        job_satisfaction_score,
        CASE
            WHEN days_feeling_burnout_per_month = 0 THEN 'No Burnout (0 days)'
            WHEN days_feeling_burnout_per_month BETWEEN 1 AND 3 THEN 'Low (1-3 days)'
            WHEN days_feeling_burnout_per_month BETWEEN 4 AND 6 THEN 'Moderate (4-6 days)'
            ELSE 'High (7+ days)'
        END AS burnout_group
    FROM social_media_vs_productivity
) AS t
GROUP BY burnout_group
ORDER BY avg_job_satisfaction DESC;
GO

-- D3-Q5 | MEDIUM | How does sleep duration relate to burnout frequency across age groups?
-- Finding: In every age group, sleep drops from 7.52-7.58 hrs (no burnout) to 6.96-7.16 hrs (7+ days).
SELECT
    age_group,
    burnout_group,
    COUNT(*) AS total_users,
    ROUND(AVG(CAST(sleep_hours AS FLOAT)), 2) AS avg_sleep_hours
FROM (
    SELECT
        sleep_hours,
        CASE
            WHEN age < 25 THEN 'Under 25'
            WHEN age BETWEEN 25 AND 40 THEN '25-40'
            WHEN age BETWEEN 41 AND 55 THEN '41-55'
            ELSE 'Above 55'
        END AS age_group,
        CASE
            WHEN days_feeling_burnout_per_month = 0 THEN 'No Burnout (0 days)'
            WHEN days_feeling_burnout_per_month BETWEEN 1 AND 3 THEN 'Low (1-3 days)'
            WHEN days_feeling_burnout_per_month BETWEEN 4 AND 6 THEN 'Moderate (4-6 days)'
            ELSE 'High (7+ days)'
        END AS burnout_group
    FROM social_media_vs_productivity
) AS t
GROUP BY age_group, burnout_group
ORDER BY age_group, burnout_group;
GO

-- D3-Q6 | HARD | Which age group and job type combination shows the highest wellbeing risk (low sleep, high stress, frequent burnout)?
-- Finding: Age 25-40 in IT: 762 high-risk users, 6.21 hrs sleep, 5.17 stress, 5.88 burnout days.
SELECT TOP 1
    age_group,
    job_type,
    COUNT(*) AS high_risk_user_count,
    ROUND(AVG(CAST(sleep_hours AS FLOAT)), 2) AS avg_sleep_hours,
    ROUND(AVG(CAST(stress_level AS FLOAT)), 2) AS avg_stress_level,
    ROUND(AVG(CAST(days_feeling_burnout_per_month AS FLOAT)), 2) AS avg_burnout_days
FROM (
    SELECT
        job_type,
        sleep_hours,
        stress_level,
        days_feeling_burnout_per_month,
        CASE
            WHEN age < 25 THEN 'Under 25'
            WHEN age BETWEEN 25 AND 40 THEN '25-40'
            WHEN age BETWEEN 41 AND 55 THEN '41-55'
            ELSE 'Above 55'
        END AS age_group
    FROM social_media_vs_productivity
    WHERE sleep_hours < (SELECT AVG(CAST(sleep_hours AS FLOAT)) FROM social_media_vs_productivity)
      AND stress_level > (SELECT AVG(CAST(stress_level AS FLOAT)) FROM social_media_vs_productivity)
      AND days_feeling_burnout_per_month > (SELECT AVG(CAST(days_feeling_burnout_per_month AS FLOAT)) FROM social_media_vs_productivity)
) AS high_risk_users
GROUP BY
    age_group,
    job_type
ORDER BY
    high_risk_user_count DESC;
GO


/* =====================================================================
   DASHBOARD 04 - Digital Habits & Focus
   ===================================================================== */

-- D4-Q1 | EASY | How does focus-app adoption vary across job types?
-- Finding: Fairly flat: 34.31% (Student) to 38.13% (Other).
SELECT
    job_type,
    COUNT(*) AS total_users,
    COUNT(CASE WHEN uses_focus_apps = 1 OR uses_focus_apps = 'True' THEN 1 END) AS focus_app_users,
    ROUND(
        (COUNT(CASE WHEN uses_focus_apps = 1 OR uses_focus_apps = 'True' THEN 1 END) * 100.0) / COUNT(*),
        2
    ) AS adoption_rate_pct
FROM social_media_vs_productivity
GROUP BY job_type
ORDER BY adoption_rate_pct DESC;
GO

-- D4-Q2 | EASY | How does digital wellbeing adoption differ across age groups?
-- Finding: Similar across ages: 40.91% (under 25) to 42.89% (above 55).
SELECT
    age_group,
    COUNT(*) AS total_users,
    COUNT(CASE WHEN has_digital_wellbeing_enabled = 1 OR has_digital_wellbeing_enabled = 'True' THEN 1 END) AS wellbeing_users,
    ROUND(
        (COUNT(CASE WHEN has_digital_wellbeing_enabled = 1 OR has_digital_wellbeing_enabled = 'True' THEN 1 END) * 100.0) / COUNT(*),
        2
    ) AS adoption_rate_pct
FROM (
    SELECT
        has_digital_wellbeing_enabled,
        CASE
            WHEN age < 25 THEN 'Under 25'
            WHEN age BETWEEN 25 AND 40 THEN '25-40'
            WHEN age BETWEEN 41 AND 55 THEN '41-55'
            ELSE 'Above 55'
        END AS age_group
    FROM social_media_vs_productivity
) AS t
GROUP BY age_group
ORDER BY adoption_rate_pct DESC;
GO

-- D4-Q3 | MEDIUM | How does screen time before sleep compare between users with and without digital wellbeing enabled?
-- Finding: Enabled users have slightly lower pre-sleep screen time: 0.99 vs 1.06 hrs.
SELECT
    CASE
        WHEN has_digital_wellbeing_enabled = 1 OR has_digital_wellbeing_enabled = 'True' THEN 'Enabled'
        ELSE 'Disabled'
    END AS digital_wellbeing_status,
    COUNT(*) AS total_users,
    ROUND(AVG(CAST(screen_time_before_sleep AS FLOAT)), 2) AS avg_pre_sleep_screen_time
FROM social_media_vs_productivity
GROUP BY has_digital_wellbeing_enabled;
GO

-- D4-Q4 | MEDIUM | How do work breaks differ between focus-app users and non-users across job types?
-- Finding: Focus-app users take 0.23-0.46 more breaks than non-users in every job type.
SELECT
    job_type,
    ROUND(AVG(CASE WHEN uses_focus_apps = 1 OR uses_focus_apps = 'True' THEN CAST(breaks_during_work AS FLOAT) END), 2) AS avg_breaks_focus_users,
    ROUND(AVG(CASE WHEN uses_focus_apps = 0 OR uses_focus_apps = 'False' THEN CAST(breaks_during_work AS FLOAT) END), 2) AS avg_breaks_non_users,
    ROUND(
        AVG(CASE WHEN uses_focus_apps = 1 OR uses_focus_apps = 'True' THEN CAST(breaks_during_work AS FLOAT) END) -
        AVG(CASE WHEN uses_focus_apps = 0 OR uses_focus_apps = 'False' THEN CAST(breaks_during_work AS FLOAT) END),
        2
    ) AS difference_in_breaks
FROM social_media_vs_productivity
GROUP BY job_type
ORDER BY job_type;
GO

-- D4-Q5 | MEDIUM | How does productivity differ for focus-app users versus non-users at different screen-time levels?
-- Finding: Focus-app users are more productive at every level: +1.26 (low), +1.33 (moderate), +1.08 (high).
SELECT
    screen_time_level,
    ROUND(AVG(CASE WHEN uses_focus_apps = 1 OR uses_focus_apps = 'True' THEN CAST(actual_productivity_score AS FLOAT) END), 2) AS avg_prod_focus_users,
    ROUND(AVG(CASE WHEN uses_focus_apps = 0 OR uses_focus_apps = 'False' THEN CAST(actual_productivity_score AS FLOAT) END), 2) AS avg_prod_non_users,
    ROUND(
        AVG(CASE WHEN uses_focus_apps = 1 OR uses_focus_apps = 'True' THEN CAST(actual_productivity_score AS FLOAT) END) -
        AVG(CASE WHEN uses_focus_apps = 0 OR uses_focus_apps = 'False' THEN CAST(actual_productivity_score AS FLOAT) END),
        2
    ) AS productivity_boost
FROM (
    SELECT
        actual_productivity_score,
        uses_focus_apps,
        CASE
            WHEN daily_social_media_time < 2 THEN 'Low (<2 hrs)'
            WHEN daily_social_media_time BETWEEN 2 AND 4 THEN 'Moderate (2-4 hrs)'
            ELSE 'High (>4 hrs)'
        END AS screen_time_level
    FROM social_media_vs_productivity
) AS t
GROUP BY screen_time_level
ORDER BY avg_prod_focus_users DESC;
GO

-- D4-Q6 | HARD | Among users with digital wellbeing enabled, which job type combines lower pre-sleep screen time, more work breaks and higher productivity?
-- Finding: Unemployed leads on productivity (7.50) with the fewest breaks; Student has the most pre-sleep screen time (1.22) and lowest productivity (6.47).
SELECT
    job_type,
    ROUND(AVG(CAST(screen_time_before_sleep AS FLOAT)), 2) AS avg_pre_sleep_screen_time,
    ROUND(AVG(CAST(breaks_during_work AS FLOAT)), 2) AS avg_work_breaks,
    ROUND(AVG(CAST(actual_productivity_score AS FLOAT)), 2) AS avg_productivity
FROM social_media_vs_productivity
WHERE has_digital_wellbeing_enabled = 1 OR has_digital_wellbeing_enabled = 'True'
GROUP BY job_type
ORDER BY avg_productivity DESC, avg_work_breaks DESC, avg_pre_sleep_screen_time ASC;
GO


/* =====================================================================
   DASHBOARD 05 - Workforce Segmentation & Insights
   ===================================================================== */

-- D5-Q1 | EASY | How is the workforce distributed across job types and genders?
-- Finding: IT is 68.7% male, Health 65.0% female, Education 62.5% female.
SELECT
    job_type,
    gender,
    COUNT(*) AS total_users,
    ROUND((COUNT(*) * 100.0) / SUM(COUNT(*)) OVER(PARTITION BY job_type), 2) AS pct_within_job_type
FROM social_media_vs_productivity
GROUP BY job_type, gender
ORDER BY job_type, total_users DESC;
GO

-- D5-Q2 | EASY | How do weekly offline hours differ across age groups?
-- Finding: Almost flat: 15.16 (under 25) to 15.77 (above 55).
SELECT
    age_group,
    COUNT(*) AS total_users,
    ROUND(AVG(CAST(weekly_offline_hours AS FLOAT)), 2) AS avg_weekly_offline_hours
FROM (
    SELECT
        weekly_offline_hours,
        CASE
            WHEN age < 25 THEN 'Under 25'
            WHEN age BETWEEN 25 AND 40 THEN '25-40'
            WHEN age BETWEEN 41 AND 55 THEN '41-55'
            ELSE 'Above 55'
        END AS age_group
    FROM social_media_vs_productivity
) AS t
GROUP BY age_group
ORDER BY avg_weekly_offline_hours DESC;
GO

-- D5-Q3 | MEDIUM | How do job types differ in job satisfaction and stress level?
-- Finding: Health lowest satisfaction (7.56) and highest stress (3.92); Unemployed the opposite (8.00 and 2.56).
SELECT
    job_type,
    COUNT(*) AS total_users,
    ROUND(AVG(CAST(job_satisfaction_score AS FLOAT)), 2) AS avg_job_satisfaction,
    ROUND(AVG(CAST(stress_level AS FLOAT)), 2) AS avg_stress_level
FROM social_media_vs_productivity
GROUP BY job_type
ORDER BY avg_job_satisfaction DESC;
GO

-- D5-Q4 | MEDIUM | How do men, women and other genders differ in job satisfaction, stress level and sleep?
-- Finding: Gender makes almost no difference: satisfaction 7.69-7.72, stress 3.41-3.44, sleep 7.33-7.37 hrs.
SELECT
    gender,
    COUNT(*) AS total_users,
    ROUND(AVG(CAST(job_satisfaction_score AS FLOAT)), 2) AS avg_job_satisfaction,
    ROUND(AVG(CAST(stress_level AS FLOAT)), 2) AS avg_stress_level,
    ROUND(AVG(CAST(sleep_hours AS FLOAT)), 2) AS avg_sleep_hours
FROM social_media_vs_productivity
GROUP BY gender
ORDER BY avg_job_satisfaction DESC;
GO

-- D5-Q5 | MEDIUM | How does perceived productivity compare with actual productivity across job types?
-- Finding: People over-estimate productivity in every job type: +0.05 (Unemployed) to +0.77 (Student).
SELECT
    job_type,
    ROUND(AVG(CAST(perceived_productivity_score AS FLOAT)), 2) AS avg_perceived_productivity,
    ROUND(AVG(CAST(actual_productivity_score AS FLOAT)), 2) AS avg_actual_productivity,
    ROUND(AVG(CAST(perceived_productivity_score AS FLOAT) - actual_productivity_score), 2) AS perception_gap
FROM social_media_vs_productivity
GROUP BY job_type
ORDER BY perception_gap DESC;
GO

-- D5-Q6 | HARD | Which job type and age-group segments are the largest, and how productive and satisfied are they?
-- Finding: Student under 25 is the largest (4,862 users); Unemployed 25-40 leads the top 10 on productivity (7.23) and satisfaction (8.02).
SELECT TOP 10
    job_type,
    age_group,
    COUNT(*) AS total_users,
    ROUND(AVG(CAST(actual_productivity_score AS FLOAT)), 2) AS avg_productivity,
    ROUND(AVG(CAST(job_satisfaction_score AS FLOAT)), 2) AS avg_job_satisfaction
FROM (
    SELECT
        job_type,
        actual_productivity_score,
        job_satisfaction_score,
        CASE
            WHEN age < 25 THEN 'Under 25'
            WHEN age BETWEEN 25 AND 40 THEN '25-40'
            WHEN age BETWEEN 41 AND 55 THEN '41-55'
            ELSE 'Above 55'
        END AS age_group
    FROM social_media_vs_productivity
) AS t
GROUP BY job_type, age_group
ORDER BY total_users DESC;
GO
