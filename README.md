Migrate Spotify
---

This project is a result from wanting to delete facebook but not being able
to since Spotify doesn't allow transfer of accounts that have facebook linked to email
addresses. **PLEASE FIX THIS SPOTIFY, THIS TOOK HOURS OF MY LIFE AWAY**. Anyways, the design
of this application is to populate a new account with an existing account's data (folled artists, 
playlists and library tracks). Some things like collaborative playlists can't be "ported".
For

### Requirements
```
docker
docker-compose
```

#### Getting credentials

#### Environment
Make sure to edit the environment in the `docker-compose.yaml` for blah and blah.
```

```

### Running
```
docker-compose up
```

### Other thoughts
You probably shouldn't host this publically unless you want to fix up the session storage, productionize the
docker image, rate limit / add captcha to some of the endpoints, sanitize the file that's uploaded
via the `/import` api endpoint and add security headers (HSTS, nosniff etc).

### Shout outs


### License

Copyright (c) 2020 Andrew Donley, MIT
