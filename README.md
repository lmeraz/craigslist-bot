# this is a bot there are many like it but this one is mine

this currently only works by running docker-compose

attempting docker run and mounting volumes fails :(

create a .env file with SLACK_API_TOKEN

i'd like to be able to run the image with:
`docker run craigslist-bot --env CONFIG_NAME=config_name --env-file ENV_FILE_PATH -v config_path:config_path`

but open to how to best store configs
