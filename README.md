# Chat parser

Chat parser is a tool for collecting messages from wex.nz chat and convenient search on them by date or nickname. The program provides a set of tools for analyzing the chat and saving useful information.

## Getting started

### Requirements

- Python 3
- MongoDB database 3.2+
- Apache/Nginx

### Installation

Clone repository with --recursive flag for downloading a submodule. 

``` 
git clone --recursive https://github.com/30mb1/chat-parser.git
cd chat-parser
```

Create virtual environment and install requirements.

```
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

Set up proxy server (example for nginx):

- Create new configuration file in save it in */etc/nginx/sites-available/your_app.conf*

  Content of *your_app.conf*:

  ```bash
  server {
      listen 80;
      server_name some_domain.com;
   
      root /path/to/your_app;
   
      access_log /path/to/your_app/logs/access.log;
      error_log /path/to/your_app/logs/error.log;
   
      location / {
          proxy_set_header X-Forward-For $proxy_add_x_forwarded_for;
          proxy_set_header Host $http_host;
          proxy_redirect off;
          if (!-f $request_filename) {
              proxy_pass http://127.0.0.1:8000; # you can choose another port
              break;
          }
      }
  }
  ```

- Create symbol link for sites-enabled:

  ```bash
  sudo ln -s /etc/nginx/sites-available/your_app.conf /etc/nginx/sites-enabled/
  ```

- Check configuration for mistakes:

  ```bash
  nginx -t
  ```

- If it is ok, reload nginx.

  ```bash
  service nginx reload
  ```

Now you can run application locally with gunicorn, using nginx for handling external requests and redirecting them.

### Setting up

#### Run parsing module

Go to application's directory and activate virtual environment

```bash
cd chat-parser
source venv/bin/activate
```

Run module, that collect messages from chat and store them in database. Don't forget to start mongodb. If you have non-standard configuration of access, you can configure it usage in database.py .

```bash
screen chat-parser.py # screen allows us to run program in a separate window, so that it works as a daemon
```

At the moment, chat-parser configured for collecting messages from **wex.nz** via websocket.

#### Create accounts for admins

Create accounts for admins (only users with accounts can use all features):

```bash
python accounts.py -n 10 # will create 10 accounts with logins admin1 ... admin10 and random passowords
```

Write given accounts credentials, you will not be able to retrieve it later (only by manual access to db). Note that module tries to create logins in form admin1...N and if it is already taken it won't do anything, so if you want to create more accounts later, use -f flag to set number to start numerating from:

```bash
python accounts.py -n 5 -f 10 # will create accounts with logins admin10...admin15
```

Example:

```bash
> python account.py -n 3
admin0 / 2I442ZIOGA
admin1 / QK6HM3YJJT
admin2 / 5CT3KZBY83
> python account.py -n 3 # trying to create 3 more accounts without flag
admin0 is already taken
admin1 is already taken
admin2 is already taken
> python accounts.py -n 2 -f 3 # now using -f flag
admin3 / FC5QR83L7D
admin4 / YFY3G9B0C6
```

### Run

Now, when we configured everything, we can run our application

```bash
cd chat-parser
source venv/bin/activate
# choose port, that we used in nginx .conf file earlier
gunicorn app:app -b 127.0.0.1:8000 -w 8 --threads 8 # you can run it in screen too
# you can set another number of workers or threads, depenging on your system characteristics
# more detailed info you can find for example here
# http://docs.gunicorn.org/en/stable/settings.html
```

You can check it locally or from external address that we specified in .conf file.

## How to use it

Users without accounts can only view history of chat, using date/nickname filter. There 3 separate tabs for channels of wex.nz

![http://storage9.static.itmages.com/i/17/1020/h_1508493240_7177178_787e403dbf.png](http://storage9.static.itmages.com/i/17/1020/h_1508493240_7177178_787e403dbf.png)

After login you get access to all features of app:

- Adding messages to favourite
- Downloading messages in csv format (it select all messages from current period)
- Commenting messages on

Note, that *favourite* is common to everyone, so admins can share useful information.

That how panel looks like for admin

![http://storage6.static.itmages.com/i/17/1020/h_1508494105_7416409_73a7f9f8c8.png](http://storage6.static.itmages.com/i/17/1020/h_1508494105_7416409_73a7f9f8c8.png)

Also, some new tabs appear

- Tabs for favourite messages
- Tab for admins log (history of all admins activity)
- Tab for changing system username (some unique inner identifier, not login)