# ChatEcho

ChatEcho is a Python-based voice chat application that leverages voice-to-text and text-to-speech technologies to create a seamless conversational AI experience.

## Features

- **Voice-to-Text:** Converts your speech into text using advanced speech recognition.
- **Text-to-Speech:** Vocalizes the AI's responses, providing a natural-sounding voice.
- **Interactive Chat:** Engage in real-time conversations with an AI assistant.
- **Modular Design:** The project is structured into reusable modules for easy maintenance and extension.

## Getting Started

### Prerequisites

- Python 3.7+
- `pip` for package management

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/ChatEcho.git
    cd ChatEcho
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    # For Windows
    python -m venv .venv
    .venv\Scripts\activate

    # For macOS and Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

To start the ChatEcho application, run the following command:

```bash
python main.py
```

Press `Enter` to start recording, and press `Enter` again to stop.

## Project Structure

```
.gitignore
LICENSE
README.md
chatecho/
├── __init__.py
├── audio_config.py
├── cli.py
├── init.py
├── recorder.py
├── sdk.py
├── speech_processor.py
├── streaming.py
└── vad.py
examples/
main.py
requirements.txt
setup.py
tests/
└── __init__.py
```

-   `main.py`: The main entry point of the application.
-   `requirements.txt`: A list of the Python packages required to run the project.
-   `setup.py`: The setup script for packaging and distributing the project.
-   `chatecho/`: The core application package.
    -   `recorder.py`: Handles audio recording.
    -   `speech_processor.py`: Processes the recorded audio.
    -   `vad.py`: Implements Voice Activity Detection (VAD).
    -   `sdk.py`: Provides an SDK for the voice-to-text service.
    -   `init.py`: Initializes the chat functionality.
    -   `audio_config.py`: Contains audio configuration settings.
    -   `cli.py`: Defines the command-line interface.
-   `tests/`: Contains tests for the application.
-   `examples/`: Includes example usage and demos.
-   `.gitignore`: Specifies which files and directories to ignore in version control.
-   `LICENSE`: The license for the project.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue to discuss your ideas.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.