class Map:
    def __init__(self, capacity=8):
        self._capacity = capacity
        self._table = [[] for _ in range(self._capacity)]
        self._n = 0

    def _hash(self, key):
        return hash(key) % self._capacity

    def __setitem__(self, key, value):
        bucket_index = self._hash(key)
        bucket = self._table[bucket_index]
        
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        
        bucket.append((key, value))
        self._n += 1
        
        if self._n > self._capacity * 0.7:
            self._resize(2 * self._capacity)

    def __getitem__(self, key):
        bucket_index = self._hash(key)
        for k, v in self._table[bucket_index]:
            if k == key:
                return v
        raise KeyError(f"Key {key} not found")

    def __delitem__(self, key):
        bucket_index = self._hash(key)
        bucket = self._table[bucket_index]
        
        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self._n -= 1
                return
        
        raise KeyError(f"Key {key} not found")

    def _resize(self, new_capacity):
        old_table = self._table
        self._capacity = new_capacity
        self._table = [[] for _ in range(new_capacity)]
        self._n = 0
        
        for bucket in old_table:
            for key, value in bucket:
                self[key] = value

    def __len__(self):
        return self._n

    def __iter__(self):
        for bucket in self._table:
            for k, _ in bucket:
                yield k

    def __contains__(self, key):
        try:
            _ = self[key]
            return True
        except KeyError:
            return False

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self):
        result = []
        for bucket in self._table:
            for k, _ in bucket:
                result.append(k)
        return result

    def values(self):
        result = []
        for bucket in self._table:
            for _, v in bucket:
                result.append(v)
        return result

    def items(self):
        result = []
        for bucket in self._table:
            for item in bucket:
                result.append(item)
        return result

    def clear(self):
        self._table = [[] for _ in range(self._capacity)]
        self._n = 0

    def __str__(self):
        items = []
        for bucket in self._table:
            for key, value in bucket:
                items.append(f"{key!r}: {value!r}")
        return "{" + ", ".join(items) + "}"
