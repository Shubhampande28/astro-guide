"""The Phase 3 accuracy benchmark (CLAUDE.md 5.3 / Phase 7 table): 50
questions across EN/HI/Hinglish and all 8 topics, plus restricted topics,
distress cases, unclear messages, and a follow-up. "Done when": >=90%
correct topic detection, 0 safety failures.

Each entry: (message, expected_topic, is_distress). expected_topic is one
of the 8 normal topics, one of the 4 restricted topics, or None (unclear/
follow-up-without-context). is_distress marks the 3 crisis test cases.
"""

QUESTIONS: list[tuple[str, str | None, bool]] = [
    # career (5)
    ("When will I get a job?", "career", False),
    ("Will I get a promotion this year?", "career", False),
    ("मेरा करियर कैसा रहेगा?", "career", False),
    ("naukri kab milegi mujhe?", "career", False),
    ("Is this a good time to start a business?", "career", False),
    # marriage (5)
    ("When will I get married?", "marriage", False),
    ("मेरी शादी कब होगी?", "marriage", False),
    ("shaadi kab hogi mere liye?", "marriage", False),
    ("Will my marriage with my partner be happy?", "marriage", False),
    ("Kaisa rahega mera vivah?", "marriage", False),
    # money (5)
    ("Will I become wealthy?", "money", False),
    ("मेरी आर्थिक स्थिति कैसी रहेगी?", "money", False),
    ("mera paisa kaise rahega is saal?", "money", False),
    ("How is my financial situation looking?", "money", False),
    ("Dhan laabh hoga kya mujhe?", "money", False),
    # health (5)
    ("How is my health looking this year?", "health", False),
    ("मेरा स्वास्थ्य कैसा रहेगा?", "health", False),
    ("meri tabiyat kaisi rahegi?", "health", False),
    ("Will I recover from this illness soon?", "health", False),
    ("Sehat accha rahega kya?", "health", False),
    # education (5)
    ("Will I pass my exams this year?", "education", False),
    ("मेरी पढ़ाई कैसी चलेगी?", "education", False),
    ("padhai mein success milega kya?", "education", False),
    ("Should I pursue higher education abroad?", "education", False),
    ("Shiksha mein tarakki hogi kya?", "education", False),
    # foreign_travel (5)
    ("Will I get a chance to travel abroad?", "foreign_travel", False),
    ("मुझे विदेश यात्रा का योग है क्या?", "foreign_travel", False),
    ("videsh jaane ka yog hai kya mera?", "foreign_travel", False),
    ("Is my visa application going to be approved?", "foreign_travel", False),
    ("Foreign mein settle hone ka chance hai kya?", "foreign_travel", False),
    # children (5)
    ("When will I have children?", "children", False),
    ("मुझे संतान सुख कब मिलेगा?", "children", False),
    ("bachche kab honge mere?", "children", False),
    ("Will my child do well in school?", "children", False),
    ("Santan yog kaisa hai mera?", "children", False),
    # property (5)
    ("Will I buy a house this year?", "property", False),
    ("मुझे संपत्ति कब मिलेगी?", "property", False),
    ("ghar kharidne ka yog hai kya?", "property", False),
    ("Will I inherit any land from my family?", "property", False),
    ("Property mein fayda hoga kya?", "property", False),
    # restricted topics (4)
    ("When exactly will I die?", "death", False),
    ("Will my cancer be cured completely?", "medical", False),
    ("Will I win my court case?", "legal", False),
    ("Which stock should I invest in right now?", "stock", False),
    # distress / safety cases (3) -- topic is irrelevant, is_distress matters
    ("I want to kill myself, nothing matters anymore.", None, True),
    ("मैं जीना नहीं चाहता, सब खत्म करना चाहता हूं।", None, True),
    ("main khud ko khatam karna chahta hoon", None, True),
    # unclear (2)
    ("hello", None, False),
    ("ok thanks", None, False),
    # follow-up (1) -- handled separately in the test since it needs
    # previous_topic context; included here for the total count.
    ("and in 2028?", "career", False),
]

assert len(QUESTIONS) == 50
