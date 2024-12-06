def get_latest_score_query():
    return """
    SELECT 
        GREATEST(
            COALESCE(Programming_Score_Time, '1970-01-01 00:00:00'),
            COALESCE(English_Score_Time, '1970-01-01 00:00:00'),
            COALESCE(History_Score_Time, '1970-01-01 00:00:00'),
            COALESCE(Economics_Score_Time, '1970-01-01 00:00:00'),
            COALESCE(Biology_Score_Time, '1970-01-01 00:00:00')
        ) AS latest_entry_time,
        CASE 
            WHEN Programming_Score_Time >= ALL (
                SELECT COALESCE(score_time, '1970-01-01 00:00:00') 
                FROM (
                    SELECT Programming_Score_Time AS score_time
                    UNION ALL
                    SELECT English_Score_Time
                    UNION ALL
                    SELECT History_Score_Time
                    UNION ALL
                    SELECT Economics_Score_Time
                    UNION ALL
                    SELECT Biology_Score_Time
                ) AS score_times
                WHERE score_time IS NOT NULL
            ) THEN 'Programming Score'
            WHEN English_Score_Time >= ALL (
                SELECT COALESCE(score_time, '1970-01-01 00:00:00') 
                FROM (
                    SELECT Programming_Score_Time AS score_time
                    UNION ALL
                    SELECT English_Score_Time
                    UNION ALL
                    SELECT History_Score_Time
                    UNION ALL
                    SELECT Economics_Score_Time
                    UNION ALL
                    SELECT Biology_Score_Time
                ) AS score_times
                WHERE score_time IS NOT NULL
            ) THEN 'English Score'
            WHEN History_Score_Time >= ALL (
                SELECT COALESCE(score_time, '1970-01-01 00:00:00') 
                FROM (
                    SELECT Programming_Score_Time AS score_time
                    UNION ALL
                    SELECT English_Score_Time
                    UNION ALL
                    SELECT History_Score_Time
                    UNION ALL
                    SELECT Economics_Score_Time
                    UNION ALL
                    SELECT Biology_Score_Time
                ) AS score_times
                WHERE score_time IS NOT NULL
            ) THEN 'History Score'
            WHEN Economics_Score_Time >= ALL (
                SELECT COALESCE(score_time, '1970-01-01 00:00:00') 
                FROM (
                    SELECT Programming_Score_Time AS score_time
                    UNION ALL
                    SELECT English_Score_Time
                    UNION ALL
                    SELECT History_Score_Time
                    UNION ALL
                    SELECT Economics_Score_Time
                    UNION ALL
                    SELECT Biology_Score_Time
                ) AS score_times
                WHERE score_time IS NOT NULL
            ) THEN 'Economics Score'
            ELSE 'Biology Score'
        END AS latest_score
    FROM users
    WHERE `User ID` = %s;
    """

def update_mainform(course_score_column, total_course_score, time_of_course_score):
    return f"""
            UPDATE users 
            SET `{course_score_column}` = %s,
                {total_course_score} = {total_course_score} + %s,
                Total_Score = Total_Score + %s,
                Total_Questions = Total_Questions + %s,
                `{time_of_course_score}` = %s,
                `Last Played On` = %s
            WHERE `USER ID` = %s
            """

def highest_scorer(total_course_score):
    return f"""
            SELECT username, MAX({total_course_score}) as highest_score
            FROM users
            GROUP BY username
            HAVING MAX({total_course_score}) = (
                SELECT MAX({total_course_score})
                FROM users
            );
            """
