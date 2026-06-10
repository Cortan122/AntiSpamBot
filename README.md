# AntiSpamBot

A Telegram bot for detecting and managing spam messages in group chats using semantic similarity analysis.

## Features

- **Admin Controls**: Add spam patterns to a group-specific database
- **Semantic Similarity Detection**: Uses embeddings (sentence-transformers) to detect similar messages (~77% threshold)
- **User Trustworthiness Tracking**: Tracks message count per user per group
- **First-Offender Enforcement**: Deletes spam, blocks users, and reports to admins
- **Repeat Offender Flagging**: Marks repeat spam with 👎 emoji
- **Auto-Cleanup**: Admin commands auto-delete after 60 seconds to keep chats clean

## Setup

### Requirements
- Python 3.8+
- Telegram bot token (get from [@BotFather](https://t.me/botfather))

### Installation

1. Clone the repository:
```bash
git clone https://github.com/G3rkul3s/AntiSpamBot.git
cd AntiSpamBot
```

2. Create `.env` file with your bot token:
```bash
cp .env.example .env
# Edit .env and add your TELEGRAM_TOKEN
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Bot

```bash
python bot.py
```

## Commands

All commands are admin-only (ignored silently if used by non-admins).

### `/addspam <message>`
Add a spam pattern to the group's database.

**Example**: `/addspam Buy cheap products now!`

**Reply usage**: Reply to any message with `/addspam` to add that message as a pattern.

### `/spamlist`
Show all spam patterns currently in the group's database.

### `/clearspam <pattern_id>`
Remove a spam pattern by its ID (from `/spamlist` output).

## How It Works

1. **Admin adds spam patterns**: Use `/addspam` to teach the bot what spam looks like
2. **Bot analyzes messages**: When users post, the bot computes a semantic embedding and compares it to stored patterns
3. **First-time spam**: If similarity > 77%, delete message, block user, and report to admins
4. **Repeat spam**: If a blocked user tries spam again, flag with 👎 emoji
5. **Message tracking**: All non-spam messages increment the user's message count (trustworthiness metric)

## Database

The bot uses SQLite (`spam_db.sqlite`) with three tables:
- `spam_patterns`: Stores spam templates and their embeddings per group
- `user_messages`: Tracks message count and block status per user per group
- `admin_logs`: Logs all admin actions (add/clear spam, block/flag users)

## Configuration

Edit `config.py` to adjust:
- `SIMILARITY_THRESHOLD`: Similarity score threshold (default: 0.77 = 77%)
- `EMBEDDING_MODEL`: Sentence transformer model (default: `all-MiniLM-L6-v2`)
- `COMMAND_AUTO_DELETE_SECONDS`: How long before admin commands auto-delete (default: 60)

## Permissions Required

The bot needs the following permissions in groups:
- Delete messages
- Send messages
- Set message reactions

## Troubleshooting

**Bot doesn't delete spam messages**: 
- Check that the bot has "Delete Messages" permission in the group

**Reactions not showing**:
- Some Telegram clients may not display message reactions immediately

**Database grows large**:
- Consider archiving old `admin_logs` entries periodically (not implemented yet)

## Development

Project structure:
```
├── bot.py           - Main bot with message handlers
├── db.py            - SQLite database layer
├── similarity.py    - Semantic similarity engine
├── config.py        - Configuration constants
├── requirements.txt - Python dependencies
└── spam_db.sqlite   - SQLite database (created at runtime)
```

## License

See LICENSE file in repository.
