import logging
import os
from typing import Optional, Any, Dict, List
from google.cloud import firestore
from app.core.config import settings

logger = logging.getLogger(__name__)

_db: Optional[Any] = None

class MockDocumentSnapshot:
    def __init__(self, doc_id: str, data: Optional[Dict[str, Any]], ref: Any):
        self.id = doc_id
        self._data = data
        self.exists = data is not None
        self.reference = ref

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data) if self._data else {}

class MockDocumentReference:
    def __init__(self, doc_id: str, collection: 'MockCollectionReference'):
        self.id = doc_id
        self.collection_ref = collection

    def get(self) -> MockDocumentSnapshot:
        data = self.collection_ref._store.get(self.id)
        return MockDocumentSnapshot(self.id, data, self)

    def set(self, data: Dict[str, Any], merge: bool = False):
        if merge and self.id in self.collection_ref._store:
            self.collection_ref._store[self.id].update(data)
        else:
            self.collection_ref._store[self.id] = dict(data)

    def update(self, data: Dict[str, Any]):
        if self.id not in self.collection_ref._store:
            self.collection_ref._store[self.id] = {}
        self.collection_ref._store[self.id].update(data)

    def delete(self):
        if self.id in self.collection_ref._store:
            del self.collection_ref._store[self.id]

    def collection(self, name: str) -> 'MockCollectionReference':
        return self.collection_ref.client._get_collection(f"{self.collection_ref.path}/{self.id}/{name}")

class MockQuery:
    def __init__(self, collection: 'MockCollectionReference', filters: List[Any] = None, order_by_field: str = None, order_dir: str = None, limit_n: int = None):
        self.collection = collection
        self.filters = filters or []
        self.order_by_field = order_by_field
        self.order_dir = order_dir
        self.limit_n = limit_n

    def where(self, filter: Any = None, **kwargs) -> 'MockQuery':
        new_filters = list(self.filters)
        if filter:
            new_filters.append(filter)
        return MockQuery(self.collection, new_filters, self.order_by_field, self.order_dir, self.limit_n)

    def order_by(self, field: str, direction: str = "ASCENDING") -> 'MockQuery':
        return MockQuery(self.collection, self.filters, field, direction, self.limit_n)

    def limit(self, count: int) -> 'MockQuery':
        return MockQuery(self.collection, self.filters, self.order_by_field, self.order_dir, count)

    def stream(self):
        results = []
        for doc_id, data in self.collection._store.items():
            matches = True
            for flt in self.filters:
                # Handle firestore.FieldFilter or tuples
                if hasattr(flt, 'field_path') and hasattr(flt, 'op_string') and hasattr(flt, 'value'):
                    val = data.get(flt.field_path)
                    if flt.op_string == "==" and val != flt.value:
                        matches = False
                        break
            if matches:
                ref = MockDocumentReference(doc_id, self.collection)
                results.append(MockDocumentSnapshot(doc_id, data, ref))

        if self.order_by_field:
            results.sort(
                key=lambda x: x.to_dict().get(self.order_by_field, ''),
                reverse=(self.order_dir == "DESCENDING")
            )
        if self.limit_n:
            results = results[:self.limit_n]
        return results

class MockCollectionReference:
    def __init__(self, path: str, client: 'MockFirestoreClient'):
        self.path = path
        self.client = client
        self._store = client._global_data.setdefault(path, {})

    def document(self, doc_id: Optional[str] = None) -> MockDocumentReference:
        if not doc_id:
            counter = self.client._auto_ids.get(self.path, 0) + 1
            self.client._auto_ids[self.path] = counter
            doc_id = f"doc_{counter}"
        return MockDocumentReference(doc_id, self)

    def where(self, filter: Any = None, **kwargs) -> MockQuery:
        return MockQuery(self, [filter] if filter else [])

    def order_by(self, field: str, direction: str = "ASCENDING") -> MockQuery:
        return MockQuery(self, [], field, direction)

    def limit(self, count: int) -> MockQuery:
        return MockQuery(self, [], None, None, count)

    def stream(self):
        return MockQuery(self).stream()

class MockWriteBatch:
    def __init__(self):
        self.ops = []

    def set(self, ref: MockDocumentReference, data: Dict[str, Any], merge: bool = False):
        self.ops.append(('set', ref, data, merge))

    def update(self, ref: MockDocumentReference, data: Dict[str, Any]):
        self.ops.append(('update', ref, data))

    def delete(self, ref: MockDocumentReference):
        self.ops.append(('delete', ref))

    def commit(self):
        for op in self.ops:
            if op[0] == 'set':
                op[1].set(op[2], merge=op[3])
            elif op[0] == 'update':
                op[1].update(op[2])
            elif op[0] == 'delete':
                op[1].delete()
        self.ops.clear()

class MockFirestoreClient:
    def __init__(self):
        self._global_data: Dict[str, Dict[str, Any]] = {}
        self._auto_ids: Dict[str, int] = {}  # per-collection monotonic counters

    def _get_collection(self, path: str) -> MockCollectionReference:
        return MockCollectionReference(path, self)

    def collection(self, name: str) -> MockCollectionReference:
        return self._get_collection(name)

    def collection_group(self, name: str) -> MockQuery:
        return MockQuery(self.collection(name))

    def batch(self) -> MockWriteBatch:
        return MockWriteBatch()

_mock_db_instance = MockFirestoreClient()

def get_firestore_client() -> Any:
    global _db
    if _db is not None:
        return _db

    # In MOCK_MODE or when ADC credentials are not configured locally
    if settings.MOCK_MODE or os.getenv("MOCK_MODE", "false").lower() == "true":
        return _mock_db_instance

    try:
        _db = firestore.Client(
            project=settings.PROJECT_ID,
            database=settings.FIRESTORE_DATABASE
        )
        return _db
    except Exception as e:
        logger.warning(f"Google Application Default Credentials not found ({e}). Falling back to In-Memory Local Firestore Mock for local development.")
        _db = _mock_db_instance
        return _db
