import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from db.DB import DB

db = DB()
db.connect()


update_query = """
UPDATE player_boxscore 
SET player_id = CAST(SPLIT_PART(boxscore_id, '-', 1) AS INTEGER)
WHERE player_id IS NULL
"""


db.execute_query(update_query)
print("Successfully updated player_id from boxscore_id")

# Vérification
verify_query = """
SELECT COUNT(*) as null_count
FROM player_boxscore
WHERE player_id IS NULL
"""
result = db.fetch_dataframe(verify_query)
print(f"Remaining NULL player_ids: {result['null_count'].iloc[0]}")

db.close()
