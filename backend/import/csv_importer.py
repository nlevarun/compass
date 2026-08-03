"""
CSV Historical Data Importer

Generic CSV importer with column mapping and validation.
Supports any CSV format with configurable field mapping.
"""

import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional, Callable
from sqlalchemy.orm import Session


class CSVImporter:
    """Import feedback from CSV files with column mapping"""

    def __init__(
        self,
        file_path: str,
        source_id: int,
        db: Session,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ):
        """
        Initialize CSV importer.

        Args:
            file_path: Path to CSV file
            source_id: Compass source ID for imported data
            db: Database session
            progress_callback: Optional callback for progress updates
        """
        self.file_path = file_path
        self.source_id = source_id
        self.db = db
        self.progress_callback = progress_callback

    def preview_csv(self, num_rows: int = 10) -> Dict:
        """
        Preview CSV file structure and data.

        Args:
            num_rows: Number of rows to preview

        Returns:
            Dictionary with columns and sample data
        """
        try:
            df = pd.read_csv(self.file_path, nrows=num_rows)

            return {
                "status": "success",
                "columns": df.columns.tolist(),
                "sample_data": df.head(num_rows).to_dict(orient="records"),
                "total_rows": len(df),
                "dtypes": df.dtypes.astype(str).to_dict()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def validate_mapping(self, column_mapping: Dict[str, str]) -> Dict:
        """
        Validate column mapping against CSV structure.

        Args:
            column_mapping: Dictionary mapping Compass fields to CSV columns
                Example: {
                    "text": "feedback_text",
                    "title": "subject",
                    "customer_name": "customer",
                    "submitted_at": "date_submitted"
                }

        Returns:
            Validation result dictionary
        """
        required_fields = ["text"]  # Only text is required
        optional_fields = [
            "title", "customer_name", "customer_revenue",
            "submitted_at", "sentiment_score"
        ]

        errors = []
        warnings = []

        # Check required fields
        for field in required_fields:
            if field not in column_mapping:
                errors.append(f"Required field '{field}' not mapped")

        # Validate CSV columns exist
        try:
            df = pd.read_csv(self.file_path, nrows=1)
            csv_columns = df.columns.tolist()

            for compass_field, csv_column in column_mapping.items():
                if csv_column not in csv_columns:
                    errors.append(f"CSV column '{csv_column}' not found in file")

            # Check for optional fields
            for field in optional_fields:
                if field not in column_mapping:
                    warnings.append(f"Optional field '{field}' not mapped")

        except Exception as e:
            errors.append(f"Error reading CSV: {str(e)}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    def parse_row_to_feedback(
        self,
        row: pd.Series,
        column_mapping: Dict[str, str]
    ) -> Optional[Dict]:
        """
        Convert CSV row to Compass feedback format.

        Args:
            row: Pandas Series representing a CSV row
            column_mapping: Column mapping configuration

        Returns:
            Feedback dictionary or None if invalid
        """
        try:
            # Extract required field
            text = str(row[column_mapping["text"]]) if "text" in column_mapping else None
            if not text or pd.isna(text) or text.strip() == "":
                return None

            # Extract optional fields
            title = None
            if "title" in column_mapping and column_mapping["title"] in row.index:
                title = str(row[column_mapping["title"]])[:500]
                if pd.isna(title):
                    title = None

            customer_name = None
            if "customer_name" in column_mapping and column_mapping["customer_name"] in row.index:
                customer_name = str(row[column_mapping["customer_name"]])
                if pd.isna(customer_name):
                    customer_name = None

            customer_revenue = None
            if "customer_revenue" in column_mapping and column_mapping["customer_revenue"] in row.index:
                try:
                    revenue_val = row[column_mapping["customer_revenue"]]
                    if not pd.isna(revenue_val):
                        # Handle currency strings like "$1,234.56"
                        if isinstance(revenue_val, str):
                            revenue_val = revenue_val.replace("$", "").replace(",", "")
                        customer_revenue = float(revenue_val)
                except (ValueError, TypeError):
                    pass

            sentiment_score = None
            if "sentiment_score" in column_mapping and column_mapping["sentiment_score"] in row.index:
                try:
                    score_val = row[column_mapping["sentiment_score"]]
                    if not pd.isna(score_val):
                        sentiment_score = float(score_val)
                        # Clamp to -1 to 1 range
                        sentiment_score = max(-1.0, min(1.0, sentiment_score))
                except (ValueError, TypeError):
                    pass

            # Parse date
            submitted_at = datetime.utcnow()  # Default to now
            if "submitted_at" in column_mapping and column_mapping["submitted_at"] in row.index:
                date_val = row[column_mapping["submitted_at"]]
                if not pd.isna(date_val):
                    try:
                        # Try to parse date (pandas is usually good at this)
                        submitted_at = pd.to_datetime(date_val).to_pydatetime()
                    except Exception:
                        pass  # Fall back to default

            # Build metadata with all unmapped columns
            source_metadata = {}
            for col in row.index:
                if col not in column_mapping.values():
                    val = row[col]
                    if not pd.isna(val):
                        source_metadata[col] = str(val)

            return {
                "source_id": self.source_id,
                "text": text[:10000],
                "title": title,
                "customer_name": customer_name,
                "customer_revenue": customer_revenue,
                "sentiment_score": sentiment_score,
                "submitted_at": submitted_at,
                "ingested_at": datetime.utcnow(),
                "source_metadata": source_metadata
            }

        except Exception as e:
            print(f"Error parsing row: {e}")
            return None

    def import_csv(
        self,
        column_mapping: Dict[str, str],
        batch_size: int = 500,
        skip_invalid: bool = True
    ) -> Dict:
        """
        Import CSV data with column mapping.

        Args:
            column_mapping: Mapping of Compass fields to CSV columns
            batch_size: Number of rows to commit at once
            skip_invalid: Whether to skip invalid rows or fail

        Returns:
            Import statistics dictionary
        """
        from models import Feedback

        # Validate mapping first
        validation = self.validate_mapping(column_mapping)
        if not validation["valid"]:
            return {
                "status": "error",
                "errors": validation["errors"]
            }

        print(f"Starting CSV import from {self.file_path}...")

        try:
            # Read CSV in chunks for memory efficiency
            chunk_size = 10000
            total_imported = 0
            total_skipped = 0
            total_rows = 0

            for chunk_num, chunk in enumerate(pd.read_csv(self.file_path, chunksize=chunk_size)):
                feedback_batch = []

                for idx, row in chunk.iterrows():
                    total_rows += 1

                    # Parse row
                    feedback_data = self.parse_row_to_feedback(row, column_mapping)

                    if feedback_data is None:
                        total_skipped += 1
                        if not skip_invalid:
                            raise ValueError(f"Invalid row at index {idx}")
                        continue

                    feedback_batch.append(Feedback(**feedback_data))

                    # Batch commit
                    if len(feedback_batch) >= batch_size:
                        self.db.bulk_save_objects(feedback_batch)
                        self.db.commit()
                        total_imported += len(feedback_batch)
                        feedback_batch = []

                        # Progress callback
                        if self.progress_callback:
                            self.progress_callback(total_imported, total_rows)

                        print(f"Imported {total_imported} rows (skipped {total_skipped})...")

                # Commit remaining in chunk
                if feedback_batch:
                    self.db.bulk_save_objects(feedback_batch)
                    self.db.commit()
                    total_imported += len(feedback_batch)

            print(f"✓ CSV import complete: {total_imported} imported, {total_skipped} skipped")

            return {
                "status": "success",
                "total_imported": total_imported,
                "total_skipped": total_skipped,
                "total_rows": total_rows
            }

        except Exception as e:
            print(f"Error during CSV import: {e}")
            return {
                "status": "error",
                "error": str(e),
                "total_imported": total_imported,
                "total_skipped": total_skipped
            }

    def auto_detect_mapping(self) -> Dict[str, str]:
        """
        Attempt to auto-detect column mapping based on column names.

        Returns:
            Suggested column mapping
        """
        try:
            df = pd.read_csv(self.file_path, nrows=10)
            columns = [col.lower() for col in df.columns]

            mapping = {}

            # Text field detection (required)
            text_candidates = ["feedback", "text", "comment", "description", "body", "message", "content"]
            for candidate in text_candidates:
                for idx, col in enumerate(columns):
                    if candidate in col:
                        mapping["text"] = df.columns[idx]
                        break
                if "text" in mapping:
                    break

            # Title field
            title_candidates = ["title", "subject", "summary", "heading"]
            for candidate in title_candidates:
                for idx, col in enumerate(columns):
                    if candidate in col:
                        mapping["title"] = df.columns[idx]
                        break
                if "title" in mapping:
                    break

            # Customer name
            customer_candidates = ["customer", "name", "user", "contact", "client", "account"]
            for candidate in customer_candidates:
                for idx, col in enumerate(columns):
                    if candidate in col and "email" not in col:
                        mapping["customer_name"] = df.columns[idx]
                        break
                if "customer_name" in mapping:
                    break

            # Revenue
            revenue_candidates = ["revenue", "arr", "mrr", "value", "contract"]
            for candidate in revenue_candidates:
                for idx, col in enumerate(columns):
                    if candidate in col:
                        mapping["customer_revenue"] = df.columns[idx]
                        break
                if "customer_revenue" in mapping:
                    break

            # Date
            date_candidates = ["date", "created", "submitted", "timestamp", "time"]
            for candidate in date_candidates:
                for idx, col in enumerate(columns):
                    if candidate in col:
                        mapping["submitted_at"] = df.columns[idx]
                        break
                if "submitted_at" in mapping:
                    break

            # Sentiment
            sentiment_candidates = ["sentiment", "score", "rating"]
            for candidate in sentiment_candidates:
                for idx, col in enumerate(columns):
                    if candidate in col:
                        mapping["sentiment_score"] = df.columns[idx]
                        break
                if "sentiment_score" in mapping:
                    break

            return mapping

        except Exception as e:
            print(f"Error auto-detecting mapping: {e}")
            return {}
