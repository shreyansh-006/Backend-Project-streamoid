from typing import List, Dict, Any
import pandas as pd
import re

class ValidatorService:
    @staticmethod
    def validate_row(row: Dict[str, Any], mapping_rules: Dict[str, str], template_schema: Dict[str, Any]) -> List[str]:
        errors = []
        
        for template_attr, rules in template_schema.items():
            # Get the mapped column name from the seller file
            seller_col = mapping_rules.get(template_attr)
            
            # If not mapped, check if required
            if not seller_col:
                # Assuming all attributes in the template schema are required for this exercise
                # or we check a specific 'required' flag if the schema was more complex.
                # Based on test.md examples, "Required attributes", so all listed are required.
                errors.append(f"Missing mapping for required attribute: {template_attr}")
                continue

            value = row.get(seller_col)

            # 1. Required Check (Empty check)
            if value is None or value == "" or pd.isna(value):
                errors.append(f"Attribute '{template_attr}' is required but value is empty.")
                continue

            # 2. Type & Constraint Checks
            attr_type = rules.get("type", "string")

            # String constraints
            if attr_type == "string":
                max_len = rules.get("max_length")
                if max_len and len(str(value)) > max_len:
                    errors.append(f"'{template_attr}' exceeds max length of {max_len}.")
                
                # Enum check
                allowed_values = rules.get("enum")
                if allowed_values and str(value) not in allowed_values:
                     errors.append(f"'{template_attr}' value '{value}' is not in allowed values: {allowed_values}.")

            # Number constraints
            elif attr_type in ["number", "integer"]:
                try:
                    num_val = float(value)
                    msg_label = "Integer" if attr_type == "integer" and not num_val.is_integer() else None
                    if msg_label:
                         errors.append(f"'{template_attr}' must be an integer.")

                    min_val = rules.get("min")
                    if min_val is not None and num_val < min_val:
                         errors.append(f"'{template_attr}' must be >= {min_val}.")
                    
                    # Logic Check: price <= mrp
                    # This requires access to other fields in the row.
                    # We handle cross-field validation separately or here if we access the whole row.
                except ValueError:
                     errors.append(f"'{template_attr}' must be a valid number.")

        # Cross-field validation (specific logic mentioned in test.md)
        # price <= mrp
        # We need to find which seller cols map to 'price' and 'mrp'
        price_col = mapping_rules.get("price") or mapping_rules.get("listingPrice")
        mrp_col = mapping_rules.get("mrp")
        
        if price_col and mrp_col:
            price_val = row.get(price_col)
            mrp_val = row.get(mrp_col)
            try:
                if price_val is not None and mrp_val is not None:
                     if float(price_val) > float(mrp_val):
                         errors.append(f"Price ({price_val}) cannot be greater than MRP ({mrp_val}).")
            except:
                pass # Already caught in type checks

        return errors

    @staticmethod
    def validate_dataframe(df: pd.DataFrame, mapping_rules: Dict[str, str], template_schema: Dict[str, Any]):
        total = len(df)
        valid_count = 0
        invalid_rows = []

        # Convert to dict records for easier iteration
        records = df.to_dict(orient='records')
        
        for idx, row in enumerate(records):
            errors = ValidatorService.validate_row(row, mapping_rules, template_schema)
            if not errors:
                valid_count += 1
            else:
                invalid_rows.append({
                    "row_index": idx,
                    "data": {k: v for k, v in row.items() if pd.notnull(v)}, # Clean NaNs
                    "errors": errors,
                    "is_valid": False
                })

        return {
            "total_rows": total,
            "valid_rows": valid_count,
            "invalid_rows_count": len(invalid_rows),
            "sample_invalid_rows": invalid_rows[:10] # Limit sample size
        }
