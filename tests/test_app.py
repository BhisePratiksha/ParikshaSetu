import unittest
import json
from app import create_app
from app.config import Config
from app.extensions import db
from app.services.api_import_service import ApiImportService
from app.services.scoring_service import ScoringService

class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key-12345'

class ParikshaSetuTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_home_page_loads(self):
        """Test home page returns 200 and brand name"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'ParikshaSetu', response.data)
        self.assertIn('पोलीस भरती'.encode('utf-8'), response.data)

    def test_police_bharti_page(self):
        """Test First Main Tab contains all 5 mandatory subjects"""
        response = self.client.get('/police-bharti')
        self.assertEqual(response.status_code, 200)
        self.assertIn('मराठी व्याकरण'.encode('utf-8'), response.data)
        self.assertIn('सामान्य ज्ञान'.encode('utf-8'), response.data)
        self.assertIn('चालू घडामोडी'.encode('utf-8'), response.data)
        self.assertIn('बुद्धिमत्ता चाचणी'.encode('utf-8'), response.data)
        self.assertIn('अंकगणित'.encode('utf-8'), response.data)

    def test_government_exams_page(self):
        """Test Second Main Tab lists exams"""
        response = self.client.get('/government-exams')
        self.assertEqual(response.status_code, 200)
        self.assertIn('MPSC'.encode('utf-8'), response.data)
        self.assertIn('तलाठी'.encode('utf-8'), response.data)

    def test_papers_list_page(self):
        """Test Previous-Year Papers listing and filters"""
        response = self.client.get('/papers')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Pune Gramin', response.data)

    def test_paper_detail_page(self):
        """Test Paper Details page displays metadata and 4 actions"""
        response = self.client.get('/papers/pb-2025-pune')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Solve Online', response.data)
        self.assertIn(b'View PDF', response.data)
        self.assertIn(b'Download', response.data)

    def test_pdf_viewer_page(self):
        """Test in-browser PDF viewer loads with valid status"""
        response = self.client.get('/papers/pb-2025-pune/pdf')
        self.assertEqual(response.status_code, 200)

    def test_solve_paper_cbt_session(self):
        """Test starting an interactive CBT examination session"""
        response = self.client.get('/tests/solve/pb-2025-pune')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'cbt-timer-display', response.data)
        self.assertIn(b'question-palette-container', response.data)

    def test_server_scoring_service(self):
        """Test server-side test scoring with exact marks calculation"""
        # q101 correct is 2 (भावे प्रयोग), q102 correct is 1 (अव्ययीभाव समास)
        submitted = {
            'q101': 2, # Correct (+1.0)
            'q102': 0, # Incorrect (0 or negative)
            # q103 unattempted
        }
        res = ScoringService.evaluate_test(
            attempt_id='test-attempt-1',
            user_id='test-user-1',
            submitted_answers=submitted,
            time_taken_seconds=120
        )
        self.assertEqual(res['attempted'], 2)
        self.assertEqual(res['correct'], 1)
        self.assertEqual(res['incorrect'], 1)
        self.assertGreaterEqual(res['score'], 1.0)
        self.assertIn('मराठी व्याकरण', res['subject_breakdown'])

    def test_rest_api_status(self):
        """Test GET /api/status endpoint"""
        response = self.client.get('/api/status')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertGreater(data['total_papers'], 0)

    def test_rest_api_papers(self):
        """Test GET /api/papers endpoint"""
        response = self.client.get('/api/papers?exam_id=police-bharti&year=2025')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertGreaterEqual(len(data['papers']), 1)

    def test_local_json_import(self):
        """Test Mock API service importing from data/papers.json"""
        local_path = self.app.config['LOCAL_PAPERS_PATH']
        result = ApiImportService.import_from_local_file(local_path)
        self.assertTrue(result['success'])
        self.assertGreaterEqual(result['total_processed'], 2)

    def test_pua_text_normalization(self):
        """Test Devanagari PUA ligature decoding to standard Marathi text"""
        from app.services.pdf_extractor_service import PdfExtractorService
        sample = '\ue0a0. 1. खाल\ue196ल पया\ue016यांमधून संयु\ue044त \ue061यंजनांनी'
        normalized = PdfExtractorService.normalize_text(sample)
        self.assertIn('प्र.', normalized)
        self.assertIn('खालील', normalized)
        self.assertIn('संयुक्त', normalized)

    def test_pdf_question_extraction_and_answer_matching(self):
        """Test complete automatic PDF question extraction and answer key matching"""
        import os
        from app.services.pdf_extractor_service import PdfExtractorService
        pdf_path = os.path.join(self.app.root_path, 'static', 'uploads', 'pdfs', 'police-bharti_2025_59670129_Yavatmal_Police_Bharti_Question_Paper_2026_-_Question_Paper_-_MahaSarav.pdf')
        if not os.path.exists(pdf_path):
            self.skipTest("Sample PDF not found")

        res = PdfExtractorService.extract_and_process_pdf(
            pdf_path=pdf_path,
            paper_id='pb-2025-yavatmal',
            exam_id='police-bharti',
            year=2025,
            replace_existing=True
        )
        self.assertTrue(res['success'])
        self.assertEqual(res['total_questions'], 100)
        self.assertEqual(res['answer_keys_found'], 100)
        self.assertEqual(res['document_type'], 'combined')

        # Verify Q1 details
        q1 = db.questions.find_one({'paper_id': 'pb-2025-yavatmal', 'question_number': 1})
        self.assertIsNotNone(q1)
        self.assertEqual(q1['correct_index'], 1) # Option B
        self.assertEqual(q1['answer_source'], 'Official Answer Key')
        self.assertEqual(q1['subject_id'], 'pb-marathi')
        self.assertIn('स्पष्टीकरण', q1['explanation'])

        # Verify duplicate detection
        dup_res = PdfExtractorService.extract_and_process_pdf(
            pdf_path=pdf_path,
            paper_id='pb-2025-yavatmal',
            exam_id='police-bharti',
            year=2025,
            replace_existing=False
        )
        self.assertTrue(dup_res.get('already_imported', False))

    def test_paper_solutions_page(self):
        """Test candidate-facing Paper Solutions & Explanations view"""
        response = self.client.get('/papers/pb-2025-yavatmal/solutions')
        self.assertEqual(response.status_code, 200)
        self.assertIn('स्पष्टीकरणे'.encode('utf-8'), response.data)

    def test_category_exam_questions_page(self):
        """Test category-wise Question Bank browser page"""
        response = self.client.get('/exams/police-bharti/questions')
        self.assertEqual(response.status_code, 200)
        self.assertIn('प्रश्नसंच'.encode('utf-8'), response.data)

if __name__ == '__main__':
    unittest.main()
