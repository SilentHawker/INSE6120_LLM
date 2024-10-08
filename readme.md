#  Setup Guide

This guide will walk you through setting up the environment to run the project using Python and Ollama.

## Step 1: Clone the Repository

First, you need to get the project files onto your computer by either cloning or downloading the repository.

### Cloning (if you're using Git)
1. Open your terminal (or command prompt on Windows).
2. Run the following command to clone the repository:

    ```bash
    git clone <repository-url>
    ```

   Replace `<repository-url>` with the actual URL of the repository you are cloning (you can get this from GitHub).

3. Navigate to the project folder by running:

    ```bash
    cd /path/to/your/project-directory
    ```

### Downloading (if you prefer not to use Git)
1. Download the ZIP file from the repository's webpage (typically by clicking the "Download ZIP" button).
2. Extract the ZIP file.
3. Open your terminal and navigate to the extracted folder:

    ```bash
    cd /path/to/your/project-directory
    ```

---

## Step 2: Download and Install Python 3.8.8

You need to have Python 3.8.8 installed. Follow these steps to get it:

### For Windows:
1. Go to the [Python 3.8.8 download page](https://www.python.org/downloads/release/python-388/).
2. Download the correct installer for your system (most likely the "Windows x86-64 executable installer").
3. Run the installer and **make sure to check the box that says "Add Python to PATH"** before clicking "Install Now."

### For macOS/Linux:
1. macOS: Use [Homebrew](https://brew.sh/) if you have it. Run `brew install python@3.8`.
2. Linux: You can install Python 3.8.8 using your package manager. For Ubuntu, run:

   ```bash
   sudo apt update
   sudo apt install python3.8
    ```
You can verify the installation by typing the following command in your terminal:
 ```bash
   python --version
   ```
## Step 3: Install Ollama

Ollama is the tool that will allow you to interact with the LLM (language model).

1. Go to the official [Ollama installation page](https://ollama.com/) and download the version compatible with your operating system (Windows/macOS/Linux).
2. Once the download is complete, follow the instructions to install it on your machine.

## Step 4: Verify Ollama Installation

After installation, ensure Ollama is running properly by checking its local server.

1. Open your terminal and type:
```bash
ollama --help
```
2. To check if Ollama is running, visit http://localhost:11434/ in your web browser. If you see a message saying "Ollama is running", you are all set to continue.

## Step 5: Download the Model (Llama 3.2)

You need to download the specific language model, Llama 3.2.

1. Open your terminal and type the following command to pull the Llama 3.2 model:
```bash
ollama pull llama3.2
```

## Step 6: Set Up the Virtual Environment

Now, let's set up a virtual environment to keep the project dependencies isolated.

1. Navigate to the root folder of the repository using the terminal:
```bash
cd <your_project_folder>
```
2. Create a virtual environment:
```bash
python -m venv venv
```
3. Activate the virtual environment:

On Windows:
```bash
venv\Scripts\activate
```
On macOS/Linux:
```bash
source venv/bin/activate
```

## Step 7: Install Dependencies

After activating the virtual environment, install the required dependencies by running the following command:
```bash
pip install -r requirements.txt
```

## Step 8: Start the Program

At this point, you have everything set up! You can now start the program using :

```bash
python main.py
```
