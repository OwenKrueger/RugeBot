Mankrik Discord moderation bot

observes guild advertisement channels for rule violations

you can do whatever you want with this code

Docker instructions 

# Build the image (tag it)
docker build -t gamon-bot:latest .

# Run it interactively
docker run --rm gamon-bot:latest

# Or detach (background)
docker run -d --name gamon_bot gamon-bot:latest