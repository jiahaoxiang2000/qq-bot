# qq bot

This project is for create the qq bot to manage the qq group service.

## architecture

we use to use the bot to manage *group*, but the office bot need the company register, not open to personal. So here we use the [NapCatQQ](https://napneko.github.io/) to open the `websocket` ability by hook the node function. then use the [NcatBot](https://docs.ncatbot.xyz/) to call the all function by the `websocket`.
