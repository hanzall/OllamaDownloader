# Ollama Model Downloader

This script is designed to download models from the Ollama library. It provides a user-friendly interface to filter models based on specific parameters or parts of the model name, select desired models, and download them efficiently. Users can also select multiple models at once for batch downloading, streamlining the process. Additionally, it offers an option to hibernate the system after the download is complete.

## Features

- **Multiple Model Selection for Download**: Users can select multiple models to download by entering their numbers separated by commas, enabling batch downloads for efficiency.
- **Filter Models for Download**: Enter a keyword to filter models by name or parameter, simplifying the selection process for downloading.
- **Select Models to Download**: Choose a model to download from the filtered list.
- **Local Model Detection for Downloads**: Identifies models already available locally to avoid redundant downloads.
- **Retry Mechanism for Downloads**: Automatically retries failed downloads up to three times with a 10-second delay between attempts. Skips the model if retries are exhausted and continues with the next one.
- **Enhanced Download Feedback**: Provides detailed feedback on download status, including the current model being downloaded, number of attempts, and success or failure details.
- **Hibernate Option**: Optionally hibernate the system after downloading, with a countdown to cancel if needed.
- **No External Dependencies for HTTP Requests**: The script now uses Python's built-in `http.client` and `urllib` modules for fetching model lists, eliminating the need for the `requests` library.

## Requirements
- Python 3.x
- `ollama` command-line tool

*Note: The `requests` library is no longer required as the script now uses Python's built-in `http.client` and `urllib` modules for HTTP requests.*

## Preparing the Requirements
### Windows
#### Option 1: Using Git
1. **Install Python**: Download and install Python from the [official website](https://www.python.org/downloads/). Ensure you check the option to add Python to your PATH during installation.
2. **Install Git**: Download and install Git from the [official website](https://git-scm.com/downloads).
3. **Clone the Repository**:
   Open Command Prompt and run:
   ```bash
   git clone https://github.com/hanzall/OllamaDownloader
   cd OllamaDownloader
   ```
   [Go to Usage Section](#usage)

#### Option 2: Without Using Git
1. **Install Python**: Download and install Python from the [official website](https://www.python.org/downloads/). Ensure you check the option to add Python to your PATH during installation.
2. **Download the Repository**:
   - Go to the repository's page on GitHub.
   - Click on the "Code" button and select "Download ZIP".
   - Extract the downloaded ZIP file to a directory of your choice.
3. **Navigate to the Directory**:
   Open Command Prompt and navigate to the extracted directory:
   ```bash
   cd <extracted-directory>
   ```
   [Go to Usage Section](#usage)

### Linux
#### Option 1: Using Git
1. **Install Python**: Most Linux distributions come with Python pre-installed. Verify the installation by running:
   ```bash
   python3 --version
   ```
   If Python is not installed, use your package manager to install it. For example, on Ubuntu:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```
2. **Install Git**: If Git is not installed, use your package manager to install it. For example, on Ubuntu:
   ```bash
   sudo apt install git
   ```
3. **Clone the Repository**:
   Open a terminal and run:
   ```bash
   git clone https://github.com/hanzall/OllamaDownloader
   cd OllamaDownloader
   ```
   [Go to Usage Section](#usage)

#### Option 2: Without Using Git
1. **Install Python**: Verify Python installation as described above. If needed, install it using your package manager.
2. **Download the Repository**:
   - Go to the repository's page on GitHub.
   - Click on the "Code" button and select "Download ZIP".
   - Extract the downloaded ZIP file to a directory of your choice.
3. **Navigate to the Directory**:
   Open a terminal and navigate to the extracted directory:
   ```bash
   cd <extracted-directory>
   ```
   [Go to Usage Section](#usage)

## Usage
1. **Run the Script**:
   Open Command Prompt in the project directory and execute:
   ```bash
   python downloadModel.py
   ```
2. **Follow Instructions**:
   - Enter a keyword to filter models or press Enter to list all models.
   - Select a model by entering its number.
   - Choose whether to hibernate after the download.

## Creating an Executable
To create an executable from the Python script, you can use `PyInstaller`:

1. **Install PyInstaller**:
   ```bash
   pip install pyinstaller
   ```
2. **Create the Executable**:
   Run the following command in the project directory:
   ```bash
   pyinstaller --onefile downloadModel.py
   ```
3. **Locate the Executable**:
   The executable will be located in the `dist` directory.

## Notes
- Ensure the `ollama` command-line tool is installed and configured on your system.
- The script saves the downloaded web page to `modelListPage.html` in the current directory.
- Use Ctrl+C to cancel hibernation if selected.

## Script Functionality

The Ollama Model Downloader script automates the process of downloading models from the Ollama library. Here's how it works:

1. **Downloading Models**:
   - The script can download a list of models from the Ollama library website. It fetches the latest model list from the URL `https://ollama.com/library?sort=newest`.
   - If a local copy of the model list (`modelListPage.html`) exists, the script will prompt the user to use the local list or download a new one.

2. **Saving Locally**:
   - The downloaded HTML content of the model list is saved locally as `modelListPage.html` in the current directory.
   - This allows the script to use the local file for subsequent operations, reducing the need for repeated downloads.

3. **Using the Model List**:
   - The script beautifully displays models with a number next to them, making it easy to identify and select models.
   - Users can filter models by entering keywords or parameters, and the script will display matching models.
   - Users can select a model to download by entering its corresponding number from the displayed list.

4. **Local Model Detection**:
   - The script checks for models already available locally using the `ollama list` command.
   - Models that are already downloaded are highlighted in the list, helping users avoid redundant downloads.

5. **Model Selection and Download Management**:
   - Users can manage downloading models by selecting from the list of available models displayed by the script.
   - The script ensures that only models available in the Ollama library are presented for download.

6. **Sequential Model Downloading**:
   - Models are downloaded one by one, ensuring that each download is completed before starting the next.
   - This approach helps manage system resources effectively and provides clear feedback for each model's download status.

7. **Handling Download Interruptions**:
   - If the download process is interrupted, the script automatically retries the download until it succeeds.
   - This ensures a reliable download process, even in the face of network issues or other interruptions.

8. **Post-Download Options**:
   - After downloading a model, users can choose to hibernate the system.
   - The script provides a countdown before hibernation, allowing users to cancel if needed.

This script is particularly useful for managing and downloading large sets of models efficiently, with options to customize the download process and manage local storage.

## Ollama Command-Line Tool

The Ollama Model Downloader script requires the `ollama` command-line tool to function correctly. This tool is used to list and download models from the Ollama library.

### Installing Ollama
1. **Download Ollama**: Visit the [Ollama website](https://ollama.com/download) to download the appropriate version for your operating system.
2. **Install Ollama**: Follow the installation instructions provided on the website to install the tool on your system.
3. **Verify Installation**: Open a terminal or command prompt and run the following command to ensure Ollama is installed correctly:
   ```bash
   ollama --version
   ```
   This should display the installed version of Ollama.

### Configuration
- Ensure that the `ollama` command is accessible from your terminal or command prompt. You may need to add it to your system's PATH if it's not automatically configured.

The Ollama tool is essential for interacting with the model library, allowing the script to list available models and manage downloads efficiently. 


## Screenshots

Here are some screenshots showcasing the functionality of the Ollama Model Downloader:

### 1. Local Model Detection
The script displays a list of models fetched from the Ollama library. If a local copy of the model list exists from a previous execution, the script will prompt the user to use the saved list or download a new one. This feature helps reduce redundant downloads and speeds up the process.

![Model List Display](https://github.com/user-attachments/assets/c98440b3-d313-469e-bccf-350e5d03b0a5)

### 2. Filtered Model List
Users can filter their search by inputting keywords and comparison operators, making it easier to locate specific models. For example, in the image below, the user narrows down the list to models with less than 8 billion parameters by entering "<8b".
Models already available locally are highlighted, allowing users to avoid redundant downloads.

![Filtered Model List](https://github.com/user-attachments/assets/f8e4a366-0bf4-4a96-8926-79e3aa30d81b)

### 3. Multiple Download Choices
The script allows users to select multiple models for batch downloading. It provides detailed feedback during the process, including the current model being downloaded, the number of attempts, and the overall progress.
Before starting the download, the script highlights the models selected for download in green, providing a clear visual indication of the models being processed. This helps users confirm their selections before the download begins.

![Multiple Download Choices](https://github.com/user-attachments/assets/66552d12-2511-46e0-b004-abec9d0bc7a6)

### 4. Download Progress and Completion Details
Once the download starts, the script provides detailed feedback, including the current model being downloaded, the number of attempts, and the overall progress.
After each model is downloaded, the script provides detailed feedback, including the model's name, size, and other information retrieved from the Ollama command-line tool. This ensures users have a clear understanding of the process and results.

![Download Progress](https://github.com/user-attachments/assets/a1f29cd9-c30f-4eea-93c6-978adc120f3c)

### 5. Hibernate Option
If the hibernate option was enabled in the previous steps, users can cancel it during the countdown provided after the downloads are completed.

![Hibernate Option](https://github.com/user-attachments/assets/783a93d4-226c-401b-954e-afbc7eacde35)

## License
This project is licensed under the MIT License.
