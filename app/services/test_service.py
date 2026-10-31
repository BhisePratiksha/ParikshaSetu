import uuid
from datetime import datetime, timedelta
from app.extensions import db

class TestService:
    @staticmethod
    def get_paper_questions(paper_id, sanitize=True):
        """Fetch questions for a paper. If sanitize=True, strip answer keys before sending to browser."""
        paper = db.papers.find_one({'id': paper_id})
        exam_id = paper.get('exam_id') if paper else 'police-bharti'
        
        # 1. Look for questions tied directly to this paper
        questions = db.questions.find({'paper_id': paper_id})
        
        # 2. If paper has few or no questions, backfill with exam questions so test is always playable
        if len(questions) < 5:
            exam_questions = db.questions.find({'exam_id': exam_id})
            # Combine without duplicates
            seen = {q['id'] for q in questions}
            for eq in exam_questions:
                if eq['id'] not in seen:
                    questions.append(eq)
                    seen.add(eq['id'])

        # Fallback if still empty
        if not questions:
            questions = db.questions.find()

        if not sanitize:
            return questions

        # SANITIZE: Never leak answers or explanations to the browser before submission
        sanitized = []
        for q in questions:
            sq = {
                'id': q.get('id'),
                'subject': q.get('subject', 'General'),
                'topic': q.get('topic', 'General'),
                'question_text': q.get('question_text'),
                'question_text_en': q.get('question_text_en', ''),
                'options': q.get('options', []),
                'options_en': q.get('options_en', []),
                'marks': q.get('marks', 1.0),
                'negative_marks': q.get('negative_marks', 0.0)
            }
            sanitized.append(sq)

        return sanitized

    @staticmethod
    def start_attempt(user_id, paper_id, duration_minutes=90):
        """Create a new timed test session"""
        paper = db.papers.find_one({'id': paper_id})
        attempt_id = str(uuid.uuid4())
        now = datetime.utcnow()
        expiry = now + timedelta(minutes=duration_minutes)

        attempt = {
            'id': attempt_id,
            'user_id': user_id or 'guest',
            'paper_id': paper_id,
            'paper_title': paper.get('title', 'Examination Paper') if paper else 'Practice Test',
            'exam_id': paper.get('exam_id') if paper else 'police-bharti',
            'started_at': now.isoformat(),
            'expires_at': expiry.isoformat(),
            'duration_minutes': duration_minutes,
            'status': 'in_progress',
            'answers': {}
        }

        db.test_attempts.insert_one(attempt)
        return attempt

    @staticmethod
    def get_attempt(attempt_id):
        return db.test_attempts.find_one({'id': attempt_id})
