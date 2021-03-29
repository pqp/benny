# Installing

1. Copy the example config into `benny.json` for your own use.

	`$ cp benny_default.json benny.json`

2. Fill `benny.json` out, add your certfile path, etc. An example configuration could look like this:
`
{
    	"password": "thebestpassword!",
    	"server": "mumbleserver.example.com",
    	"nick": "Benny",
    	"port": "6120",
    	"channel": "Lobby",
    	"certfile": "",
    	"stereo": true,
    	"library": {
        	"path": "snd/",
        	"allowed_file_types": [".wav", ".mp3", ".ogg"]
    	}
}
`

## Docker-compose

3. Use docker-compose to build and launch a container:

	Create a .env file and set the environment variable `SRC`, like this:

	`SRC=/home/user/mylibrary/mp3`

	Save it. Then:

4. `$ docker-compose up -d`

	To build and launch a Benny container.
