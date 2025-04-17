import os
import re
import time
import http.client
import urllib.parse
import subprocess
from math import ceil
import sys


# Determine the base directory
if getattr(sys, 'frozen', False):
    # If the application is frozen (running as an executable)
    current_dir = os.path.dirname(sys.executable)
else:
    # If the application is running as a script
    current_dir = os.path.dirname(__file__)

# Define the local file to save the downloaded web page
web_page_file = os.path.join(current_dir, "modelListPage.html")

def select_models(model_params):
    """Prompt user to select models by index from model_params."""
    while True:
        try:
            modelparam_indices = input("Enter the comma-separated \033[92mnumbers\033[0m corresponding to the models you wish to download (or enter \033[95m0\033[0m to change the filter, or \033[95ma\033[0m to select all): ").strip()
            if modelparam_indices.lower() == 'a':
                return model_params
            if modelparam_indices in ['0', '']:
                return None  # Signal to change filter
            if not re.match(r'^\d+(,\d+)*$', modelparam_indices):
                print("Invalid input. Please enter only numbers separated by commas, 'a' to select all, or 0 to change the filter.")
                continue
            selected_indices = [int(index.strip()) for index in modelparam_indices.split(',')]
            if all(1 <= index <= len(model_params) for index in selected_indices):
                return [model_params[index - 1] for index in selected_indices]
            print(f"\033[91mInvalid selection. Valid range is 1 to {len(model_params)}.\033[0m")
        except ValueError:
            print(f"\033[91mInvalid input. Please enter valid numbers separated by commas.\033[0m")

def confirm_models(selected_models, descriptions):
    """Show selected models and ask for confirmation or reselection."""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n\033[1mConfirm Selected Models:\033[0m")
        for i, model in enumerate(selected_models, 1):
            base_model = model.split(':')[0]
            desc = descriptions.get(base_model, "No description available")
            print(f"\n{i}. \033[92m{model}\033[0m")
            print(f"   \033[90m{desc}\033[0m")
        print("\n\033[94mOptions:\033[0m")
        print("  \033[92m[Y]\033[0m - Confirm and start download (default)")
        print("  \033[93m[N]\033[0m - Select different models")
        print("  \033[91m[F]\033[0m - Change filter and search again")
        confirm = input("\nYour choice (Y/N/F, default: Y): ").strip().upper()
        if confirm == '' or confirm == 'Y':
            return 'confirm'
        elif confirm == 'N':
            return 'reselect'
        elif confirm == 'F':
            return 'filter'
        else:
            print("\n\033[91mInvalid input. Please enter Y, N, or F.\033[0m")
            time.sleep(1)

def extract_model_data(html_content):
    """Extract models, parameters and descriptions from HTML content"""
    models = extract_models(html_content)
    parameters = {}
    descriptions = {}
    if models:
        for model in models:
            parameters[model] = extract_parameters(html_content, model)
            descriptions[model] = extract_description(html_content, model)
    return models, parameters, descriptions

def main():

    # Initialize variables
    parameters = {}
    descriptions = {}

    if os.path.exists(web_page_file):
        print("\033[33mLocal model list found. Loading local list...")
        try:
            # First load the local model list
            with open(web_page_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            # Extract data from local file
            models, parameters, descriptions = extract_model_data(html_content)
        except Exception as e:
            print(f"\033[91mError reading local model list: {e}\033[0m")
            print("Downloading a fresh list...")
            html_content = get_model_list()
            models, parameters, descriptions = extract_model_data(html_content)
        else:
            # Ask the user whether to load the local HTML or download a new one
            choice = input("Press \033[95mEnter\033[33m to continue with your local list (default) or enter \033[95m'd'\033[33m to download a fresh list: ")
            if choice.upper() == 'D':
                html_content = get_model_list()
                models, parameters, descriptions = extract_model_data(html_content)
            elif choice != '':
                print("Invalid choice. Exiting.")
                exit(1)
    else:
        print("No local model list found. Downloading a new list...")
        html_content = get_model_list()
        models, parameters, descriptions = extract_model_data(html_content)

    if not models:
        print("No models found in the HTML content.")
        exit(1)

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
        model_params = display_models(models, parameters, localmodels, descriptions, filter_keyword if filter_keyword else None)

        if not model_params:
            continue  # Prompt the user to enter a new filter keyword

        print(f"\nTotal models found: {len(model_params)}")

        while True:
            selected_models = select_models(model_params)
            if selected_models is None:
                break  # User wants to change filter
            while True:
                action = confirm_models(selected_models, descriptions)
                if action == 'confirm':
                    hibernate_choice = input("Do you want to hibernate after the downloads? (Y/N, default: Y): ").strip().upper()
                    should_hibernate = hibernate_choice == '' or hibernate_choice != 'N'

                    # Infinite loop to retry models
                    retry_count = {}
                    total_models = len(selected_models)

                    def check_internet():
                        """Check internet connectivity by trying to connect to ollama.com"""
                        try:
                            # conn = http.client.HTTPSConnection("ollama.com", timeout=5)
                            conn = http.client.HTTPSConnection("registry.ollama.ai", timeout=5)
                            conn.request("HEAD", "/")
                            return conn.getresponse().status == 200
                        except:
                            return False

                    while selected_models:  # Keep going until all models are processed
                        modelparam_selected = selected_models[0]  # Always work on the first model in the list
                        current_model_index = total_models - len(selected_models) + 1
                        exec_count = retry_count.get(modelparam_selected, 0) + 1
                        retry_count[modelparam_selected] = exec_count

                        print(f"Downloading \033[92m{modelparam_selected}\033[0m ({current_model_index}/{total_models}), Attempt: {exec_count}")
                        result = subprocess.run(['ollama', 'pull', modelparam_selected])

                        if result.returncode == 0:
                            print(f"\033[92m{modelparam_selected}\033[0m downloaded successfully in {exec_count} attempt(s).")

                            print("\nModel details:")
                            show_result = subprocess.run(['ollama', 'show', modelparam_selected], capture_output=True, text=True)
                            if show_result.returncode == 0:
                                print(f"\033[90m{show_result.stdout}\033[0m")
                            else:
                                print("Failed to show model details.")

                            selected_models.pop(0)  # Remove the successfully downloaded model
                            retry_count.pop(modelparam_selected, None)  # Clear retry count
                            
                            if selected_models:
                                print(f"\nMoving to next model. {len(selected_models)} models remaining.")
                        else:
                            print(f"\nDownload interrupted for {modelparam_selected}.")
                            if not check_internet():
                                print("Internet connection lost. Waiting for restoration...")
                                while not check_internet():
                                    print("Waiting for internet connection...", end='\r')
                                    time.sleep(5)
                                print("\nInternet connection restored. Retrying...")
                            else:
                                print("Failure not related to internet connection.")
                                if exec_count >= 3:
                                    print(f"Moving {modelparam_selected} to end of queue after 3 failed attempts.")
                                    selected_models.pop(0)  # Remove from front
                                    selected_models.append(modelparam_selected)  # Add to end
                                time.sleep(5)  # Wait before retry

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
                    # Ask the user if they want to download another model
                    another_choice = input("\nDo you want to download another model? (Y/N, default: Y): ").strip().upper()
                    if another_choice == '' or another_choice == 'Y':
                        main()  # Restart the main process to allow downloading another model
                    else:
                        print("Exiting the script. Goodbye!")
                    return  # Exit after download
                elif action == 'reselect':
                    selected_models = select_models(model_params)
                    if selected_models is None:
                        break  # User wants to change filter
                elif action == 'filter':
                    break  # Go back to filter selection
            if selected_models is None or action == 'filter':
                break

def extract_models(html):
    """Extract models from HTML content"""
    model_regex = r'<div x-test-model-title title="([^"]+)"'
    matches = re.findall(model_regex, html)
    return matches

def extract_description(html, model):
    """Extract description for a specific model"""
    escaped_model = re.escape(model)
    # Find the specific <li> element containing this model
    pattern = f'<li[^>]*x-test-model[^>]*>(?:(?!<li[^>]*x-test-model[^>]*>).)*?<div[^>]*title="{escaped_model}".*?</li>'
    model_block = re.search(pattern, html, re.DOTALL)
    
    if model_block:
        # Look for the description paragraph with specific classes that follows the title
        desc_regex = r'<p class="max-w-lg[^"]*break-words text-neutral-800[^"]*">(.*?)</p>'
        desc_match = re.search(desc_regex, model_block.group(), re.DOTALL)
        if desc_match:
            description = desc_match.group(1)
            # Remove HTML tags if any remain
            description = re.sub(r'<[^>]+>', '', description)
            # Clean up whitespace
            description = ' '.join(description.split())
            return description
    return "No description available"

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


def display_models(models, parameters, localmodels, descriptions, filter_keyword=None):
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
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        input("Press Enter to close the program...")