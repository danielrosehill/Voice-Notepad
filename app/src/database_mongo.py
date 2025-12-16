"""Mongita database for transcript history, prompts, and settings.

This replaces the SQLite database with Mongita (pure Python MongoDB implementation).
Provides identical API to the old database.py for easy migration.
"""

import csv
import threading
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

from mongita import MongitaClientDisk


# Database directory
DB_DIR = Path.home() / ".config" / "voice-notepad-v3"
MONGO_DIR = DB_DIR / "mongita"
AUDIO_ARCHIVE_DIR = DB_DIR / "audio-archive"
CSV_EXPORT_FILE = DB_DIR / "transcription_history.csv"


@dataclass
class TranscriptionRecord:
    """A single transcription record."""
    id: Optional[str]  # MongoDB _id as string
    timestamp: str
    provider: str
    model: str
    transcript_text: str
    audio_duration_seconds: Optional[float]
    inference_time_ms: Optional[int]
    input_tokens: int
    output_tokens: int
    estimated_cost: float
    text_length: int
    word_count: int
    audio_file_path: Optional[str]
    vad_audio_duration_seconds: Optional[float]
    prompt_text_length: int = 0
    source: str = "recording"  # "recording" or "file"
    source_path: Optional[str] = None

    def to_dict(self):
        """Convert to dict for MongoDB storage."""
        d = asdict(self)
        # Remove id if None (let MongoDB generate _id)
        if d.get('id') is None:
            d.pop('id', None)
        return d

    @classmethod
    def from_doc(cls, doc: Dict[str, Any]) -> "TranscriptionRecord":
        """Create from MongoDB document."""
        # Convert _id to string id
        doc_copy = doc.copy()
        if '_id' in doc_copy:
            doc_copy['id'] = str(doc_copy['_id'])
            del doc_copy['_id']

        # Provide defaults for optional fields
        defaults = {
            'audio_duration_seconds': None,
            'inference_time_ms': None,
            'input_tokens': 0,
            'output_tokens': 0,
            'estimated_cost': 0.0,
            'text_length': 0,
            'word_count': 0,
            'audio_file_path': None,
            'vad_audio_duration_seconds': None,
            'prompt_text_length': 0,
            'source': 'recording',
            'source_path': None,
        }

        for key, default_val in defaults.items():
            if key not in doc_copy:
                doc_copy[key] = default_val

        return cls(**doc_copy)


class TranscriptionDB:
    """Mongita database for storing transcription history and prompts.

    Collections:
    - transcriptions: Transcription history (replaces SQLite table)
    - prompts: Prompt library (new)

    Thread-safe: all operations are protected by a lock.
    """

    def __init__(self):
        MONGO_DIR.mkdir(parents=True, exist_ok=True)
        AUDIO_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

        self._client: Optional[MongitaClientDisk] = None
        self._db = None
        self._lock = threading.RLock()

        self._init_db()

    def _get_db(self):
        """Get database connection, creating if needed."""
        if self._client is None:
            self._client = MongitaClientDisk(str(MONGO_DIR))
            self._db = self._client.voice_notepad
        return self._db

    def _init_db(self):
        """Initialize database and indexes."""
        with self._lock:
            db = self._get_db()

            # Transcriptions collection indexes
            transcriptions = db.transcriptions
            transcriptions.create_index('timestamp')
            transcriptions.create_index('provider')
            transcriptions.create_index('source')

            # Text search index (Mongita supports text indexes)
            try:
                transcriptions.create_index([('transcript_text', 'text')])
            except Exception:
                # Text indexes may not be fully supported, fallback to regex search
                pass

    def save_transcription(
        self,
        provider: str,
        model: str,
        transcript_text: str,
        audio_duration_seconds: Optional[float] = None,
        inference_time_ms: Optional[int] = None,
        input_tokens: int = 0,
        output_tokens: int = 0,
        estimated_cost: float = 0.0,
        audio_file_path: Optional[str] = None,
        vad_audio_duration_seconds: Optional[float] = None,
        prompt_text_length: int = 0,
        source: str = "recording",
        source_path: Optional[str] = None,
    ) -> str:
        """Save a transcription and return its ID as string."""
        with self._lock:
            db = self._get_db()
            timestamp = datetime.now().isoformat()
            text_length = len(transcript_text)
            word_count = len(transcript_text.split())

            doc = {
                'timestamp': timestamp,
                'provider': provider,
                'model': model,
                'transcript_text': transcript_text,
                'audio_duration_seconds': audio_duration_seconds,
                'inference_time_ms': inference_time_ms,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'estimated_cost': estimated_cost,
                'text_length': text_length,
                'word_count': word_count,
                'audio_file_path': audio_file_path,
                'vad_audio_duration_seconds': vad_audio_duration_seconds,
                'prompt_text_length': prompt_text_length,
                'source': source,
                'source_path': source_path,
            }

            result = db.transcriptions.insert_one(doc)
            return str(result.inserted_id)

    def get_transcription(self, id: str) -> Optional[TranscriptionRecord]:
        """Get a single transcription by ID."""
        with self._lock:
            db = self._get_db()
            from bson import ObjectId

            try:
                doc = db.transcriptions.find_one({'_id': ObjectId(id)})
                if doc:
                    return TranscriptionRecord.from_doc(doc)
            except Exception:
                # Invalid ObjectId format
                pass
            return None

    def get_transcriptions(
        self,
        limit: int = 50,
        offset: int = 0,
        search: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> List[TranscriptionRecord]:
        """Get transcriptions with pagination and optional filtering."""
        with self._lock:
            db = self._get_db()

            query = {}

            if search:
                # Use regex search for text matching
                query['transcript_text'] = {'$regex': search, '$options': 'i'}

            if provider:
                query['provider'] = provider

            cursor = db.transcriptions.find(query).sort('timestamp', -1).skip(offset).limit(limit)
            return [TranscriptionRecord.from_doc(doc) for doc in cursor]

    def get_total_count(self, search: Optional[str] = None, provider: Optional[str] = None) -> int:
        """Get total count of transcriptions (for pagination)."""
        with self._lock:
            db = self._get_db()

            query = {}

            if search:
                query['transcript_text'] = {'$regex': search, '$options': 'i'}

            if provider:
                query['provider'] = provider

            return db.transcriptions.count_documents(query)

    def delete_transcription(self, id: str) -> bool:
        """Delete a transcription by ID. Returns True if deleted."""
        with self._lock:
            db = self._get_db()
            from bson import ObjectId

            try:
                # Get the record first to check for audio file
                doc = db.transcriptions.find_one({'_id': ObjectId(id)})
                if doc and doc.get('audio_file_path'):
                    audio_path = Path(doc['audio_file_path'])
                    if audio_path.exists():
                        audio_path.unlink()

                result = db.transcriptions.delete_one({'_id': ObjectId(id)})
                return result.deleted_count > 0
            except Exception:
                return False

    def delete_all(self) -> int:
        """Delete all transcriptions. Returns count of deleted records."""
        with self._lock:
            db = self._get_db()

            # Delete audio files
            for audio_file in AUDIO_ARCHIVE_DIR.glob("*.opus"):
                audio_file.unlink()

            result = db.transcriptions.delete_many({})
            return result.deleted_count

    def get_storage_stats(self) -> dict:
        """Get storage statistics."""
        with self._lock:
            db = self._get_db()

            # Count records
            total_records = db.transcriptions.count_documents({})

            # Database directory size (Mongita uses multiple files)
            db_size = sum(f.stat().st_size for f in MONGO_DIR.rglob('*') if f.is_file())

            # Audio archive size
            audio_size = sum(f.stat().st_size for f in AUDIO_ARCHIVE_DIR.glob("*.opus"))

            # Count records with audio
            records_with_audio = db.transcriptions.count_documents(
                {'audio_file_path': {'$ne': None}}
            )

            return {
                "total_records": total_records,
                "records_with_audio": records_with_audio,
                "db_size_bytes": db_size,
                "audio_size_bytes": audio_size,
                "total_size_bytes": db_size + audio_size,
            }

    def get_model_performance(self) -> List[dict]:
        """Get aggregated performance statistics by provider/model."""
        with self._lock:
            db = self._get_db()

            # MongoDB aggregation pipeline
            pipeline = [
                {
                    '$match': {
                        'inference_time_ms': {'$ne': None}
                    }
                },
                {
                    '$group': {
                        '_id': {
                            'provider': '$provider',
                            'model': '$model'
                        },
                        'count': {'$sum': 1},
                        'avg_inference_ms': {'$avg': '$inference_time_ms'},
                        'total_cost': {'$sum': '$estimated_cost'},
                        'avg_audio_duration': {'$avg': '$audio_duration_seconds'},
                        'total_text_length': {'$sum': '$text_length'},
                        'total_inference_time': {'$sum': '$inference_time_ms'}
                    }
                },
                {
                    '$sort': {'count': -1}
                }
            ]

            results = list(db.transcriptions.aggregate(pipeline))

            return [
                {
                    "provider": r['_id']['provider'],
                    "model": r['_id']['model'],
                    "count": r['count'],
                    "avg_inference_ms": round(r.get('avg_inference_ms', 0), 1),
                    "avg_chars_per_sec": round(
                        (r['total_text_length'] * 1000.0 / r['total_inference_time'])
                        if r['total_inference_time'] > 0 else 0,
                        1
                    ),
                    "total_cost": round(r.get('total_cost', 0), 4),
                    "avg_audio_duration": round(r.get('avg_audio_duration', 0), 1),
                }
                for r in results
            ]

    def get_recent_stats(self, days: int = 7) -> dict:
        """Get statistics for recent days."""
        with self._lock:
            db = self._get_db()

            cutoff = (datetime.now() - timedelta(days=days)).isoformat()

            pipeline = [
                {
                    '$match': {
                        'timestamp': {'$gte': cutoff}
                    }
                },
                {
                    '$group': {
                        '_id': None,
                        'count': {'$sum': 1},
                        'total_cost': {'$sum': '$estimated_cost'},
                        'avg_inference_ms': {'$avg': '$inference_time_ms'},
                        'total_chars': {'$sum': '$text_length'},
                        'total_words': {'$sum': '$word_count'}
                    }
                }
            ]

            results = list(db.transcriptions.aggregate(pipeline))

            if results:
                r = results[0]
                return {
                    "count": r.get('count', 0),
                    "total_cost": round(r.get('total_cost', 0), 4),
                    "avg_inference_ms": round(r.get('avg_inference_ms', 0), 1),
                    "total_chars": r.get('total_chars', 0),
                    "total_words": r.get('total_words', 0),
                }

            return {
                "count": 0,
                "total_cost": 0,
                "avg_inference_ms": 0,
                "total_chars": 0,
                "total_words": 0,
            }

    def _get_cost_stats(self, query: Dict[str, Any]) -> dict:
        """Helper to get cost statistics for a query."""
        with self._lock:
            db = self._get_db()

            pipeline = [
                {'$match': query},
                {
                    '$group': {
                        '_id': None,
                        'count': {'$sum': 1},
                        'total_cost': {'$sum': '$estimated_cost'}
                    }
                }
            ]

            results = list(db.transcriptions.aggregate(pipeline))

            if results:
                r = results[0]
                return {
                    "count": r.get('count', 0),
                    "total_cost": round(r.get('total_cost', 0), 6),
                }

            return {"count": 0, "total_cost": 0}

    def get_cost_today(self) -> dict:
        """Get cost for today (since midnight local time)."""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        return self._get_cost_stats({'timestamp': {'$gte': today_start}})

    def get_cost_this_hour(self) -> dict:
        """Get cost for the current hour."""
        hour_start = datetime.now().replace(minute=0, second=0, microsecond=0).isoformat()
        return self._get_cost_stats({'timestamp': {'$gte': hour_start}})

    def get_cost_last_hour(self) -> dict:
        """Get cost for the previous hour."""
        now = datetime.now()
        last_hour_start = (now - timedelta(hours=1)).replace(minute=0, second=0, microsecond=0).isoformat()
        this_hour_start = now.replace(minute=0, second=0, microsecond=0).isoformat()

        return self._get_cost_stats({
            'timestamp': {
                '$gte': last_hour_start,
                '$lt': this_hour_start
            }
        })

    def get_cost_this_week(self) -> dict:
        """Get cost for the current week (Monday to now)."""
        now = datetime.now()
        # Get Monday of current week
        monday = now - timedelta(days=now.weekday())
        week_start = monday.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

        return self._get_cost_stats({'timestamp': {'$gte': week_start}})

    def get_cost_this_month(self) -> dict:
        """Get cost for the current calendar month."""
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
        return self._get_cost_stats({'timestamp': {'$gte': month_start}})

    def get_cost_last_60_min(self) -> dict:
        """Get cost for the last 60 minutes."""
        cutoff = (datetime.now() - timedelta(minutes=60)).isoformat()
        return self._get_cost_stats({'timestamp': {'$gte': cutoff}})

    def get_cost_all_time(self) -> dict:
        """Get total cost for all transcriptions."""
        return self._get_cost_stats({})

    def get_cost_by_provider(self) -> List[dict]:
        """Get cost breakdown by provider."""
        with self._lock:
            db = self._get_db()

            pipeline = [
                {
                    '$group': {
                        '_id': '$provider',
                        'count': {'$sum': 1},
                        'total_cost': {'$sum': '$estimated_cost'}
                    }
                },
                {'$sort': {'total_cost': -1}}
            ]

            results = list(db.transcriptions.aggregate(pipeline))

            return [
                {
                    "provider": r['_id'],
                    "count": r['count'],
                    "total_cost": round(r.get('total_cost', 0), 6),
                }
                for r in results
            ]

    def get_cost_by_model(self) -> List[dict]:
        """Get cost breakdown by model."""
        with self._lock:
            db = self._get_db()

            pipeline = [
                {
                    '$group': {
                        '_id': {
                            'provider': '$provider',
                            'model': '$model'
                        },
                        'count': {'$sum': 1},
                        'total_cost': {'$sum': '$estimated_cost'}
                    }
                },
                {'$sort': {'total_cost': -1}}
            ]

            results = list(db.transcriptions.aggregate(pipeline))

            return [
                {
                    "provider": r['_id']['provider'],
                    "model": r['_id']['model'],
                    "count": r['count'],
                    "total_cost": round(r.get('total_cost', 0), 6),
                }
                for r in results
            ]

    def export_to_csv(
        self,
        filepath: Optional[Path] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> tuple[Path, int]:
        """Export transcriptions to a CSV file."""
        if filepath is None:
            filepath = CSV_EXPORT_FILE

        with self._lock:
            db = self._get_db()

            query = {}

            if start_date:
                query['timestamp'] = {'$gte': start_date}

            if end_date:
                # Add one day to make end_date inclusive
                end_dt = datetime.fromisoformat(end_date) + timedelta(days=1)
                if 'timestamp' in query:
                    query['timestamp']['$lt'] = end_dt.isoformat()
                else:
                    query['timestamp'] = {'$lt': end_dt.isoformat()}

            cursor = db.transcriptions.find(query).sort('timestamp', -1)
            docs = list(cursor)

        record_count = len(docs)

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Timestamp',
                'Provider',
                'Model',
                'Transcript',
                'Audio Duration (s)',
                'VAD Duration (s)',
                'Inference Time (ms)',
                'Input Tokens',
                'Output Tokens',
                'Estimated Cost',
                'Word Count'
            ])
            for doc in docs:
                writer.writerow([
                    doc.get('timestamp'),
                    doc.get('provider'),
                    doc.get('model'),
                    doc.get('transcript_text'),
                    doc.get('audio_duration_seconds'),
                    doc.get('vad_audio_duration_seconds'),
                    doc.get('inference_time_ms'),
                    doc.get('input_tokens'),
                    doc.get('output_tokens'),
                    doc.get('estimated_cost'),
                    doc.get('word_count')
                ])

        return filepath, record_count

    def close(self):
        """Close database connection."""
        # Mongita doesn't require explicit close, but we'll clean up references
        self._client = None
        self._db = None


# Global instance with thread-safe initialization
_db: Optional[TranscriptionDB] = None
_db_lock = threading.Lock()


def get_db() -> TranscriptionDB:
    """Get the global database instance (thread-safe)."""
    global _db
    if _db is None:
        with _db_lock:
            # Double-check after acquiring lock
            if _db is None:
                _db = TranscriptionDB()
    return _db
