# Xtwitter

There are gonna be two sections to this readme. First instructions on how to build the code and get it running. Hopefully you will find success doing that from the instructions.
Next will be a code documentation. Since I am a bit out of time I am just gonna create the documentation using markdown inside readme only. I do feel code is mostly self explanatory but still I will try to outline how registeration works and where what code resides. Hopefully you guys will like my code and we will talk again.

# Build Instructions.

You can do this with or without a venv but I am gonna try include usage of a venv in the instructions.

* Make sure you have python 3.6 installed.
* `pip3 install virtualenv`
* Extract the project zip I sent you and open up a terminal to the project folder location.
*  `virtualenv xtwitter-venv` This will create a virtual env.
*  `source xtwitter-venv/bin/activate`
*  `pip install -r requirements.txt`
* Migrate the database using `python manage.py migrate`.

To start a web server run `python manage.py runserver`. A web server will start up at `localhost:8000`.
To run tests once can use `python manage.py test <path to test file from cur location>`.


# Code Documentation.

So code is basically a standard Django app with standard places to find things.
I am gonna go in order of assignment elements detailing stuff. I would mention over here which is going to apply to requests at every endpoint. Every request to a logged in endpoint would expect presence of a CSRF header. This is a header value which can be obtained by doing a get request and doing all subsequent requests by passing the value of CSRF-token in cookies in form of request header using `X-CSRFToken` header.

### Registeration

Registration works by using three endpoints signifying a three step process. Replicating what twitter does for registeration, I built an endpoints:

* `/accounts/new` for handling new registerations starting point. Here we accept post requests with new email id's and full names and register these email id's for confirmation of email id by sending a secret key to the given email id.
Expects two parameters:
```
{
"email": "a@b.com",
"full_name": "A B"
}
```
* `/accounts/confirm` for handling new email id's confirmation. Recently twitter shifted from post registeration email confirmation to pre registeration confirmation since obviously its more smart and less mess. Here we accept the secret key associated with the email id registered for confirmation and verify the email id.
Expects two parameters:
```
{
"email": "a@b.com",
"key": "CR33R9"
}
```
* `/accounts` for handling the final registeration where we accept password and username from the user and after doing all the sanity checks create a new account and login the user into it.
Expects two parameters:
```
{
"email": "a@b.com",
"password": "@1234",
"username": "adnrs96"
}
```

All the code for the above endpoints could be found inside the `xterver/views/registeration.py`.

### User login and logout (Session maintainance)

Since the assignment mentioned whatever I wanted to use for maintaining sessions I went with the Django's built in sessions framework which we include in the installed apps in `xtwitter/settings.py`. This framework essentially acts as a middleware where it checks for sessions and associates users with the appropriate sessions.
For the login and logout endpoints I think code is pretty much self explanatory and you should check out `xterver/registeration.py` for functions `authenticate_and_login` and `logout_view`.

* `/login` Expects two parameters
```
{
    "email": "a@b.com",
    "password": "yoyo@1234"
}
```
* `/logout` Does not expect any parameter except the obvious CSRF header.

### Follow and Unfollow.

For tracking user following, I created a new DB table called `Connection`. See `xterver/models.py` for all the DB Tables equivalent class definations. A connection is basically a record which indicates that a particular user follows another user. We keep track of both there profiles using `Connection` table and also establish backward relations from `UserProfile` table to be able to do things like `UserProfile.objects.get(id=123).following()`. Keeping scalability in mind we can easily build up index on `follower_userprofile` field and create shards using different `follower_userprofile`. Responses to repeated requests can be cached.
We can also compute follower lists from the same table. Apart from that if we think about very popular pages with huge number of followers we can easily query shards once to generate a follower list and using cache make processing very efficient.

Apart from it a bit about endpoints facilitating follow and unfollow. We have a single endpoint called `users/<slug:username>/follow` which accepts `PUT` requests to make a user follow another user and `DELETE` to unfollow that user. All this is done by creating and deleting `Connection` DB records. Code can be found at `xterver/views/users.py`. Both these requests would need just the CSRF header.

### Create, Read and Delete a Xtweet.

An Xtweet is nothing but a 140 character message. Stored in DB using the Xtweet table this is where I spent some time thinking about how can I make my life easy if I endup reaching the last part of the assignment where I need to create retweet, like/unlike, replies and threading. The infra for Xtweet at its core supports all this right from its inception.
Every Xtweet is tracked by Xtweet table but also in addition to this we keep track of these Xtweets using a UserXtweet table. The UserXtweet table tracks what user has been doing with the xtweets. There are some basic options to conside over here:
* User can either create a new Xtweet. This is something we can call a root in replies and threading.
* User can retweet an already existing xtweet. In this case rather than creating and storing a new xtweet we can simply create a new UserXtweet and indicate in it the Xtweet and that its a retweet.
* User can reply to can already existing Xtweet. In this case a user has created a new Xtweet which is of a special nature since its a reply and hence a child in the tweet tree. We can track all this using fields in the UserXtweet table.

After demonstrating how maintainable and easy to build upon architecture it is (Since I will probably end up running out of time), I will like to divert to the endpoints
which handle creation, deletion and read requests for the xtweets.

* `<slug:username>/xtweets` handles `POST` requests to create new tweets. These are those tweets which a user is posting for the first time also known as the root tweets. It makes sure user is logged in and has the right to post and accepts a data like dict which will have fields `xtweet_content` indicating the text for the xtweet and possibly in the future can have fields like `has_attachment`, `attachment_path`.
Expects parameters in the following format.
```
{
	"data": {
		"xtweet_content": "Hey this is my first Xtweet!"
	}
}
```
A dict with data attribute and another dict as its value. This value dict can have lots of other useful attributes like `xtweet_content`.
* `<slug:username>/xtweets/<int:xtweet_id>` handles `GET` and `DELETE` requests to server read and delete operations on a particular xtweet id. It does all the sanity checks regarding user and the xtweet id before serving or deleting the xtweet. These endpoints don't expect any parameters except the CSRF header.


### Testing...

We use the Django rest frameworks built in testing infrastructure. Tests for all the endpoints are located under `xterver/tests/*.py`. To run the tests one needs to give the command like `python manage.py test <path-to-test-file-from-cur-dir>`.
