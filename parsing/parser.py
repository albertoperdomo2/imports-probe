from typing import List, Dict, Tuple, Union
import re
import pandas as pd
import plotly.express as px

def parse_line(line: str) -> Tuple:
    """
    Parse a line from the log file and extracts relevant information.
    
    Args:
        line (str): The log line to parse.
        
    Returns:
        Tuple or None: A tuple containing parsed information if successful, or None if parsing fails.
    """
    match = re.match(r'^import time:\s+(\d+) \|\s+(\d+)\s+\|(\s+)(.+)$', line)

    if match:
        t_self_us, t_cumulative_us, indentation, package_name = match.groups()
        return int(t_self_us), int(t_cumulative_us), len(indentation), package_name.strip()

    return None

def build_nested_structure(log_lines: List[str]) -> List[Dict]:
    """
    Parse the log lines and build a nested hierarchical structure.
    
    Args:
        log_lines (List[str]): Lines from the log file.
        
    Returns:
        List[Dict]: A list of dictionaries representing the nested structure.
    """
    nested_structure = []
    stack = []

    for line in log_lines:
        parsed_line = parse_line(line)

        if parsed_line:
            t_self_us, t_cumulative_us, depth, package_name = parsed_line
            current_node = {"name": package_name, "t_self_us": t_self_us, "t_cumulative_us": t_cumulative_us, "depth": depth, "nested": []} 

            if not stack and not nested_structure:
                stack.append(current_node)
                continue
            
            if depth == 1:
               current_node["nested"] = stack 
               nested_structure.append(current_node) 
               stack = []
            else:
                if stack:
                    if stack[-1]["depth"] == depth:
                        stack.append(current_node)

                    elif stack[-1]["depth"] > depth:
                        current_node["nested"] = [stack[-1]]
                        stack[-1] = current_node
                        # XXX: does not work for depth > 3 (abs)

                    elif depth > stack[-1]["depth"]:
                        stack.append(current_node)

                else:
                    stack.append(current_node) 
            
    return nested_structure

def flatten_json(json_data: List[Dict]) -> List[Dict]:
    """
    Flattens a nested/hierarchical JSON into a list of single entries.
    
    Args:
        json_data (List[Dict]): The JSON data with nested structure.
    
    Returns:
        List[Dict]: Flattened data.
    """
    flat_data = []
    for j in json_data:
        parse_entry(j['nested'], j['name'], flat_data)
        flat_data.append({'parent_import': j['name'], 'package': j['name'], 'duration': j['t_self_us']}) 

    return flat_data

def parse_entry(entry: Union[Dict, List[Dict]], parent: str, flat_data: List[Dict]):
    """
    Recursively parse a nested structure.
    
    Args:
        entry (Union[Dict, List[Dict]]): Nested entry to be parsed.
        parent (str): Parent of the nested structure.
        flat_data (List[Dict]): List to store the flattened data.
    """
    if isinstance(entry, dict):
        entry = [entry]

    for element in entry:
        if element['nested']:
            parse_entry(element["nested"], parent, flat_data)
        else:
            flat_data.append({'parent_import': parent, 'package': element['name'], 'duration': element['t_self_us']}) 

def process_file(file: str) -> str:
    """
    Process the log file and generate a bar chart using Plotly Express.
    
    Args:
        file (str): Path to the log file.
        
    Returns:
        str: JSON representation of the Plotly Express bar chart.
    """
    try:
        content = None
        with open(file, 'r') as f:
            content = f.readlines()

        nested_structure = build_nested_structure(content)
        flat_data = flatten_json(nested_structure)

        df = pd.DataFrame(flat_data)
        df['duration'] = df['duration'] * .001 # to ms
        
        fig = px.bar(
            df,
            x="duration", 
            y="parent_import", 
            color="package",
            labels={"parent": "Parent Import", "duration": "Duration (ms)"},
            title="Time required to import a package"
        )
        fig.update_layout(width=1920, height=2160)
           
        chart_json = fig.to_json()
        return chart_json

    except Exception as e:
            return f"Error processing file: {str(e)}"