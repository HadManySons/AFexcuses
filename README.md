# AFexcuses
A reddit bot for /r/AirForce that generates a generic Air Force excuse on command

# Run
## To run the latest image from docker, execute:

`docker run -d --name afexcuses -v AFexcuses:/app --restart unless-stopped --env-file ./AFE_ENVS.list hadmanysons/afexcuses`

`--restart unless-stopped` is optional, only needed if you want the bot to survive errors.

`--env-file ./AFE_ENVS.list` needs to be populated with the bot creds, the excuse file name and the subreddits to watch.

## To run the latest image from the GitHub repo:
`git clone https://github.com/hadmanysons/afexcuses.git`

You'll then need to build the Dockerfile (need to be root)

`# cd afexcuses`

`# docker build -t afexcuses .`

`# docker run -d --name afexcuses -v AFexcuses:/app --restart unless-stopped --env-file ./AFE_ENVS.list afexcuses`

Same rules apply to the `--restart` attribute and the `--env-file`.
