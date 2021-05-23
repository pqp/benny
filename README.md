# Installing

1. Copy the example config into `benny.json` for your own use.

<<<<<<< HEAD
	`cp benny_default.json benny.json`
=======
	`$ cp benny_default.json benny.json`
>>>>>>> 5e6313d639b4d70f5e54108ea1c20460cd8ae8ab

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

<<<<<<< HEAD
	`docker build -t benny .`
=======
	`SRC=/home/user/mylibrary/mp3`
>>>>>>> 5e6313d639b4d70f5e54108ea1c20460cd8ae8ab

	Save it. Then:

<<<<<<< HEAD
	`docker run -d --restart unless-stopped -v "/home/admin/sound_library/:/app/snd/" benny`
=======
4. `$ docker-compose up -d`
>>>>>>> 5e6313d639b4d70f5e54108ea1c20460cd8ae8ab

	To build and launch a Benny container.
