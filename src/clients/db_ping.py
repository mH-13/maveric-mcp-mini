from src.common.db import ping, get_logs_collection
from src.common.models import CellLog

def main():
    ok = ping()
    print("Mongo ping:", "✅" if ok else "❌")

    coll = get_logs_collection()
    doc = CellLog(cell_id=1, status="ON", run_id=1).model_dump(mode="python")
    res = coll.insert_one(doc)
    print("Inserted _id:", res.inserted_id)

if __name__ == "__main__":
    main()
