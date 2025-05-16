import json
from collections import deque

# Преобразует deque в JSON-строку.
def serialize_deque(dq: deque) -> str:
    return json.dumps(list(dq))

# Преобразует JSON-строку обратно в deque с необязательным maxlen.
def deserialize_deque(s: str, maxlen: int = 10) -> deque:
    try:
        return deque(json.loads(s), maxlen=maxlen)
    except (json.JSONDecodeError, TypeError) as e:
        print(f"Ошибка при десериализации deque: {e}")
        return deque(maxlen=maxlen)



def profile(profile):
    profile_text = f"""
<b>{profile.user_name}, {profile.user_age}, {profile.user_city},{profile.user_course} курс, {profile.user_direction}</b>

 {profile.text}    
"""
    return profile_text