# Installing

1. Copy the example config into `benny.json` for your own use.

`cp benny_default.json benny.json`

2. Fill `benny.json` out, add your certfile path, etc. An example configuration could look like this:

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

3. Build a docker image.

`docker build -t benny .`

4. Launch a container. I recommend using bind mounts to point your sound files into the container. For example,

`docker run -d --restart unless-stopped -v "/home/admin/sound_library/:/app/snd/" benny`

will launch Benny as a daemon, and reroute reading from the container's `snd` directory to `/home/admin/sound_library`.
