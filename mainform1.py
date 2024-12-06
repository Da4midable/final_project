from flask import render_template, session, redirect, url_for

# Map score types to their indices in user_data
SCORE_INDICES = {
    'Programming Score': 10,
    'English Score': 11,
    'History Score': 12,
    'Economics Score': 13,
    'Biology Score': 14
}

def get_latest_score_query():
    return """
    SELECT 
        GREATEST(
            COALESCE(`Programming Score`, '1970-01-01'),
            COALESCE(`English Score`, '1970-01-01'),
            COALESCE(`History Score`, '1970-01-01'),
            COALESCE(`Economics Score`, '1970-01-01'),
            COALESCE(`Biology Score`, '1970-01-01')
        ) AS latest_entry_date,
        CASE 
            WHEN `Programming Score` >= ALL (
                SELECT COALESCE(score, '1970-01-01')
                FROM (VALUES 
                    (`Programming Score`),
                    (`English Score`),
                    (`History Score`),
                    (`Economics Score`),
                    (`Biology Score`)
                ) AS scores(score)
            ) THEN 'Programming Score'
            WHEN `English Score` >= ALL (
                SELECT COALESCE(score, '1970-01-01')
                FROM (VALUES 
                    (`Programming Score`),
                    (`English Score`),
                    (`History Score`),
                    (`Economics Score`),
                    (`Biology Score`)
                ) AS scores(score)
            ) THEN 'English Score'
            WHEN `History Score` >= ALL (
                SELECT COALESCE(score, '1970-01-01')
                FROM (VALUES 
                    (`Programming Score`),
                    (`English Score`),
                    (`History Score`),
                    (`Economics Score`),
                    (`Biology Score`)
                ) AS scores(score)
            ) THEN 'History Score'
            WHEN `Economics Score` >= ALL (
                SELECT COALESCE(score, '1970-01-01')
                FROM (VALUES 
                    (`Programming Score`),
                    (`English Score`),
                    (`History Score`),
                    (`Economics Score`),
                    (`Biology Score`)
                ) AS scores(score)
            ) THEN 'Economics Score'
            ELSE 'Biology Score'
        END AS latest_score
    FROM users
    """

@app.route('/mainform', strict_slashes=False)
def mainform():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_data = session['user']
    
    # Extract user info
    user_info = {
        'full_name': user_data[1],
        'profile_picture': user_data[6],
        'created_on': user_data[7],
        'all_time_score': user_data[15]
    }
    
    # Get the most recent score
    cursor.execute(get_latest_score_query())
    result = cursor.fetchone()
    
    # Get the recent score using the mapping
    recent_score = None
    if result:
        score_type = result[1]
        # Get the index for the score type, defaulting to Biology Score index if not found
        score_index = SCORE_INDICES.get(score_type)
        if score_index is not None:
            recent_score = user_data[score_index]
        else:
            # Fallback to Biology Score only if something went wrong
            recent_score = user_data[SCORE_INDICES['Biology Score']]
    
    return render_template(
        'mainform.html',
        user_full_name=user_info['full_name'],
        user_profile_picture=user_info['profile_picture'],
        created_on=user_info['created_on'],
        all_time_score=user_info['all_time_score'],
        recent_score=recent_score
    )

@app.route('/mainform/<course>/result', methods=['GET'])
def quiz_result(course):
    score = session.get('score', 0)
    tot_questions = session.get('total_questions', 0)
    user = session['user']
    user_id = user[7]  # Assuming User ID is at index 7

    if not course.isalpha():
        raise ValueError("Invalid course name")
    
    course_score_column = f"{course.capitalize()} Score"
    
    # Update the user's scores using UPDATE instead of INSERT
    query = f"""
    UPDATE users 
    SET `{course_score_column}` = %s,
        Total_Score = Total_Score + %s,
        Total_Questions = Total_Questions + %s
    WHERE `User ID` = %s
    """
    
    cursor.execute(query, (score, score, tot_questions, user_id))
    connection.commit()
    
    clear_quiz_session()
    return render_template('quiz_result.html', score=score, total_questions=tot_questions, course=course)