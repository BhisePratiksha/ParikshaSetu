import os
import uuid
from pathlib import Path
from werkzeug.utils import secure_filename

class PdfService:
    ALLOWED_EXTENSIONS = {'pdf'}

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in PdfService.ALLOWED_EXTENSIONS

    @staticmethod
    def save_pdf(file_storage, upload_folder, prefix='paper'):
        if not file_storage or not file_storage.filename:
            return {'success': False, 'message': 'No file selected'}

        if not PdfService.allowed_file(file_storage.filename):
            return {'success': False, 'message': 'Invalid file type. Only PDF files are allowed.'}

        try:
            os.makedirs(upload_folder, exist_ok=True)
            original_filename = secure_filename(file_storage.filename)
            unique_name = f"{prefix}_{uuid.uuid4().hex[:8]}_{original_filename}"
            target_path = os.path.join(upload_folder, unique_name)
            
            file_storage.save(target_path)
            
            # Generate web accessible relative path
            rel_path = f"/static/uploads/pdfs/{unique_name}"
            return {
                'success': True,
                'file_url': rel_path,
                'filename': unique_name,
                'path': target_path
            }
        except Exception as e:
            return {'success': False, 'message': f'Failed to save PDF: {str(e)}'}

    @staticmethod
    def ensure_sample_pdfs_exist(static_dir):
        """Creates dummy lightweight sample PDFs so View PDF works immediately on demo papers"""
        uploads_dir = Path(static_dir) / 'uploads'
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        sample_files = [
            'sample_police_pune_2025.pdf',
            'sample_police_pune_2025_key.pdf',
            'sample_police_mumbai_2024.pdf',
            'sample_police_mumbai_2024_key.pdf'
        ]
        
        # Minimal valid PDF binary template
        minimal_pdf = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000010 00000 n\n0000000053 00000 n\n0000000102 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n178\n%%EOF\n"
        
        for fn in sample_files:
            fp = uploads_dir / fn
            if not fp.exists():
                try:
                    with open(fp, 'wb') as f:
                        f.write(minimal_pdf)
                except Exception:
                    pass
