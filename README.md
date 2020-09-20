Migrate Spotify
---

This project is a result from wanting to delete facebook but not being able
to since Spotify doesn't allow transfer of accounts that were created with facebook to email addresses.
 **PLEASE FIX THIS SPOTIFY, THIS TOOK HOURS OF MY LIFE AWAY**. Anyways, the design
of this application is to populate a new account with an existing account's data (folled artists, 
playlists and library tracks). Some things like collaborative playlists can't be "ported".

### Requirements
```
docker
docker-compose
```

#### Getting credentials


#### Environment
Make sure to edit the environment in the `docker-compose.yaml` for blah and blah.
```
export SPOTIPY_CLIENT_ID=<CHANGEME>;
export SPOTIPY_CLIENT_SECRET=<CHANGEME>;
export SPOTIPY_REDIRECT_URI=http://127.0.0.1:8080; # you'll need to add this via developer API
export FLASK_ENV=development;
```

### Running
```
docker-compose up
```

### Other thoughts
#### Import behavior
If a playlist was public and not owned by the exported user, the new account will follow that playlist instead of recreating
it. In all other cases, we recreate the playlist in the new account.

| Public | Owned | Recreated? |
|----------|:-------------:|------:|
| True |  True | True |
| True |  False | False |
| False | True | True |
| False | False | True |


#### Hosting
You probably shouldn't host this publically unless you want to fix up the session storage, productionize the
docker image (don't use the flask debug server), rate limit / add captcha to some of the endpoints, sanitize the file that's uploaded
via the `/import` api endpoint and add security headers (HSTS, nosniff etc).

### Shout outs


### License

Copyright (c) 2020 Andrew Donley, MIT
