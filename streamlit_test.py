from flask import render_template, session, redirect, url_for
from database.queries import get_latest_score_query, get_update_score_query

# Map score types to their indices in user_data
SCORE_INDICES = {
    'Programming Score': 10,
    'English Score': 11,
    'History Score': 12,
    'Economics Score': 13,
    'Biology Score': 14
}

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
    cursor.execute(get_latest_score_query(), (user_data[7],))  # Assuming user_data[7] is the User ID
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
    
    # Update the user's scores
    query = get_update_score_query(course)
    cursor.execute(query, (score, score, tot_questions, user_id))
    connection.commit()
    
    clear_quiz_session()
    return render_template('quiz_result.html', score=score, total_questions=tot_questions, course=course)