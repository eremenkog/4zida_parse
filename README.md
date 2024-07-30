# 4zida parse to Telegram posts

Collects property listings to .csv with possibility to send posts to Telegram channel

## Docker
```sh
docker build -t 4zida-bot-image .
docker run -d --name 4zida-bot-container 4zida-bot-image
```

Don't forget to put your credentials in `token.env`
```
export BOT_TOKEN=123456
export CHAT_ID=-123456
```

## Features
- Start or stop your bot with **/start** or **/stop** messages
- Throw random (though, not posted yet) listing with **/random** message
- Upon posting, a timestamp is appended to corresponding listing in .csv file
- By default, collects data in 1hr intervals, excludes duplicates
> Hint: You can hunt for only recent listings, if you set all cells to non-null in "Posted" column upon initial population
- By default, posts in 15min intervals.

## To do
- Also collect data for houses
- Set data collection parameters from Telegram
