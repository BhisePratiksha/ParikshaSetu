import uuid
from datetime import datetime
from app.extensions import db
from app.services.test_service import TestService

class ScoringService:
    @staticmethod
    def evaluate_test(attempt_id, user_id, submitted_answers, time_taken_seconds=0):
        """
        Evaluate candidate submission on server against verified correct answers.
        Returns full result document with subject breakdown, analysis, and study recommendations.
        """
        attempt = db.test_attempts.find_one({'id': attempt_id})
        paper_id = attempt.get('paper_id') if attempt else None
        paper = db.papers.find_one({'id': paper_id}) if paper_id else None

        # Fetch unsanitized questions with verified correct answers from DB
        raw_questions = TestService.get_paper_questions(paper_id, sanitize=False)
        
        total_questions = len(raw_questions)
        attempted_count = 0
        correct_count = 0
        incorrect_count = 0
        total_score = 0.0
        max_possible_score = 0.0

        subject_stats = {}
        reviewed_questions = []

        for q in raw_questions:
            qid = str(q.get('id'))
            subj = q.get('subject', 'General Knowledge')
            if subj not in subject_stats:
                subject_stats[subj] = {
                    'total': 0,
                    'attempted': 0,
                    'correct': 0,
                    'incorrect': 0,
                    'marks_obtained': 0.0,
                    'max_marks': 0.0
                }

            q_marks = float(q.get('marks', 1.0))
            q_neg = float(q.get('negative_marks', paper.get('negative_marks', 0.0) if paper else 0.0))
            max_possible_score += q_marks
            subject_stats[subj]['total'] += 1
            subject_stats[subj]['max_marks'] += q_marks

            user_choice = submitted_answers.get(qid)
            correct_ans = q.get('correct_answer')
            correct_idx = q.get('correct_index')
            options = q.get('options', [])

            # Determine correctness
            is_attempted = user_choice is not None and user_choice != ""
            is_correct = False
            user_choice_idx = None
            user_choice_text = None

            if is_attempted:
                attempted_count += 1
                subject_stats[subj]['attempted'] += 1
                
                # User choice can be integer index (0, 1, 2, 3) or string option text
                try:
                    user_choice_idx = int(user_choice)
                    if 0 <= user_choice_idx < len(options):
                        user_choice_text = options[user_choice_idx]
                except (ValueError, TypeError):
                    user_choice_text = str(user_choice)
                    if user_choice_text in options:
                        user_choice_idx = options.index(user_choice_text)

                if user_choice_idx is not None and correct_idx is not None:
                    is_correct = (user_choice_idx == correct_idx)
                elif user_choice_text and correct_ans:
                    is_correct = (user_choice_text.strip().lower() == str(correct_ans).strip().lower())

                if is_correct:
                    correct_count += 1
                    total_score += q_marks
                    subject_stats[subj]['correct'] += 1
                    subject_stats[subj]['marks_obtained'] += q_marks
                else:
                    incorrect_count += 1
                    total_score -= q_neg
                    subject_stats[subj]['incorrect'] += 1
                    subject_stats[subj]['marks_obtained'] -= q_neg

            reviewed_questions.append({
                'id': qid,
                'subject': subj,
                'topic': q.get('topic', 'General'),
                'question_text': q.get('question_text'),
                'options': options,
                'user_choice_idx': user_choice_idx,
                'user_choice_text': user_choice_text,
                'correct_index': correct_idx,
                'correct_answer': correct_ans,
                'is_attempted': is_attempted,
                'is_correct': is_correct,
                'explanation': q.get('explanation', 'स्पष्टीकरण उपलब्ध नाही.')
            })

        unattempted_count = total_questions - attempted_count
        total_score = max(0.0, round(total_score, 2))
        percentage = round((total_score / max_possible_score * 100), 2) if max_possible_score > 0 else 0.0

        # Calculate subject percentages
        for s, data in subject_stats.items():
            data['percentage'] = round((data['correct'] / data['total'] * 100), 1) if data['total'] > 0 else 0.0

        # Generate rule-based study suggestions based on actual performance
        study_suggestions = ScoringService._generate_study_suggestions(percentage, subject_stats)

        # Build final result record
        result_id = str(uuid.uuid4())
        mins, secs = divmod(int(time_taken_seconds), 60)
        time_formatted = f"{mins}m {secs}s"

        result_doc = {
            'id': result_id,
            'attempt_id': attempt_id,
            'user_id': user_id or 'guest',
            'paper_id': paper_id,
            'paper_title': paper.get('title', 'CBT Mock Paper') if paper else 'Practice Paper',
            'exam_id': paper.get('exam_id') if paper else 'police-bharti',
            'submitted_at': datetime.utcnow().isoformat(),
            'total_questions': total_questions,
            'attempted': attempted_count,
            'correct': correct_count,
            'incorrect': incorrect_count,
            'unattempted': unattempted_count,
            'score': total_score,
            'max_marks': max_possible_score,
            'percentage': percentage,
            'time_taken_seconds': time_taken_seconds,
            'time_taken_formatted': time_formatted,
            'subject_breakdown': subject_stats,
            'study_suggestions': study_suggestions,
            'questions_review': reviewed_questions
        }

        # Save to database
        db.results.insert_one(result_doc)

        # Mark attempt completed
        if attempt:
            db.test_attempts.update_one({'id': attempt_id}, {
                '$set': {
                    'status': 'completed',
                    'completed_at': datetime.utcnow().isoformat(),
                    'result_id': result_id
                }
            })

        return result_doc

    @staticmethod
    def _generate_study_suggestions(overall_pct, subject_stats):
        suggestions = []
        
        # Identify weak subjects (accuracy < 60%)
        weak_subjects = [s for s, d in subject_stats.items() if d.get('percentage', 0) < 60]
        strong_subjects = [s for s, d in subject_stats.items() if d.get('percentage', 0) >= 80]

        if overall_pct >= 85:
            suggestions.append("उत्कृष्ट कामगिरी! तुमची संकल्पनांची तयारी उत्तम आहे. वेळ व्यवस्थापनावर आणि उच्च काठिण्य पातळीच्या प्रश्नांवर लक्ष केंद्रित ठेवा.")
        elif overall_pct >= 65:
            suggestions.append("चांगली कामगिरी. नियमित सराव आणि मागील वर्षांच्या प्रश्नपत्रिका पुन्हा सोडवल्यास गुणवत्ता यादीत उच्च स्थान मिळू शकेल.")
        else:
            suggestions.append("सखोल अभ्यासाची गरज आहे. विशेषतः पायाभूत नियम, सूत्रे आणि व्याकरण घटकांची पुन्हा उजळणी करा.")

        if weak_subjects:
            weak_names = ", ".join(weak_subjects)
            suggestions.append(f"सुधारणा आवश्यक विषय: [{weak_names}]. या विषयांवर दररोज किमान ४५ मिनिटे विशेष सराव सत्र आयोजित करा.")

        if strong_subjects:
            strong_names = ", ".join(strong_subjects)
            suggestions.append(f"तुमची ताकद: [{strong_names}]. या घटकांमधील गती व अचूकता टिकवून ठेवा.")

        suggestions.append("परीक्षेत 'Elimination Technique' (पर्याय वगळणे पद्धत) वापरा ज्यामुळे संभ्रम कमी होऊन अचूकता वाढते.")
        return suggestions
