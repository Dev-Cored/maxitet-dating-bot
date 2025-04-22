

def profile(profile):
    profile_text = f"""
<b>{profile['user_profile_name']}, {profile['user_age']}, {profile['user_city']},{profile['user_course']} курс, {profile['user_direction']}</b>

 {profile['profile_text']}    
"""
    return profile_text