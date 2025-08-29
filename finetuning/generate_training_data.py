import json
import pandas as pd

def generate_conversation_from_excel(file_path):
    """
    Reads an Excel file, combines data from specific columns, and returns
    a dictionary in a conversational format.

    Args:
        file_path (str): The path to the Excel file.
        prompt_prefix (str): A string to prepend to the 'problem' content.

    Returns:
        dict: A dictionary with a list of conversations.
              Example: {"conversations": [{"role": "user", "content": ...}, ...]}
    """

    try:
        df = pd.read_excel(file_path)

        required_columns = ["feature_name", "feature_description", "feature_type", "compliance_status", "reasoning"]
        if not all(col in df.columns for col in required_columns):
            print(f"Error: The Excel file must contain the following columns: {required_columns}")
            return {"conversations": []}

        conversations = []

        for index, row in df.iterrows():
            feature_name = row["feature_name"]
            feature_description = row["feature_description"]

            prompt = f"""
/no_think
You are an AI-powered geo-regulation checker. Your task is to analyze 
the provided context to determine if a feature requires geo-specific compliance actions to meet legal requirement. 
If the feature is business driven, select 'No Compliance Logic Needed'. If uncertain, select 'Requires Further Review'. 
Only use the information provided in the context to make your determination. 
Your final answer MUST be in the specified JSON format.
\n\n
---EXAMPLES---
'Feature reads user location to enforce France's copyright rules (download blocking)' - 'Compliance Logic Needed'
'Geofences feature rollout in US for market testing' - 'No Compliance Logic Needed' (Business decision, not regulatory)'
'A video filter feature is available globally except KR' - 'Requires Further Review' (didn't specify the intention, need human evaluation)
---CONTEXT---
\n\n
---USER QUESTION---
Here is the feature and feature description to validate:
{feature_name}, {feature_description}
\n\n
"""

            problem_content = prompt
            solution_content = {
                "feature_type": row["feature_type"],
                "compliance_status": row["compliance_status"],
                # "supporting_regulations": row["supporting_regulations"],
                "reasoning": row["reasoning"]
            }

            # Create the conversation pair as a list of dictionaries.
            conversation_pair = [
                {"role": "user", "content": problem_content},
                {"role": "assistant", "content": json.dumps(solution_content)}
            ]

            # Append the conversation pair to the list.
            conversations.append(conversation_pair)

        # Return the final dictionary.
        return {"conversations": conversations}

    except FileNotFoundError:
        print(f"Error: The file at path '{file_path}' was not found.")
        return {"conversations": []}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"conversations": []}

# --- Example Usage ---

excel_file_path = "data/synthetic_feature_data100.xlsx"

result = generate_conversation_from_excel(excel_file_path)

print(result)

output_json_file_path = "data/conversations_output.json"

if result["conversations"]:
    try:
        with open(output_json_file_path, 'w') as json_file:
            json.dump(result, json_file, indent=4)
        print(f"Successfully saved conversation data to '{output_json_file_path}'")
    except Exception as e:
        print(f"An error occurred while saving the file: {e}")
else:
    print("No conversations were generated. Nothing to save.")
