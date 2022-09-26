# Bird API

A random bird, anytime you'd like. This is a small, single-purpose API that provides you with the name and an image of a random bird species.

```
$ curl "{BASE_URL}:5000/random"

{
  "image":"https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Basileuterus_flaveolus.jpg/749px-Basileuterus_flaveolus.jpg",
  "name":"flavescent warbler"
}
```

There is not much more to it than that. The rate limit is set a 50 requests/hour. The information is fetched from Wikipedia each request, so I'm trying not to spam their API.

Some improvements to be made:
- Cache the list of bird links so it's not getting fetched every time.
- I don't believe this is fully asyncronous. I think there is still a blocking operation somewhere around here. It may be worthwhile to move to FastAPI.
- See if I can extract any additional bird info from the Wikipedia API.
