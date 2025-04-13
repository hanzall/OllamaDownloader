import os
import re
import time
import http.client
import urllib.parse
import subprocess
from math import ceil

# Define the local file to save the downloaded web page
current_dir = os.path.dirname(__file__)
web_page_file = os.path.join(current_dir, "modelListPage.html")

def main():
    # Ask the user whether to load the local HTML or download a new one
    if os.path.exists(web_page_file):
        print("\033[33mLocal model list file found.")
        choice = input("Enter \033[95m'q'\033[33m to quit, \033[95m'd'\033[33m to download a new list, or press \033[95mEnter\033[33m to use the local list (default)\033[0m:")
        if choice.upper() == 'D':
            html_content = get_model_list()
        elif choice == '':
            print("Using the local model list...")
            with open(web_page_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
        elif choice.upper() == 'Q':
            print("Quitting the script.")
            exit(0)
        else:
            print("Invalid choice. Exiting.")
            exit(1)
    else:
        print("No local model list found. Downloading a new list...")
        html_content = get_model_list()

    # Extract models and parameters
    models = extract_models(html_content)
    if not models:
        print("No models found in the HTML content.")
        exit(1)
    
    # Initialize parameters dictionary
    parameters = {}

    # Extract parameters for each model individually
    for model in models:
        parameters[model] = extract_parameters(html_content, model)

    # Get list of local models
    local_result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
    localmodels = []
    if local_result.returncode == 0:
        for line in local_result.stdout.splitlines():
            if line.strip():  # Skip empty lines
                model_name = line.split()[0]  # First column contains model:tag
                localmodels.append(model_name)


    # Clear the screen for better readability
    os.system('cls' if os.name == 'nt' else 'clear')

    while True:
        filter_keyword = input("Enter a \033[92mkeyword\033[0m to filter models (press \033[95mEnter\033[0m to show all, or \033[95m'h'\033[0m for help): ").strip()
        
        if filter_keyword.lower() == 'h':
            showHelp()
            continue  # Prompt the user again after showing help

        # Clear the screen for better readability
        os.system('cls' if os.name == 'nt' else 'clear')
        model_params = display_models(models, parameters, localmodels, filter_keyword if filter_keyword else None)

        if not model_params:
            continue  # Prompt the user to enter a new filter keyword

        print(f"\nTotal models found: {len(model_params)}")


        while True:
            try:
                modelparam_indices = input("Enter the \033[92mnumbers\033[0m of the models you want to download (comma-separated, or enter \033[95m0\033[0m to change the filter): ").strip()
                if modelparam_indices == '0':
                    break  # Go back to filter input
                if not re.match(r'^\d+(,\d+)*$', modelparam_indices):
                    print("Invalid input. Please enter only numbers separated by commas.")
                    continue
                selected_indices = [int(index.strip()) for index in modelparam_indices.split(',')]
                if all(1 <= index <= len(model_params) for index in selected_indices):
                    break
                print(f"\033[91mInvalid selection. Valid range is 1 to {len(model_params)}.\033[0m")
            except ValueError:
                print(f"\033[91mInvalid input. Please enter valid numbers separated by commas.\033[0m")

        if modelparam_indices != '0':
            break  # Exit the loop if valid models are selected

    selected_models = [model_params[index - 1] for index in selected_indices]


    # List the selected models before starting the download
    # print("\n\033[92mSelected models for download:\033[0m")
    print("Selected models for download:")
    columns = 4
    max_length = max(len(model) for model in selected_models)
    col_width = max_length + 5  # Add padding for better readability
    items_per_col = ceil(len(selected_models) / columns)
    for row in range(items_per_col):
        line = ""
        for col in range(columns):
            index = row + (col * items_per_col)
            if index < len(selected_models):
                model = selected_models[index]
                padded_item = f"\033[92m{model:<{col_width}}\033[0m"
                line += padded_item
        print(line.rstrip())
        


    hibernate_choice = input("Do you want to hibernate after the downloads? (Y/N, default: Y): ").strip().upper()
    should_hibernate = hibernate_choice != 'N'

    # Download the selected models one by one
    retry_count = {}
    total_models = len(selected_models)
    while selected_models:
        modelparam_selected = selected_models.pop(0)
        current_model_index = total_models - len(selected_models)
        exec_count = retry_count.get(modelparam_selected, 0) + 1
        retry_count[modelparam_selected] = exec_count

        print(f"Downloading \033[92m{modelparam_selected}\033[0m ({current_model_index}/{total_models}), Attempt: {exec_count}")
        result = subprocess.run(['ollama', 'pull', modelparam_selected])
        
        if result.returncode == 0:
            print(f"Command succeeded for \033[92m{modelparam_selected}\033[0m after {exec_count} attempt(s).")

            print("\nModel details:")
            show_result = subprocess.run(['ollama', 'show', modelparam_selected], capture_output=True, text=True)
            if show_result.returncode == 0:
                print(f"\033[90m{show_result.stdout}\033[0m")
            else:
                print("Failed to show model details.")
        else:
            print(f"\nCommand failed for {modelparam_selected}.")
            if exec_count < 3:
                print("Retrying in 10 seconds...")
                time.sleep(10)  # Wait for 10 seconds before retrying
                print("Retrying now...")
                selected_models.append(modelparam_selected)  # Add to the end of the list for retry
            else:
                print(f"Max retries reached for {modelparam_selected}. Skipping.")

    if should_hibernate:
        print("\nPress Ctrl+C to cancel hibernation...")
        try:
            for i in range(120, 0, -1):
                print(f"\rHibernating in {i} seconds...", end='', flush=True)
                time.sleep(1)
            print("\nHibernating now...")
            if os.name == 'nt':  # Windows
                os.system('shutdown /h')
            else:  # Linux/Unix
                os.system('systemctl hibernate')
        except KeyboardInterrupt:
            print("\nHibernate cancelled.")


def extract_models(html):
    """Extract models from HTML content"""
    model_regex = r'<div x-test-model-title title="([^"]+)"'
    matches = re.findall(model_regex, html)
    return matches

def extract_parameters(html, model):
    """Extract parameters related to each model"""
    escaped_model = re.escape(model)
    # Find the specific <li> element containing this model
    pattern = f'<li[^>]*x-test-model[^>]*>(?:(?!<li[^>]*x-test-model[^>]*>).)*?<div[^>]*title="{escaped_model}".*?</li>'
    model_block = re.search(pattern, html, re.DOTALL)
    
    if model_block:
        # Only search for parameters within this model's block
        param_regex = r'<span[^>]*x-test-size[^>]*>([^<]+)</span>'
        param_matches = re.findall(param_regex, model_block.group())
        
        params = [match.lower().strip() for match in param_matches]
        if params:
            return ",".join(params)
    return "latest"

def get_model_list():
    """Fetch the model list from the website"""
    url = "https://ollama.com/library?sort=newest"
    print(f"Fetching model list from {url}...")
    try:
        parsed_url = urllib.parse.urlparse(url)
        conn = http.client.HTTPSConnection(parsed_url.netloc)
        conn.request("GET", parsed_url.path + "?" + parsed_url.query)
        response = conn.getresponse()
        if response.status != 200:
            raise Exception(f"HTTP error: {response.status} {response.reason}")
        html_content = response.read().decode('utf-8')
        conn.close()
        
        # Save the entire web page to a local file, overwriting if it exists
        with open(web_page_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Web page saved to {web_page_file}.")
        
        return html_content
    except Exception as e:
        print(f"Failed to fetch model list: {e}")
        exit(1)


def display_models(models, parameters, localmodels, filter_keyword=None):
    """
    Display models with each parameter as a separate entry.
    Optionally filter models by a compound expression of model:parameter or by parameter size.
    """
    print("Available models:")
    columns = 4  # Reduced number of columns for better readability

    # Create expanded list with model:parameter combinations
    model_params = []
    unique_models = set()
    model_colors = {}
    # Light colors (foreground)
    color_codes = [32, 92, 96, 95, 94, 91, 35, 34, 95, 36]  # Replaced yellow (33) with blue (34)

    # Parse filter for parameter comparison or equality
    param_filter = None
    if filter_keyword and re.match(r'[<>=]=?\d+(\.\d+)?[kmgb]', filter_keyword.lower()):
        operator = filter_keyword[:2] if filter_keyword[1] in "=<>" else filter_keyword[0]
        value = filter_keyword[len(operator):]
        param_filter = (operator, value)

    def parse_param(param):
        """Convert parameter string like '8b', '700k', '10.5m' to a float for comparison."""
        match = re.match(r'(\d+(\.\d+)?)([kmgb])', param.lower())
        if not match:
            return None
        num, _, unit = match.groups()
        multiplier = {'k': 1_000, 'm': 1_000_000, 'b': 1_000_000_000, 'g': 1_000_000_000}[unit]
        return float(num) * multiplier

    def matches_filter(param):
        """Check if a parameter matches the filter condition."""
        if not param_filter:
            return True
        operator, value = param_filter
        param_value = parse_param(param)
        filter_value = parse_param(value)
        if param_value is None or filter_value is None:
            return False
        if operator == "=":
            return param_value == filter_value
        return eval(f"{param_value} {operator} {filter_value}")

    # First pass to collect all entries
    color_index = 0  # Keep track of color index
    for model in models:
        params = parameters[model].split(',')
        for param in params:
            param = param.strip()
            if param_filter and not matches_filter(param):
                continue  # Skip entries that don't match the filter
            entry = f"{model}:{param}"
            if filter_keyword and not param_filter:
                # Check if the filter matches either the model or parameter
                if filter_keyword.lower() not in entry.lower():
                    continue  # Skip entries that don't match the filter
            model_params.append(entry)
            unique_models.add(model)
            if model not in model_colors:
                # Sequentially assign colors, wrapping around if needed
                model_colors[model] = color_codes[color_index % len(color_codes)]
                color_index += 1

    if not model_params:
        print("\033[91m\nNo models match the filter. Try changing the filter keyword or press Enter to show all models.\n\033[0m")
        return model_params

    print(f"Total number of models: {len(model_params)}\n")
    # Calculate lengths for formatting
    max_length = max(len(entry) for entry in model_params)
    col_width = max_length + 7  # Add space for the index number and padding

    # Calculate items per column
    items_per_col = ceil(len(model_params) / columns)

    # Print vertically
    for row in range(items_per_col):
        line = ""
        for col in range(columns):
            index = row + (col * items_per_col)
            if index < len(model_params):
                entry = model_params[index]
                model, param = entry.split(':')
                # Determine if the model exists locally
                is_local = entry in localmodels
                number = f"{str(index + 1).rjust(3)}."
                if is_local:
                    number = f"\033[93m{number}\033[0m"  # Use yellow color for the number if local

                # Format the item with consistent padding
                item = f"{number} \033[{model_colors[model]}m{model}\033[0m:{param}"
                # Adjust padding to account for ANSI escape sequences
                padded_item = f"{item:<{col_width + 9 + (len(number) - 4 if is_local else 0)}}"
                line += padded_item
        print(line.rstrip())
    print("\n\033[93mNote:\033[0m Models with a \033[93myellow number\033[0m are already available locally.")
    return model_params


def showHelp():
    """Display help information."""
    help_message = (
        "\n\033[92m[HELP]\033[0m\n"
        "\033[94mFiltering Models:\033[0m\n"
        "  - Enter a keyword to filter models by any part of the model name or parameter (e.g., 'model', 'parameter', or size comparison like '>=8b').\n"
        "  - Press Enter to show all models without filtering.\n\n"
        "\033[94mSelecting Models:\033[0m\n"
        "  - Enter the number of the model to download.\n"
        "  - Enter 0 to change the filter and search again.\n\n"
        "\033[94mPost-Download Options:\033[0m\n"
        "  - Use 'Y' or 'N' to decide whether to hibernate after download.\n"
        "  - Press Ctrl+C to cancel hibernation if it was selected.\n"
    )
    print(help_message)




if __name__ == "__main__":

    main()