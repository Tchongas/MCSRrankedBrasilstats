# ALL OVERWORLDS

```bash
python query.py "SELECT seed_type, COUNT(id) AS count FROM matches WHERE seed_type IS NOT NULL GROUP BY seed_type ORDER BY count DESC LIMIT 5; -- Shows top 5"
```

