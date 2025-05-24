import json
from connection import get_db_connection

def clean_text(text):
    """Clean and encode text to handle special characters."""
    if text is None:
        return ""
    try:
        # Replace problematic characters and ensure UTF-8
        text = text.replace('\u2019', "'").replace('\u2018', "'")
        text = text.replace('\u201c', '"').replace('\u201d', '"')
        return text.encode('utf-8', 'ignore').decode('utf-8')
    except:
        return str(text)

def insert_data_from_json(file_path):
    """Insert data from a JSON file into the PostgreSQL database."""
    connection = None
    try:
        with open(file_path, "r", encoding='utf-8') as file:
            data = json.load(file)

        connection = get_db_connection()
        cursor = connection.cursor()

        # Set client encoding to UTF-8
        cursor.execute("SET CLIENT_ENCODING TO 'UTF8';")
        
        # Modify the bank table to allow NULL ratings (if needed)
        try:
            cursor.execute("ALTER TABLE bank ALTER COLUMN global_rating DROP NOT NULL;")
        except:
            pass  # Ignore if column is already nullable

        insert_bank_query = """
        INSERT INTO bank (name, branch_name, global_rating, location)
        VALUES (%s, %s, %s, %s)
        RETURNING bank_id
        """

        insert_review_query = """
        INSERT INTO review (review_text, rating, display_name, review_date, bank_id)
        VALUES (%s, %s, %s, %s, %s)
        """

        records_inserted = 0
        reviews_inserted = 0
        errors = 0
        
        # Handle both single record and list of records
        records = data if isinstance(data, list) else [data]
        
        for record in records:
            try:
                # Process bank data with defaults for missing fields
                address = record.get("formattedAddress", "Unknown Location")
                name = record.get("displayName", {}).get("text", "Unknown Bank")
                rating = record.get("rating")  # This can be NULL
                
                # Clean and prepare data
                branch = clean_text(f"{name} {address.split(',')[0]}")
                name = clean_text(name)
                location = clean_text(address)

                # Insert bank (rating can be NULL)
                cursor.execute(insert_bank_query, (name, branch, rating, location))
                bank_id = cursor.fetchone()[0]
                records_inserted += 1
                print(f"Inserted bank ID {bank_id}: {name}")

                # Process reviews if they exist
                for review in record.get("reviews", []):
                    try:
                        review_text = clean_text(review.get("text", {}).get("text", ""))
                        if not review_text.strip():
                            continue  # Skip empty reviews
                            
                        cursor.execute(insert_review_query, (
                            review_text,
                            review.get("rating", 0),  # Default to 0 if no rating
                            clean_text(review.get("authorAttribution", {}).get("displayName", "Anonymous")),
                            review.get("publishTime", "")[:10],  # Just the date part
                            bank_id
                        ))
                        reviews_inserted += 1
                    except Exception as rev_err:
                        print(f"Error inserting review: {rev_err}")
                        errors += 1
                        continue

            except Exception as bank_err:
                print(f"Error processing bank record: {bank_err}")
                errors += 1
                continue

        connection.commit()
        print(f"\nSummary:")
        print(f"Successfully inserted {records_inserted} banks")
        print(f"Successfully inserted {reviews_inserted} reviews")
        print(f"Encountered {errors} errors")

    except Exception as error:
        print(f"Fatal error: {error}")
        if connection:
            connection.rollback()
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Database connection closed")

if __name__ == "__main__":
    insert_data_from_json("banques2.json")