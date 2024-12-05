import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from db.DB import DB

# Connect to database
db = DB()
db.connect()

# Update query to strip whitespace from action_type
update_query = """
UPDATE play_by_play 
SET action_type = TRIM(action_type)
WHERE action_type LIKE ' %' OR action_type LIKE '% '
"""

# Execute query and commit
db.execute_query(update_query)

print("Successfully stripped whitespace from action_type column")

# Close connection
db.close()
