# qq bot

This project is for create the qq bot to manage the qq group service.

## architecture

we use to use the bot to manage *group*, but the office bot need the company register, not open to personal. So here we use the [NapCatQQ](https://napneko.github.io/) to open the `websocket` ability by hook the node function. then use the [NcatBot](https://docs.ncatbot.xyz/) to call the all function by the `websocket`.

## Development

### Prerequisites

1. Install Python 3.7+ and pip
2. Install required packages: `pip install -r requirements.txt`
3. Set up [NapCatQQ](https://napneko.github.io/) and make sure it's running

### Environment Variables

Create a `.env` file in the project root with the following variables:

``` env
BOT_UIN=your_bot_qq_number
WS_URI=ws://localhost:3001
BOT_TOKEN=your_napcat_token
```

### Running the Bot

Basic run:

```bash
python main.py
```

### Hot Reloading

For development with hot reloading, install `watchdog`:

```bash
pip install watchdog
```

Run the bot with hot reloading:

```bash
python run_dev.py
```

This will automatically restart the bot whenever you make changes to the code.
