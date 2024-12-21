# Test Dialer installation

### Install packages (BEFORE Python installation!):

```shell
yum group install "Development Tools"
yum install -y libffi-devel
yum install -y openldap-devel
yum install -y mysql-devel
```

### Install pyenv:

```shell
sudo -i
export PYENV_ROOT=/opt/pyenv
curl https://pyenv.run | bash
```

Add `export PYENV_ROOT=/opt/pyenv` into `~/.bashrc` otherwise your local Python shims won't be activated during login.

### Install PJSIP:

See instruction bellow.

### Install Python libs:

**_(TODO: create `requirements.txt`)_**

```shell
pip install django djangorestframework django-rest-knox elasticsearch aiohttp python-ldap django-auth-ldap install mysql-connector aiomysql mysqlclient uvicorn aiosmtplib tzlocal httpx psutil
```

### Clone Test Dialer sources:

```shell
cd /opt/five9
git clone git@gitlab.com:fivn/cloud-operations/tools-and-monitoring/test-dialer.git
```

Default branch is `master`. Set `dev` is needed:

```shell
git checkout dev
```

### Install NodeJS:

```shell
curl -sL https://rpm.nodesource.com/setup_10.x | sudo bash -
yum install -y nodejs
```

Install Node modules (not from root, just from your user):

```shell
cd /opt/five9/test-dialer/td/frontend
mkdir /opt/five9/test-dialer/td/frontend/node_modules
chmod a+wr /opt/five9/test-dialer/td/frontend/node_modules
npm install
```

Build React project _(run this after each FrontEnd update)_:

```shell
npm run build
```

### Collect django static:

```shell
cd /opt/five9/test-dialer
python manage.py collectstatic
```

### Prepare TestDialer DB:

SSH to DB host (if not sqlite3), open SQL CLI.

Create DB:

    CREATE DATABASE td_db CHARACTER SET UTF8;

Create a user and give privileges:

    CREATE USER 'testdialer'@'%' IDENTIFIED BY '<testdialer password>';
    GRANT ALL PRIVILEGES ON *.* TO 'testdialer'@'%';
    FLUSH PRIVILEGES;
    SHOW GRANTS FOR 'testdialer'@'%';

### Create project DB tables:

```shell
cd /opt/five9/test-dialer
python manage.py migrate
```

### Create Django super user

_(it will be needed to set some initial data)_

```shell
python manage.py createsuperuser
```

### Install NGINX:

Create `/etc/yum.repos.d/nginx.repo`:

_(where `$releasever` == CentOS version, perhaps 7, to check it: `cat /etc/redhat-release`)_

```ini
[nginx]
name=nginx repo
baseurl=https://nginx.org/packages/centos/$releasever/$basearch/
gpgcheck=0
enabled=1
```

Install:

```shell
yum install -y nginx
```

### Configure NGINX:

Create `/etc/nginx/api_proxy.conf`:

```
proxy_set_header Host $http_host;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_redirect off;
proxy_buffering off;
proxy_pass http://uvicorn;
```

Edit NGINX config file `/etc/nginx/nginx.conf`:

```
user root;
worker_processes 4;
worker_cpu_affinity auto;

events {
    worker_connections 1024;
}

http {
    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
            '$status $body_bytes_sent "$http_referer" '
            '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    server {
        listen 80 default_server;
        return 301 https://$host$request_uri;
    }

    upstream uvicorn {
        server unix:/var/run/uvicorn.sock;
    }

    server {
        listen 443 http2 ssl;

        server_name labtools002.infra.five9lab.com;
        client_max_body_size 4G;

        ssl_certificate /etc/ssl/certs/nginx-selfsigned.crt;
        ssl_certificate_key /etc/ssl/private/nginx-selfsigned.key;
        ssl_dhparam /etc/ssl/certs/dhparam.pem;

        location /static/ {
            include /etc/nginx/api_proxy.conf;
            alias /opt/five9/test-dialer/static/;
        }

        location / {
            include /etc/nginx/api_proxy.conf;
        }

        location /testdialer/ {
            include /etc/nginx/api_proxy.conf;
            root /opt/five9/test-dialer/td/frontend/build;
        }

        location /api/ {
            include /etc/nginx/api_proxy.conf;
        }

        location /admin/ {
            include /etc/nginx/api_proxy.conf;
            root /opt/pyenv/versions/3.8.6/lib/python3.8/site-packages/django/contrib/admin/static;
        }
    }
}
```

NGINX service `/usr/lib/systemd/system/nginx.service`:

**_(TODO: double check this, may be default file is ok)_**

```ini
[Unit]
Description=The nginx HTTP and reverse proxy server
After=network.target remote-fs.target nss-lookup.target

[Service]
User=root
Group=root

Type=forking
PIDFile=/run/nginx.pid
# Nginx will fail to start if /run/nginx.pid already exists but has the wrong
# SELinux context. This might happen when running `nginx -t` from the cmdline.
# https://bugzilla.redhat.com/show_bug.cgi?id=1268621
ExecStartPre=/usr/bin/rm -f /run/nginx.pid
ExecStartPre=/usr/sbin/nginx -t
ExecStart=/usr/sbin/nginx
ExecReload=/bin/kill -s HUP $MAINPID
KillSignal=SIGQUIT
TimeoutStopSec=5
KillMode=process
PrivateTmp=false

[Install]
WantedBy=multi-user.target
```

Create Unix socket:

```shell
nc -lU /var/run/uvicorn.sock
chmod a+rw /var/run/uvicorn.sock
```

Edit Unix Socket service `/etc/systemd/system/uvicorn.socket`:

```ini
[Unit]
Description=uvicorn socket

[Socket]
ListenStream=/var/run/uvicorn.sock

[Install]
WantedBy=sockets.target
```

Edit Uvicorn service `/etc/systemd/system/uvicorn.service`:

```ini
[Unit]
Description=uvicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=root
Group=root
EnvironmentFile=/etc/sysconfig/uvicorn
WorkingDirectory=/opt/five9/test-dialer
ExecStart=/root/.pyenv/shims/uvicorn test_dialer_django.asgi:application --loop asyncio --uds /var/run/uvicorn.sock --log-config /opt/five9/test-dialer/logging.cfg

[Install]
WantedBy=multi-user.target
```

Create Test Dialer environment variables `/etc/sysconfig/uvicorn` (example):
_(Parameters with default value are optional and may be skipped)_

```ini
PYTHONPATH="/opt/five9/test-dialer/td:$PYTHONPATH"

TD_VCC_MAIN_DB_HOST="maindbm001.scl.five9.com"
TD_VCC_MAIN_DB_PORT=3306  (DEFAULT: 3306)
TD_VCC_DB_USERNAME="report"
TD_VCC_DB_PASSWORD="report59"
TD_VCC_MAIN_DB_NAME="Five9App"  (DEFAULT: "Five9App")

TD_VCC_TENANT_ID=131739  // this tenant_id is put into SIP header and is used by SBC for routing,
                         // but the domain itself is useless and can be disabled
TD_CPS=4  (DEFAULT: 4)

TD_ES_HOSTS="esk001.scl.five9.com"  (space separated)
TD_ES_PORT=9200  (DEFAULT: 9200)
TD_ES_USERNAME=<Elastic Search user name>
TD_ES_PASSWORD=<Elastic Search password">
TD_ES_PDC_NAME=scl  (PDC name in lower case, e.g. "scl", "ldn", mandatory)
TD_ES_BDC_NAME=atl  (BDC name in lower case, e.g. "atl", "ams", optional)
TD_ES_PDC_CLUSTER=scl_cluster3  (ES cluster for SIP logs in PDC, optional)
TD_ES_BDC_CLUSTER=atl_cluster2  (ES cluster for SIP logs in BDC, optional)
TD_ES_REFRESH_INTERVAL=5  (DEFAULT: 5, ElasticSearch index refresh interval)
TD_ES_DC_COUNTRY_CODE=1  (DEFAULT: 1, country code in data center)
TD_ES_POLLING_INTERVAL=3  (DEFAULT: 3, how often to send search request to ElasticSearch)

TD_DB_HOST="toolsdb001.scl.five9.com"  (if this variable is not set, then sqlite3 is used)
TD_DB_NAME="td_db"  (DEFAULT: "td_db")
TD_DB_USER="testdialer"
TD_DB_PASS=<testdialer password>

TD_LDAP_SERVER_URI=ldaps://ldap002.scl.five9.com:636  (NN: "ldap://ldap001.nn.five9.com", "ldaps//ipa002.infra.five9lab.com")

TD_USE_STUB=1  (use stubs for dialer and es checker if non-empty value specified)
```

### Create SSL certificate:

_Example for **toolsutil001**:_

```shell
openssl req -new -nodes -sha256 -out toolsutil001.csr -newkey rsa:2048 -keyout toolsutil001.key -extensions v3_req -subj "/C=us/ST=CA/L=San Ramon/O=Five9/OU=Tools/CN=Tools/emailAddress=toolsdev@five9.com" -reqexts SAN -config <(cat /etc/pki/tls/openssl.cnf <(printf "[SAN]\nsubjectAltName=DNS:toolsutil001.scl.five9.com"))
sudo openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048
```

Sign it _(get **toolsutil001.crt**)_.

```shell
sudo mkdir /etc/ssl/private
sudo chmod 700 /etc/ssl/private
```

Move certificate and key here:

```shell
/etc/ssl/certs/nginx-selfsigned.crt
/etc/ssl/private/nginx-selfsigned.key
```

More details about NGINX and certificates here:\
https://www.digitalocean.com/community/tutorials/how-to-create-a-self-signed-ssl-certificate-for-nginx-on-centos-7

### Run the services:

```shell
systemctl daemon-reload
systemctl start uvicorn.socket
systemctl enable uvicorn.socket
systemctl start uvicorn
systemctl enable uvicorn
systemctl enable nginx

systemctl status uvicorn.socket
systemctl status uvicorn
systemctl status nginx
```

### Set initial data:

Login with Django super user to http://your_TD_host/admin

- Add at least 1 Test ANI _(can be taken from SAT)_
- Add at least 1 Gateway _(at the moment named "Carrier")_
- Add a Data Center _(probably will be deprecated in future)_

---

# How to build PJSIP (CentOS)

Install dependencies:

```shell
sudo yum install -y libasound2-dev libssl-dev libv4l-dev libsdl2-dev libsdl2-gfx-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-net-dev libsdl2-ttf-dev libx264-dev libavformat-dev libavcodec-dev libavdevice-dev libavfilter-dev libavresample-dev libavutil-dev libavcodec-extra libopus-dev libopencore-amrwb-dev libopencore-amrnb-dev libvo-amrwbenc-dev subversion
sudo yum install -y python3-devel
sudo yum install -y gcc gcc-c++
sudo yum install -y swig
```

Download project archive: https://github.com/pjsip/pjproject

Increase maximum number of simultaneous calls _(see instruction below)_

**_NOTE: Make sure that pyenv set the correct Python version for this folder where you run this all from!_**

Build PJSIP:

```shell
cd pjproject-master
./configure CFLAGS=-fPIC CXXFLAGS=-fPIC --enable-shared --libdir=/lib64 --prefix=/usr
    (need to check if those are needed: --disable-ssl --disable-sound)
make dep && make
sudo make install
```

Build PJSUA using SWIG:

```shell
cd pjproject-master/pjsip-apps/src/swig
```

Open `Makefile` and remove "java" from string: `java python csharp:`\
OTHERWISE there could be a problem with make and JDK is needed.

_(Not sudo)_

```shell
make clean
make python
make install
```

Run Python and check that import works:

```python
import pjsua2
```

Also this should display a list of pjsip libraries:

```shell
ldconfig -p | grep pj
```

### Increase number of calls supported on PJSIP

Example: If you have to increase simultaneous calls to 400 change the following:

1. Change to 400:

   - `PJSUA_MAX_CALLS`
   - `PJSUA_MAX_ACC`
   - `PJSUA_MAX_PLAYERS`

2. Change to 800 (double of desired number of calls):

   - `PJ_IOQUEUE_MAX_HANDLES`
   - `__FD_SETSIZE` (maybe not needed)

3. Also change in `pjproject-2.10\pjsip\src\pjsua-lib\pjsua_core.c`:

   `cfg->max_calls = ((PJSUA_MAX_CALLS) < 400) ? (PJSUA_MAX_CALLS) : 400;`

4. Recompile PJSIP and PJSUA.

To find files where the values are defined (for example):

```shell
grep -r "PJSUA_MAX_CALLS" *
```
