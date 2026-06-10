# AntiSpamBot

A Telegram bot for detecting and managing spam messages in group chats using string similarity analysis.

## Features

- **Smart Spam Detection**: Uses string similarity to detect spam patterns (77% threshold)
- **Admin Controls**: Add, view, and manage spam patterns per group
- **User Blocking**: Automatically block repeat spammers and first-time violators
- **Admin Reactions**: React with 👎 to flagged messages to manually block users
- **Trustworthiness Tracking**: Message count per user shows engagement level
- **Auto-Cleanup**: Admin commands auto-delete after 60 seconds
- **Multi-Group Support**: Separate spam databases per group

## Quick Start

### Prerequisites
- Python 3.8+
- Telegram bot token from [@BotFather](https://t.me/botfather)

### Installation

```bash
# Clone the repository
git clone https://github.com/G3rkul3s/AntiSpamBot.git
cd AntiSpamBot

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your TELEGRAM_TOKEN
```

### Running the Bot

```bash
python bot.py
```

## Commands

All commands are **admin-only** (non-admins: silently ignored).

### `/help`
Show help message with all available commands.

### `/addspam <message>`
Add a spam pattern to the group's database.

**Examples:**
```
/addspam Buy cheap products now!
/addspam Click here for free money
```

**Reply Usage:**
Reply to any message with `/addspam` to add that message as a pattern:
```
[Admin replies to spam message with: /addspam]
```

### `/spamlist`
Show all spam patterns currently in the group's database with their IDs.

Output example:
```
Spam patterns in this group:
1. Buy cheap products now!
2. Click here for free money
3. Get rich quick scheme
```

### `/clearspam <id>`
Remove a spam pattern by its ID (shown in `/spamlist`).

**Example:** `/clearspam 2` removes pattern ID 2

### `/unblock <user_id>`
Unblock a previously blocked user so they can post messages again.

**Example:** `/unblock 123456789`

### `/start`
Show welcome message.

## How It Works

### Spam Detection Process

1. **Admin Adds Pattern**: Use `/addspam` to teach the bot what spam looks like
2. **Message Check**: When users post, the bot analyzes the message
3. **Similarity Match**: Compares new messages to stored patterns
4. **Action Taken**:
   - **First-time spam** (new user): Delete message, block user, notify admins
   - **Repeat spam** (known user): Flag with 👎 emoji

### User Trustworthiness

The bot tracks message count per user per group:
- **Count = 0**: New user (first message is spam = permanent block)
- **Count > 0**: Established user (spam = flagged with 👎)
- Admins can use `/unblock` to restore flagged users

### Admin Emoji Reactions

When the bot flags spam with 👎:
1. Admin can react to that flagged message with 👎
2. Bot detects admin's reaction
3. User is immediately blocked and reported
4. Flagged message is deleted

## Configuration

Edit `config.py` to customize:

| Setting | Default | Description |
|---------|---------|-------------|
| `SIMILARITY_THRESHOLD` | 0.77 | Spam detection sensitivity (0.0-1.0) |
| `COMMAND_AUTO_DELETE_SECONDS` | 60 | How long before admin commands auto-delete |
| `SPAM_FLAG_EMOJI` | 👎 | Emoji used to flag repeat spam |

## Database

SQLite database (`spam_db.sqlite`) contains three tables:

| Table | Purpose |
|-------|---------|
| `spam_patterns` | Spam templates per group |
| `user_messages` | Message count and block status per user per group |
| `admin_logs` | Log of all admin actions |
| `flagged_messages` | Track which user sent each flagged message |

## Permissions Required

The bot needs these permissions in groups:
- ✅ Send messages
- ✅ Delete messages
- ✅ Read message history
- ✅ Set message reactions (for flagging)

## Example Workflow

```
1. Admin in group: /addspam "Buy cheap crypto!"
   → Bot stores pattern and deletes command

2. User sends: "Buy cheap crypto now!"
   → Bot detects match (90% similarity)
   → First time? Block user and report
   → Repeat spammer? Flag with 👎

3. Admin sees 👎 on message
   → Admin reacts with 👎
   → Bot blocks that user and deletes message

4. To unblock: /unblock <user_id>
   → User can post again
```

## Similarity Threshold

The default **77% threshold** catches:
- ✅ Exact matches: "Buy cheap crypto!"
- ✅ Typos: "Bey cheap crypto!" (96%)
- ✅ Different case: "BUY CHEAP CRYPTO!" (100%)
- ❌ Different message: "Buy something else" (30%)

Adjust `SIMILARITY_THRESHOLD` in `config.py` to be more/less strict.

## Troubleshooting

### Bot doesn't delete messages
- Check bot has "Delete Messages" permission in group settings
- Verify bot is group admin

### Reactions not showing
- Some Telegram clients cache reactions
- Try refreshing the message
- Ensure bot has "Set Message Reactions" permission

### No spam detection happening
- Verify spam patterns are added: `/spamlist`
- Check similarity threshold isn't too high
- Ensure messages are long enough (very short messages get high match rates)

### Database errors
- Delete `spam_db.sqlite` to reset (will lose all data)
- Bot recreates database automatically on next run

## Development

### Project Structure
```
AntiSpamBot/
├── bot.py              (Main bot with handlers)
├── db.py               (SQLite database layer)
├── similarity.py       (String similarity engine)
├── config.py           (Configuration constants)
├── requirements.txt    (Python dependencies)
├── .env.example        (Environment template)
├── README.md           (This file)
└── spam_db.sqlite      (SQLite database - created at runtime)
```

### Adding Features
To add new functionality:
1. Add database functions to `db.py`
2. Add command handler to `bot.py`
3. Register handler in `main()` function
4. Add tests in group chat
