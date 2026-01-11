"""
Voice Agent - Voice-to-Clipboard Tool

Launch the GUI application.
Use --cli flag for command-line mode.
"""

import sys


def main():
    """Entry point."""
    # Check for CLI flag
    if "--cli" in sys.argv:
        from cli import run_cli
        run_cli()
    else:
        from ui.app import VoiceAgentApp
        app = VoiceAgentApp()
        app.run()


if __name__ == "__main__":
    main()
