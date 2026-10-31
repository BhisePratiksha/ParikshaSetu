import json
import logging
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from werkzeug.security import generate_password_hash

logger = logging.getLogger('parikshasetu')

class MongoCompatibleCollection:
    def __init__(self, name, store):
        self.name = name
        self.store = store

    def _matches(self, doc, query):
        if not query:
            return True
        for key, val in query.items():
            if key == '$or':
                if not any(self._matches(doc, q) for q in val):
                    return False
                continue
            doc_val = doc.get(key)
            if isinstance(val, dict):
                for op, op_val in val.items():
                    if op == '$in':
                        if doc_val not in op_val:
                            return False
                    elif op == '$regex':
                        if doc_val is None or not re.search(str(op_val), str(doc_val), re.IGNORECASE):
                            return False
                    elif op == '$ne':
                        if doc_val == op_val:
                            return False
                    elif op == '$gte':
                        if doc_val is None or doc_val < op_val:
                            return False
                    elif op == '$lte':
                        if doc_val is None or doc_val > op_val:
                            return False
            else:
                if doc_val != val:
                    return False
        return True

    def find(self, query=None, projection=None, sort=None):
        query = query or {}
        docs = [d for d in self.store.data.get(self.name, []) if self._matches(d, query)]
        if sort:
            # sort is list of (field, direction)
            for field, direction in reversed(sort):
                docs.sort(key=lambda x: x.get(field, ''), reverse=(direction < 0))
        # deep copy
        return [dict(d) for d in docs]

    def find_one(self, query=None):
        query = query or {}
        for d in self.store.data.get(self.name, []):
            if self._matches(d, query):
                return dict(d)
        return None

    def insert_one(self, doc):
        doc = dict(doc)
        if '_id' not in doc:
            doc['_id'] = str(uuid.uuid4())
        if 'created_at' not in doc:
            doc['created_at'] = datetime.utcnow().isoformat()
        if self.name not in self.store.data:
            self.store.data[self.name] = []
        self.store.data[self.name].append(doc)
        self.store.save()
        class InsertResult:
            def __init__(self, inserted_id):
                self.inserted_id = inserted_id
        return InsertResult(doc['_id'])

    def insert_many(self, docs):
        res_ids = []
        for d in docs:
            r = self.insert_one(d)
            res_ids.append(r.inserted_id)
        return res_ids

    def update_one(self, query, update, upsert=False):
        query = query or {}
        for d in self.store.data.get(self.name, []):
            if self._matches(d, query):
                if '$set' in update:
                    d.update(update['$set'])
                d['updated_at'] = datetime.utcnow().isoformat()
                self.store.save()
                return True
        if upsert:
            new_doc = dict(query)
            if '$set' in update:
                new_doc.update(update['$set'])
            self.insert_one(new_doc)
            return True
        return False

    def delete_one(self, query):
        query = query or {}
        coll = self.store.data.get(self.name, [])
        for i, d in enumerate(coll):
            if self._matches(d, query):
                del coll[i]
                self.store.save()
                return True
        return False

    def count_documents(self, query=None):
        return len(self.find(query))

    def distinct(self, key, query=None):
        docs = self.find(query)
        vals = set()
        for d in docs:
            if key in d and d[key] is not None:
                vals.add(d[key])
        return sorted(list(vals))

class MongoCompatibleDatabase:
    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.data = {}
        self.load()

    def load(self):
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load data store: {e}")
                self.data = {}
        else:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self.data = {}

    def save(self):
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving data store: {e}")

    def __getitem__(self, name):
        return MongoCompatibleCollection(name, self)

    def __getattr__(self, name):
        return MongoCompatibleCollection(name, self)

class DbProxy:
    def __init__(self):
        self._target = None

    def set_target(self, target):
        self._target = target

    def __getitem__(self, name):
        if self._target is None:
            # Auto fallback
            store_path = Path(__file__).resolve().parent.parent / 'data' / 'db_store.json'
            self._target = MongoCompatibleDatabase(store_path)
        return self._target[name]

    def __getattr__(self, name):
        if self._target is None:
            store_path = Path(__file__).resolve().parent.parent / 'data' / 'db_store.json'
            self._target = MongoCompatibleDatabase(store_path)
        return getattr(self._target, name)

    def __bool__(self):
        return True

# Global DB proxy
db = DbProxy()
is_mongo_live = False

class PyMongoCollectionWrapper:
    def __init__(self, coll):
        self._coll = coll

    @staticmethod
    def _clean_doc(doc):
        if not doc:
            return doc
        d = dict(doc)
        if '_id' in d:
            d['_id'] = str(d['_id'])
        return d

    def find(self, filter=None, projection=None, sort=None, **kwargs):
        filter = filter or {}
        cursor = self._coll.find(filter, projection, **kwargs)
        if sort:
            cursor = cursor.sort(sort)
        return [self._clean_doc(d) for d in cursor]

    def find_one(self, filter=None, *args, **kwargs):
        filter = filter or {}
        doc = self._coll.find_one(filter, *args, **kwargs)
        return self._clean_doc(doc)

    def count_documents(self, filter=None, **kwargs):
        filter = filter or {}
        return self._coll.count_documents(filter, **kwargs)

    def distinct(self, key, filter=None, **kwargs):
        filter = filter or {}
        return self._coll.distinct(key, filter, **kwargs)

    def insert_one(self, *args, **kwargs):
        return self._coll.insert_one(*args, **kwargs)

    def insert_many(self, *args, **kwargs):
        return self._coll.insert_many(*args, **kwargs)

    def update_one(self, *args, **kwargs):
        return self._coll.update_one(*args, **kwargs)

    def update_many(self, *args, **kwargs):
        return self._coll.update_many(*args, **kwargs)

    def delete_one(self, *args, **kwargs):
        return self._coll.delete_one(*args, **kwargs)

    def delete_many(self, *args, **kwargs):
        return self._coll.delete_many(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._coll, name)

class PyMongoDatabaseWrapper:
    def __init__(self, raw_db):
        self._db = raw_db

    def __getitem__(self, name):
        return PyMongoCollectionWrapper(self._db[name])

    def __getattr__(self, name):
        return PyMongoCollectionWrapper(getattr(self._db, name))

def init_db(app):
    global is_mongo_live
    mongo_uri = app.config.get('MONGO_URI')
    mongo_db_name = app.config.get('MONGO_DB_NAME')

    # Try connecting to real MongoDB if pymongo is installed
    try:
        import pymongo
        client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=1500)
        client.server_info()  # trigger connection test
        target = PyMongoDatabaseWrapper(client[mongo_db_name])
        db.set_target(target)
        is_mongo_live = True
        logger.info(f"Connected successfully to live MongoDB at {mongo_uri}")
    except Exception as e:
        is_mongo_live = False
        logger.info(f"Using high-performance embedded Mongo-compatible JSON store (MongoDB not reachable: {e})")
        store_path = Path(app.root_path).parent / 'data' / 'db_store.json'
        target = MongoCompatibleDatabase(store_path)
        db.set_target(target)

    # Seed initial data
    seed_database(app)

def seed_database(app):
    """Seed default admin, student, exams, subjects, questions, and papers"""
    global db
    if not db:
        return

    # 1. Seed Admin User
    admin_email = app.config.get('ADMIN_EMAIL', 'admin@parikshasetu.com')
    admin_user = db.users.find_one({'email': admin_email})
    if not admin_user:
        db.users.insert_one({
            'name': app.config.get('ADMIN_NAME', 'System Administrator'),
            'email': admin_email,
            'password_hash': generate_password_hash(app.config.get('ADMIN_PASSWORD', 'Admin@123')),
            'role': 'admin',
            'is_active': True,
            'created_at': datetime.utcnow().isoformat()
        })
        logger.info(f"Seeded Admin user: {admin_email}")

    # Seed Demo Student User
    student_email = 'student@parikshasetu.com'
    if not db.users.find_one({'email': student_email}):
        db.users.insert_one({
            'name': 'Rahul Patil (Demo Candidate)',
            'email': student_email,
            'password_hash': generate_password_hash('Student@123'),
            'role': 'student',
            'target_exam': 'police-bharti',
            'is_active': True,
            'created_at': datetime.utcnow().isoformat()
        })
        logger.info(f"Seeded Demo Student user: {student_email}")

    # 2. Seed Exams
    exams_data = [
        {
            'id': 'police-bharti',
            'name': 'Maharashtra Police Bharti',
            'name_mr': 'महाराष्ट्र पोलीस भरती',
            'category': 'Police & Security',
            'badge': 'State Police',
            'description': 'Recruitment for Maharashtra Police Constable, Driver Constable, SRPF, and Bandsman.',
            'description_mr': 'महाराष्ट्र पोलीस शिपाई, चालक, एसआरपीएफ व बॅण्डस्मन पदांसाठीची अधिकृत भरती परीक्षा.',
            'duration_minutes': 90,
            'total_questions': 100,
            'total_marks': 100,
            'negative_marks': 0.0,
            'active': True
        },
        {
            'id': 'mpsc',
            'name': 'MPSC Group B & C Combine',
            'name_mr': 'MPSC गट ब व गट क संयुक्त परीक्षा',
            'category': 'State Public Service',
            'badge': 'Gazetted & Non-Gazetted',
            'description': 'State recruitment for PSI, STI, ASO, Tax Assistant, and Sub-Registrar.',
            'description_mr': 'पोलीस उपनिरीक्षक (PSI), राज्य कर निरीक्षक (STI) व सहायक कक्ष अधिकारी (ASO) स्पर्धा परीक्षा.',
            'duration_minutes': 60,
            'total_questions': 100,
            'total_marks': 100,
            'negative_marks': 0.25,
            'active': True
        },
        {
            'id': 'talathi-bharti',
            'name': 'Maharashtra Talathi Bharti',
            'name_mr': 'महाराष्ट्र तलाठी भरती',
            'category': 'Revenue Department',
            'badge': 'TCS Pattern',
            'description': 'Revenue department examination for village revenue officers (Talathi) across Maharashtra districts.',
            'description_mr': 'महसूल व वन विभागांतर्गत तलाठी पदांसाठी टीसीएस (TCS) पॅटर्ननुसार घेण्यात येणारी परीक्षा.',
            'duration_minutes': 120,
            'total_questions': 100,
            'total_marks': 200,
            'negative_marks': 0.0,
            'active': True
        },
        {
            'id': 'zp-bharti',
            'name': 'Zilla Parishad (ZP) Bharti',
            'name_mr': 'जिल्हा परिषद भरती',
            'category': 'Rural Development',
            'badge': 'IBPS Pattern',
            'description': 'Recruitment for Gramsevak, Arogya Sevak, Health Worker, and Junior Clerks.',
            'description_mr': 'ग्रामसेवक, आरोग्य सेवक/सेविका व कनिष्ठ प्रशासन सहायक भरती परीक्षा.',
            'duration_minutes': 120,
            'total_questions': 100,
            'total_marks': 200,
            'negative_marks': 0.0,
            'active': True
        },
        {
            'id': 'ssc',
            'name': 'SSC (GD / CGL / CHSL)',
            'name_mr': 'कर्मचारी निवड आयोग (SSC)',
            'category': 'Central Government',
            'badge': 'Central Staff',
            'description': 'Central staff selection commission examinations for defense and central ministries.',
            'description_mr': 'केंद्रीय मंत्रालये व सशस्त्र दलांमधील विविध पदांसाठी राष्ट्रीय स्तरावरील परीक्षा.',
            'duration_minutes': 60,
            'total_questions': 80,
            'total_marks': 160,
            'negative_marks': 0.5,
            'active': True
        },
        {
            'id': 'railway',
            'name': 'Railway Recruitment Board (RRB)',
            'name_mr': 'रेल्वे भरती बोर्ड (RRB ALP / NTPC)',
            'category': 'Central Railway',
            'badge': 'Indian Railways',
            'description': 'Indian Railways recruitment for NTPC, Assistant Loco Pilot (ALP), and Group D positions.',
            'description_mr': 'भारतीय रेल्वे अंतर्गत एनटीपीसी, लोको पायलट व ग्रुप-डी पदांसाठी भरती.',
            'duration_minutes': 90,
            'total_questions': 100,
            'total_marks': 100,
            'negative_marks': 0.33,
            'active': True
        },
        {
            'id': 'banking',
            'name': 'Banking Exams (IBPS / SBI / RBI)',
            'name_mr': 'बँकिंग परीक्षा (IBPS / SBI / RBI)',
            'category': 'Financial Sector',
            'badge': 'Banking',
            'description': 'Probationary Officers (PO) and Clerical cadre recruitment across public sector banks.',
            'description_mr': 'सार्वजनिक क्षेत्रातील बँकांमधील प्रोबेशनरी ऑफिसर (PO) व लिपिक संवर्ग भरती.',
            'duration_minutes': 60,
            'total_questions': 100,
            'total_marks': 100,
            'negative_marks': 0.25,
            'active': True
        }
    ]

    for ex in exams_data:
        db.exams.update_one({'id': ex['id']}, {'$set': ex}, upsert=True)

    # 3. Seed Subjects & Topics for Police Bharti (specifically requested)
    police_subjects = [
        {
            'id': 'pb-marathi',
            'exam_id': 'police-bharti',
            'name': 'Marathi Grammar',
            'name_mr': 'मराठी व्याकरण',
            'description': 'वर्णविचार, नाम, सर्वनाम, विशेषण, क्रियापद, काळ, प्रयोग, समास, समानार्थी व विरुद्धार्थी शब्द.',
            'icon': 'bi-book-fill',
            'color': '#6366F1',
            'weightage_percent': 25,
            'topics': [
                'वर्णमाला व उच्चारस्थाने',
                'शब्दांच्या जाती (नाम, सर्वनाम, विशेषण, क्रियापद)',
                'विभक्ती व विभक्ती प्रत्यय',
                'प्रयोग (कर्तरी, कर्मणी, भावे)',
                'समास (अव्ययीभाव, तत्पुरुष, द्वंद्व, बहुव्रीही)',
                'समानार्थी, विरुद्धार्थी व म्हणी'
            ]
        },
        {
            'id': 'pb-gk',
            'exam_id': 'police-bharti',
            'name': 'General Knowledge',
            'name_mr': 'सामान्य ज्ञान व महाराष्ट्र इतिहास-भूगोल',
            'description': 'महाराष्ट्राचा इतिहास, भूगोल, राज्यघटना, पंचायत राज, विज्ञान आणि पोलीस प्रशासन.',
            'icon': 'bi-globe-americas',
            'color': '#EC4899',
            'weightage_percent': 25,
            'topics': [
                'महाराष्ट्राचा इतिहास व समाजसुधारक',
                'महाराष्ट्राचा भूगोल (नद्या, पर्वत, जिल्हे)',
                'भारतीय राज्यघटना व मूलभूत हक्क',
                'पोलीस प्रशासन व गुप्तवार्ता विभाग (SID/CID)',
                'सामान्य विज्ञान (भौतिक, रसायन, जीवशास्त्र)'
            ]
        },
        {
            'id': 'pb-current',
            'exam_id': 'police-bharti',
            'name': 'Current Affairs',
            'name_mr': 'चालू घडामोडी',
            'description': 'राष्ट्रीय व आंतरराष्ट्रीय महत्त्वाच्या घडामोडी, क्रीडा पुरस्कार, योजना आणि नियुक्त्या.',
            'icon': 'bi-newspaper',
            'color': '#F59E0B',
            'weightage_percent': 15,
            'topics': [
                'महाराष्ट्र राज्य शासनाच्या नवीन योजना',
                'प्रमुख क्रीडा स्पर्धा व पदके (ऑलिम्पिक, क्रिकेट)',
                'महत्त्वाचे राष्ट्रीय व आंतरराष्ट्रीय पुरस्कार',
                'नवीन नियुक्त्या व पदाधिकारी'
            ]
        },
        {
            'id': 'pb-reasoning',
            'exam_id': 'police-bharti',
            'name': 'Reasoning / Intelligence Test',
            'name_mr': 'बुद्धिमत्ता चाचणी',
            'description': 'संख्या मालिका, अक्षर मालिका, नातेसंबंध, दिशाज्ञान, घड्याळ व दिनदर्शिका.',
            'icon': 'bi-cpu-fill',
            'color': '#10B981',
            'weightage_percent': 15,
            'topics': [
                'संख्या व अक्षर मालिका (Series Completion)',
                'नातेसंबंध व सांकेतिक भाषा (Coding-Decoding)',
                'दिशाज्ञान चाचणी व बैठक व्यवस्था',
                'घड्याळ व दिनदर्शिका (Calendar & Clock)',
                'वेन आकृत्या व तार्किक निष्कर्ष'
            ]
        },
        {
            'id': 'pb-math',
            'exam_id': 'police-bharti',
            'name': 'Arithmetic / Mathematics',
            'name_mr': 'अंकगणित',
            'description': 'संख्याज्ञान, लसावि-मसावि, सरासरी, शेकडेवारी, नफा-तोटा, काळ-काम-वेग आणि सरळव्याज.',
            'icon': 'bi-calculator-fill',
            'color': '#FF6B00',
            'weightage_percent': 20,
            'topics': [
                'संख्यांचे प्रकार, ल.सा.वि. व म.सा.वि.',
                'शेकडेवारी व सरासरी',
                'नफा आणि तोटा',
                'काळ, काम आणि वेग (रेल्वे व अंतर)',
                'सरळव्याज व चक्रवाढ व्याज'
            ]
        }
    ]

    for sub in police_subjects:
        db.subjects.update_one({'id': sub['id']}, {'$set': sub}, upsert=True)

    # 4. Seed Questions for practice & CBT tests
    questions_data = [
        {
            'id': 'q101',
            'exam_id': 'police-bharti',
            'subject_id': 'pb-marathi',
            'subject': 'मराठी व्याकरण',
            'topic': 'प्रयोग (Prayog)',
            'question_text': '‘रामाने रावणास मारले’ - या वाक्यातील प्रयोग ओळखा.',
            'question_text_en': 'Identify the "Prayog" in the sentence: "Ramane Ravanas Marale".',
            'options': ['कर्तरी प्रयोग', 'कर्मणी प्रयोग', 'भावे प्रयोग', 'मिश्र / संकर प्रयोग'],
            'options_en': ['Kartari Prayog', 'Karmani Prayog', 'Bhave Prayog', 'Mishra Prayog'],
            'correct_answer': 'भावे प्रयोग',
            'correct_index': 2,
            'explanation': 'जेव्हा कर्त्याला व कर्माला दोघांनाही विभक्ती प्रत्यय असतो आणि क्रियापद तृतीयपुरुषी, नपुंसकलिंगी एकवचनी असते, तेव्हा "सकर्मक भावे प्रयोग" होतो.',
            'marks': 1.0,
            'negative_marks': 0.0,
            'paper_id': 'pb-2025-pune'
        },
        {
            'id': 'q102',
            'exam_id': 'police-bharti',
            'subject_id': 'pb-marathi',
            'subject': 'मराठी व्याकरण',
            'topic': 'समास (Samas)',
            'question_text': 'खालीलपैकी ‘यथाशक्ती’ या शब्दाचा समास कोणता आहे?',
            'question_text_en': 'Which type of Samas is the compound word "Yathashakti"?',
            'options': ['तत्पुरुष समास', 'अव्ययीभाव समास', 'द्वंद्व समास', 'बहुव्रीही समास'],
            'options_en': ['Tatpurusha Samas', 'Avyayibhava Samas', 'Dvandva Samas', 'Bahuvrihi Samas'],
            'correct_answer': 'अव्ययीभाव समास',
            'correct_index': 1,
            'explanation': '‘यथाशक्ती’ म्हणजे शक्तीप्रमाणे. यात पहिले पद अव्यय (यथा) असून संपूर्ण शब्द क्रियाविशेषणाचे काम करतो, म्हणून हा अव्ययीभाव समास आहे.',
            'marks': 1.0,
            'negative_marks': 0.0,
            'paper_id': 'pb-2025-pune'
        },
        {
            'id': 'q103',
            'exam_id': 'police-bharti',
            'subject_id': 'pb-gk',
            'subject': 'सामान्य ज्ञान व पोलीस प्रशासन',
            'topic': 'पोलीस प्रशासन',
            'question_text': 'महाराष्ट्र राज्याच्या गुप्तवार्ता विभागाचे (State Intelligence Department - SID) मुख्यालय कुठे आहे?',
            'question_text_en': 'Where is the headquarters of the State Intelligence Department (SID) located?',
            'options': ['पुणे (Pune)', 'मुंबई (Mumbai)', 'नागपूर (Nagpur)', 'नाशिक (Nashik)'],
            'options_en': ['Pune', 'Mumbai', 'Nagpur', 'Nashik'],
            'correct_answer': 'मुंबई (Mumbai)',
            'correct_index': 1,
            'explanation': 'महाराष्ट्र राज्य गुप्तवार्ता विभाग (SID) चे मुख्य कार्यालय मुंबई येथे आहे. गुन्हे अन्वेषण विभाग (CID) चे मुख्यालय पुणे येथे आहे.',
            'marks': 1.0,
            'negative_marks': 0.0,
            'paper_id': 'pb-2025-pune'
        },
        {
            'id': 'q104',
            'exam_id': 'police-bharti',
            'subject_id': 'pb-gk',
            'subject': 'सामान्य ज्ञान',
            'topic': 'भारतीय राज्यघटना',
            'question_text': 'भारतीय राज्यघटनेत मूलभूत कर्तव्यांचा समावेश कोणत्या घटनादुरुस्ती कायद्याद्वारे करण्यात आला?',
            'question_text_en': 'Under which Constitutional Amendment were Fundamental Duties added to the Indian Constitution?',
            'options': ['४२ वी घटनादुरुस्ती १९७६', '४४ वी घटनादुरुस्ती १९७८', '५२ वी घटनादुरुस्ती १९८५', '८६ वी घटनादुरुस्ती २००२'],
            'options_en': ['42nd Amendment 1976', '44th Amendment 1978', '52nd Amendment 1985', '86th Amendment 2002'],
            'correct_answer': '४२ वी घटनादुरुस्ती १९७६',
            'correct_index': 0,
            'explanation': '१९७६ च्या ४२ व्या घटनादुरुस्तीने स्वर्णसिंह समितीच्या शिफारशीनुसार राज्यघटनेत भाग IV-A आणि कलम ५१-A चा समावेश करून मूलभूत कर्तव्ये जोडली.',
            'marks': 1.0,
            'negative_marks': 0.0,
            'paper_id': 'pb-2025-pune'
        },
        {
            'id': 'q105',
            'exam_id': 'police-bharti',
            'subject_id': 'pb-math',
            'subject': 'अंकगणित',
            'topic': 'काळ, काम आणि वेग',
            'question_text': 'ताशी ६० किमी वेगाने धावणारी १८० मीटर लांबीची आगगाडी एका खांबाला किती सेकंदात ओलांडेल?',
            'question_text_en': 'In how many seconds will a 180m long train running at 60 km/h cross an electric pole?',
            'options': ['१०.२ सेकंद', '१०.८ सेकंद', '११.५ सेकंद', '१२ सेकंद'],
            'options_en': ['10.2 Seconds', '10.8 Seconds', '11.5 Seconds', '12 Seconds'],
            'correct_answer': '१०.८ सेकंद',
            'correct_index': 1,
            'explanation': 'वेग = ६० × (५/१८) = ५०/३ मीटर/सेकंद. वेळ = अंतर / वेग = १८० / (५०/३) = (१८० × ३) / ५० = ५४० / ५० = १०.८ सेकंद.',
            'marks': 1.0,
            'negative_marks': 0.0,
            'paper_id': 'pb-2025-pune'
        },
        {
            'id': 'q106',
            'exam_id': 'police-bharti',
            'subject_id': 'pb-reasoning',
            'subject': 'बुद्धिमत्ता चाचणी',
            'topic': 'संख्या मालिका (Series)',
            'question_text': 'खालील संख्या मालिकेतील पुढील पद शोधा: ३, ७, १५, ३१, ६३, ?',
            'question_text_en': 'Find the next number in the series: 3, 7, 15, 31, 63, ?',
            'options': ['१२५', '१२७', '१२९', '१३१'],
            'options_en': ['125', '127', '129', '131'],
            'correct_answer': '१२७',
            'correct_index': 1,
            'explanation': 'पॅटर्न: (मागील संख्या × २) + १. म्हणून: (६३ × २) + १ = १२६ + १ = १२७.',
            'marks': 1.0,
            'negative_marks': 0.0,
            'paper_id': 'pb-2025-pune'
        },
        {
            'id': 'q107',
            'exam_id': 'police-bharti',
            'subject_id': 'pb-current',
            'subject': 'चालू घडामोडी',
            'topic': 'क्रीडा व पुरस्कार',
            'question_text': 'भारतात दरवर्षी ‘राष्ट्रीय क्रीडा दिन’ कोणत्या महान खेळाडूच्या स्मरणार्थ २९ ऑगस्ट रोजी साजरा केला जातो?',
            'question_text_en': 'National Sports Day is celebrated on August 29 in India in memory of which legendary athlete?',
            'options': ['मिल्खा सिंग', 'मेजर ध्यानचंद', 'के. डी. जाधव', 'सचिन तेंडुलकर'],
            'options_en': ['Milkha Singh', 'Major Dhyan Chand', 'K. D. Jadhav', 'Sachin Tendulkar'],
            'correct_answer': 'मेजर ध्यानचंद',
            'correct_index': 1,
            'explanation': 'हॉकीचे जादूगार मेजर ध्यानचंद यांच्या जन्मदिनी (२९ ऑगस्ट) दरवर्षी राष्ट्रीय क्रीडा दिन साजरा करण्यात येतो.',
            'marks': 1.0,
            'negative_marks': 0.0,
            'paper_id': 'pb-2025-pune'
        }
    ]

    for q in questions_data:
        db.questions.update_one({'id': q['id']}, {'$set': q}, upsert=True)

    # 5. Load and seed papers from data/papers.json
    local_papers_path = app.config.get('LOCAL_PAPERS_PATH')
    if local_papers_path and Path(local_papers_path).exists():
        try:
            with open(local_papers_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for paper in data.get('papers', []):
                    db.papers.update_one({'id': paper['id']}, {'$set': paper}, upsert=True)
            logger.info("Loaded and seeded papers from data/papers.json")
        except Exception as e:
            logger.error(f"Error loading initial papers from {local_papers_path}: {e}")
