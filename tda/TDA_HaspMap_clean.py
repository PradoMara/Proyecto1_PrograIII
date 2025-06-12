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

    def __len__(self):
        """Return the number of items in the map."""
        return self._n

    def __contains__(self, key):
        """Return True if key is in the map."""
        try:
            self[key]
            return True
        except KeyError:
            return False

    def _resize(self, new_capacity):
        """Resize the hash table to new_capacity."""
        old_table = self._table
        self._capacity = new_capacity
        self._table = [[] for _ in range(self._capacity)]
        old_n = self._n
        self._n = 0
        
        for bucket in old_table:
            for k, v in bucket:
                self[k] = v

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

    def keys(self):
        """Return a list of all keys."""
        result = []
        for bucket in self._table:
            for k, _ in bucket:
                result.append(k)
        return result

    def values(self):
        """Return a list of all values."""
        result = []
        for bucket in self._table:
            for _, v in bucket:
                result.append(v)
        return result

    def items(self):
        """Return a list of all key-value pairs."""
        result = []
        for bucket in self._table:
            for item in bucket:
                result.append(item)
        return result

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

    def update(self, other):
        """Update map with key-value pairs from another map/dict."""
        if isinstance(other, Map):
            for key, value in other.items():
                self[key] = value
        elif hasattr(other, 'items'):
            for key, value in other.items():
                self[key] = value
        else:
            for key, value in other:
                self[key] = value

    def copy(self):
        """Return a shallow copy of the map."""
        new_map = Map(self._capacity)
        for key, value in self.items():
            new_map[key] = value
        return new_map

    def __iter__(self):
        """Return an iterator over the keys."""
        return iter(self.keys())

    def __str__(self):
        """Return string representation of the map."""
        items = [f"{k}: {v}" for k, v in self.items()]
        return "{" + ", ".join(items) + "}"

    def __repr__(self):
        """Return repr of the map."""
        return f"Map({dict(self.items())})"
