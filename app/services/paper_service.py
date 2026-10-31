import re
from app.extensions import db

class PaperService:
    @staticmethod
    def get_papers(exam_id=None, year=None, district=None, exam_type=None, search=None):
        query = {}
        if exam_id and exam_id != 'all':
            query['exam_id'] = exam_id
        if year and year != 'all':
            try:
                query['year'] = int(year)
            except ValueError:
                pass
        if district and district != 'all':
            query['district'] = district
        if exam_type and exam_type != 'all':
            query['exam_type'] = exam_type
        if search:
            query['title'] = {'$regex': search}

        # Sort by year descending, then title
        papers = db.papers.find(query, sort=[('year', -1), ('title', 1)])
        return papers

    @staticmethod
    def get_paper_by_id(paper_id):
        if not paper_id:
            return None
        return db.papers.find_one({'id': str(paper_id)})

    @staticmethod
    def get_distinct_years(exam_id=None):
        query = {'exam_id': exam_id} if exam_id else {}
        years = db.papers.distinct('year', query)
        return sorted([y for y in years if y is not None], reverse=True)

    @staticmethod
    def get_distinct_districts(exam_id=None):
        query = {'exam_id': exam_id} if exam_id else {}
        districts = db.papers.distinct('district', query)
        return sorted([d for d in districts if d])

    @staticmethod
    def get_exam_papers_grouped_by_year(exam_id):
        papers = db.papers.find({'exam_id': exam_id}, sort=[('year', -1)])
        grouped = {}
        for p in papers:
            yr = p.get('year', 'Unknown')
            if yr not in grouped:
                grouped[yr] = []
            grouped[yr].append(p)
        return grouped

    @staticmethod
    def get_exam_by_id(exam_id):
        return db.exams.find_one({'id': exam_id})

    @staticmethod
    def get_all_exams(active_only=True):
        query = {'active': True} if active_only else {}
        return db.exams.find(query)
