# Discord Bot

A Discord bot with music playback (YouTube) and utility commands.

## Setup

### 1. Requirements
- Python 3.10+
- FFmpeg installed on your system
  - **Windows**: Download from https://ffmpeg.org/download.html and add to PATH
  - **Linux**: `sudo apt install ffmpeg`
  - **Mac**: `brew install ffmpeg`

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure your token
Copy `.env.example` to `.env` and fill in your bot token:
```bash
cp .env.example .env
```
Then open `.env` and replace `your_bot_token_here` with your actual token from https://discord.com/developers/applications

### 4. Run the bot
```bash
python bot.py
```

---

## Commands

### 🎵 Music
| Command | Description |
|---|---|
| `!join` | Join your voice channel |
| `!play <query>` | Play a YouTube song by title or URL |
| `!pause` | Pause playback |
| `!resume` | Resume playback |
| `!skip` | Skip the current song |
| `!stop` | Stop and disconnect |
| `!queue` | Show the song queue |
| `!volume <1-100>` | Set playback volume |

### 🛠️ Utility
| Command | Description |
|---|---|
| `!ping` | Check bot latency |
| `!serverinfo` | Show server details |
| `!userinfo [@user]` | Show user details |
| `!avatar [@user]` | Show a user's avatar |
| `!poll Question \| Opt1 \| Opt2` | Create a reaction poll |
| `!say <message>` | Bot repeats your message |
| `!clear <n>` | Delete last n messages (requires Manage Messages) |
| `!invite` | Get the bot's invite link |

---

## Getting a Bot Token

1. Go to https://discord.com/developers/applications
2. Click **New Application** → give it a name
3. Go to **Bot** → click **Add Bot**
4. Under **Token**, click **Copy**
5. Paste it into your `.env` file
6. Under **Privileged Gateway Intents**, enable:
   - **Message Content Intent**
   - **Server Members Intent**

## Project Structure
```
discord_bot/
├── bot.py           # Entry point
├── requirements.txt
├── .env             # Your token (never share this!)
├── .env.example
└── cogs/
    ├── music.py     # Music commands
    └── utility.py   # Utility commands
```
