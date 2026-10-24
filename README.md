# DeckFlow Demo

DeckFlow is a React Native/Expo, AI-assisted trading-card pre-grading concept for Game Citi TCG. The same frontend runs as a phone app and in a MacBook web browser. This demo follows the workflow in `Docs/design.md`: capture the front and back, validate the images, confirm a supported card, generate an unofficial pre-grade, display cached market information, and save the report to session history.

This is a CPSC 490 demonstration, not a professional grading service. Camera capture, uploads, validation, computer-vision measurements, the API, error handling, and session history are working software. Automatic card recognition and a trained grading model are future components.

## Requirements

- Docker Desktop 4.x or newer
- macOS, Windows, or Linux
- About 1 GB of free disk space for the first container build
- No API key is required for grading; a JustTCG key is optional for live prices

The containers use Python 3.12, Node.js 22, Expo SDK 58, and React Native 0.88. Docker handles these versions and dependencies automatically.

## Clone and run

```bash
git clone https://github.com/raulmunoz0711/DeckFlow.git
cd DeckFlow
docker compose up --build
docker compose exec backend python sync_catalog.py --languages en ja
```

After both services start and cards finish indexing, open:

```text
http://localhost:5173
```

After the demo is over:
```End
docker compose down
```

Not yet implemented:

- Automatic card identification
- A trained machine-learning grade predictor validated against PSA/CGC labels
- Scratch detection under controlled angled lighting
- Automatic card identification from unrestricted cards

These mocked components are the next development targets. They are clearly separated in the backend so each can be replaced without changing the user flow.
