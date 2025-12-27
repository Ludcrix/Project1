# analysis/creator_profile.py

CREATOR_PROFILES = {
    "gmk": "LIFESTYLE / LUXE / REACTION",
    "anyme": "ENTERTAINMENT / REACTION",
    "yomi": "BUSINESS / MINDSET",
    "oussama": "MINDSET / OPINION",
    "inoxtag": "ADVENTURE / ENTERTAINMENT",
}

def detect_creator_profile(channel_name: str) -> str:
    name = channel_name.lower()
    for key, profile in CREATOR_PROFILES.items():
        if key in name:
            return profile
    return "GENERAL CREATOR"
