# telegram website monitor

Telegram bot that checks your websites for availability. Sends an error message via Telegram, if website is not available.
Best to be run in a docker container.


## Prerequisites
- Create your own Bot and request a API Key by adding @botfather to your telegram contact list.
- Install docker

## Setup

#### Clone repository
    $ git clone https://github.com/Marcel43367/telegram-website-monitor
    $ cd telegram-website-monitor

#### Build image
    $ docker build -t telegram-website-monitor .

#### Create and delete container to extract settings file
    $ docker create --name  website-monitor -v WebsiteMonitor_settings:/home/settings telegram-website-monitor
    $ docker rm website-monitor

#### Edit settings file
    $ sudo nano /var/lib/docker/volumes/WebsiteMonitor_settings/_data/settings.py
    
##### Parameters
| Parameter        | Description                              |
| ---------------- | ---------------------------------------- |
| TELEGRAM_API_KEY | API Key optained from @botfather         |
| CHECK_INTERVAL   | Interval between two checks              |
| MSG_THRESHOLD    | Threshold before error message  is send  |

## Run
    $ docker run -d --name  website-monitor --restart always -v WebsiteMonitor_data:/home/data -v WebsiteMonitor_settings:/home/settings -v /etc/localtime:	/etc/localtime 	telegram-website-monitor



Based on the telegram-website-monitor made by:
Kuznetsov Aleksey aka crusat <crusat@yandex.ru>
