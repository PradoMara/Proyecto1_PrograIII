import hashlib
import time

class Map:
    def __init__(self, capacity=8):
        self._capacity = capacity
        self._table = [[] for _ in range(self._capacity)]  # Bucket array
        self._n = 0  # Number of items

    def _hash(self, key):
        """Compute the index for a key using hash() and compression."""
        return hash(key) % self._capacity

    def __setitem__(self, key, value):
        """Insert or update a key-value pair."""
        bucket_index = self._hash(key)
        bucket = self._table[bucket_index]
        
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)  # Update if exists
                return
        
        bucket.append((key, value))
        self._n += 1
        
        # Resize if load factor > 70%
        if self._n > self._capacity * 0.7:
            self._resize(2 * self._capacity)

    def __getitem__(self, key):
        """Get the value associated with a key."""
        bucket_index = self._hash(key)
        for k, v in self._table[bucket_index]:
            if k == key:
                return v
        raise KeyError(f"Key {key} not found")

    def __delitem__(self, key):
        """Delete an item by key."""
        bucket_index = self._hash(key)
        bucket = self._table[bucket_index]
        
        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self._n -= 1
                
                # Resize if load factor < 20%
                if self._capacity > 8 and self._n < self._capacity * 0.2:
                    self._resize(self._capacity // 2)
                return
        
        raise KeyError(f"Key {key} not found")

    def _resize(self, new_capacity):
        """Resize the hash table."""
        old_table = self._table
        self._capacity = new_capacity
        self._table = [[] for _ in range(new_capacity)]
        self._n = 0
        
        for bucket in old_table:
            for key, value in bucket:
                self[key] = value  # Reinsert

    def __len__(self):
        """Number of elements in the map."""
        return self._n

    def __iter__(self):
        """Iterator over keys."""
        for bucket in self._table:
            for k, _ in bucket:
                yield k

    def __contains__(self, key):
        """Check if a key exists."""
        try:
            _ = self[key]
            return True
        except KeyError:
            return False

    def get(self, key, default=None):
        """Get value or default if key doesn't exist."""
        try:
            return self[key]
        except KeyError:
            return default

    def setdefault(self, key, default=None):
        """Return value if exists; otherwise set default and return it."""
        bucket_index = self._hash(key)
        bucket = self._table[bucket_index]
        
        for i, (k, v) in enumerate(bucket):
            if k == key:
                return v
        
        bucket.append((key, default))
        self._n += 1
        return default

    def pop(self, key, default=None):
        """Remove and return item, or default/KeyError if not found."""
        bucket_index = self._hash(key)
        bucket = self._table[bucket_index]
        
        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self._n -= 1
                return v
        
        if default is not None:
            return default
        raise KeyError(f"Key {key} not found")

    def popitem(self):
        """Remove and return an arbitrary key-value pair."""
        for bucket in self._table:
            if bucket:
                self._n -= 1
                return bucket.pop()
        raise KeyError("Map is empty")

    def clear(self):
        """Remove all items from the map."""
        self._table = [[] for _ in range(self._capacity)]
        self._n = 0

    def keys(self):
        """Return a view of all keys."""
        return iter(self)

    def values(self):
        """Return a view of all values."""
        for bucket in self._table:
            for _, v in bucket:
                yield v

    def items(self):
        """Return a view of all key-value pairs."""
        for bucket in self._table:
            for item in bucket:
                yield item

    def update(self, other):
        """Update map with key-value pairs from another map/dict."""
        if isinstance(other, Map):
            for key, value in other.items():
                self[key] = value
        else:
            for key, value in dict(other).items():
                self[key] = value

    def __eq__(self, other):
        """Compare if two maps are equal."""
        if not isinstance(other, Map) or len(self) != len(other):
            return False
        for key, value in self.items():
            try:
                if other[key] != value:
                    return False
            except KeyError:
                return False
        return True

    def __ne__(self, other):
        """Compare if two maps are different."""
        return not (self == other)

    def __str__(self):
        """String representation of the map."""
        items = []
        for bucket in self._table:
            for key, value in bucket:
                items.append(f"{key!r}: {value!r}")
        return "{" + ", ".join(items) + "}"

# Funciones para generar IDs hashed
def generate_client_id(name, email):
    """Genera un ID hash para un cliente basado en su nombre y email"""
    combined = f"{name}_{email}_{int(time.time())}"
    return hashlib.md5(combined.encode()).hexdigest()[:8].upper()

def generate_order_id(client_id, items_str):
    """Genera un ID hash para un pedido basado en el client_id y items"""
    combined = f"{client_id}_{items_str}_{int(time.time())}"
    return hashlib.md5(combined.encode()).hexdigest()[:8].upper()

# Example usage
m = Map()
m["name"] = "Alice"
m["age"] = 30
print(m.items())  # Outputs all key-value pairs
print(m.pop("age"))  # Outputs: 30
print("name" in m)  # Outputs: True