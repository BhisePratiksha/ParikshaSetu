import json
import logging
from datetime import datetime
from pathlib import Path
import requests
from app.extensions import db

logger = logging.getLogger('parikshasetu.import')

class ApiImportService:
    @staticmethod
    def import_from_local_file(file_path):
        """Import paper metadata from the local sample data/papers.json"""
        path = Path(file_path)
        if not path.exists():
            return {'success': False, 'message': f'Local papers file not found at {file_path}'}
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return ApiImportService._process_import_data(data, source='local_file')
        except Exception as e:
            logger.error(f"Error reading local papers.json: {e}")
            return {'success': False, 'message': f'Failed to parse JSON file: {str(e)}'}

    @staticmethod
    def import_from_external_url(url, timeout=8):
        """Fetch paper metadata from configurable external API URL with validation & error handling"""
        if not url or not url.startswith(('http://', 'https://')):
            return {'success': False, 'message': 'Invalid URL format. Must start with http:// or https://'}

        log_entry = {
            'url': url,
            'source': 'external_api',
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'started'
        }

        try:
            headers = {'User-Agent': 'ParikshaSetu-PaperImporter/1.0'}
            response = requests.get(url, headers=headers, timeout=timeout)
            
            if response.status_code != 200:
                log_entry['status'] = 'failed'
                log_entry['error'] = f'HTTP error {response.status_code}'
                db.api_import_logs.insert_one(log_entry)
                return {'success': False, 'message': f'External API returned status {response.status_code}'}

            try:
                data = response.json()
            except ValueError:
                log_entry['status'] = 'failed'
                log_entry['error'] = 'Invalid JSON response from server'
                db.api_import_logs.insert_one(log_entry)
                return {'success': False, 'message': 'External API response was not valid JSON'}

            result = ApiImportService._process_import_data(data, source=url)
            log_entry['status'] = 'success' if result['success'] else 'failed'
            log_entry['imported_count'] = result.get('imported', 0)
            log_entry['updated_count'] = result.get('updated', 0)
            db.api_import_logs.insert_one(log_entry)
            return result

        except requests.Timeout:
            log_entry['status'] = 'timeout'
            log_entry['error'] = f'Request timed out after {timeout} seconds'
            db.api_import_logs.insert_one(log_entry)
            return {'success': False, 'message': f'Request timed out after {timeout}s'}
        except requests.RequestException as e:
            log_entry['status'] = 'failed'
            log_entry['error'] = str(e)
            db.api_import_logs.insert_one(log_entry)
            return {'success': False, 'message': f'Network request error: {str(e)}'}

    @staticmethod
    def _process_import_data(data, source):
        """Validate format and upsert papers into MongoDB"""
        if not isinstance(data, dict):
            return {'success': False, 'message': 'Top-level JSON payload must be an object'}

        papers = data.get('papers')
        if not isinstance(papers, list):
            return {'success': False, 'message': 'Missing "papers" array in payload'}

        imported = 0
        updated = 0
        errors = []

        for item in papers:
            if not isinstance(item, dict):
                continue
            paper_id = item.get('id')
            exam_id = item.get('exam_id')
            year = item.get('year')
            title = item.get('title')

            # Validate mandatory fields
            if not paper_id or not exam_id or not year or not title:
                errors.append(f"Skipping record with missing required fields: {item}")
                continue

            # Standardize record
            doc = {
                'id': str(paper_id).strip(),
                'exam_id': str(exam_id).strip(),
                'year': int(year),
                'district': item.get('district', 'Maharashtra'),
                'exam_type': item.get('exam_type', 'General'),
                'title': str(title).strip(),
                'pdf_url': item.get('pdf_url') or None,
                'answer_key_url': item.get('answer_key_url') or None,
                'total_questions': int(item.get('total_questions', 100)),
                'duration_minutes': int(item.get('duration_minutes', 90)),
                'total_marks': float(item.get('total_marks', 100.0)),
                'negative_marks': float(item.get('negative_marks', 0.0)),
                'shift': item.get('shift', 'General Shift'),
                'source': source,
                'last_imported_at': datetime.utcnow().isoformat()
            }

            existing = db.papers.find_one({'id': doc['id']})
            if existing:
                db.papers.update_one({'id': doc['id']}, {'$set': doc})
                updated += 1
            else:
                db.papers.insert_one(doc)
                imported += 1

        return {
            'success': True,
            'message': f'Imported {imported} new papers, updated {updated} existing papers.',
            'imported': imported,
            'updated': updated,
            'total_processed': len(papers),
            'errors': errors
        }
