# pocker
Docker implemented in Python (3)

> What I cannot create, I do not understand - Richard Feynman

Inspired by [bocker](https://github.com/p8952/bocker)

### Issues
- The original bocker script was written in 2015, all the docker API changed since then.
- `bocker pull` no longer works due to above reason. Use https://github.com/moby/moby/blob/master/contrib/download-frozen-image-v2.sh instead.
  The script requires `golang` and `jq` dependencies. Both are replacible by pure Python (jq -> json, golang -> platform just to get arch `amd64`)
- This fork https://github.com/frohoff/bocker works, which uses above download script.

### TODO
- Vendor then change `download-frozen-image-v2.sh` to eliminate usage of jq and golang.
- Change subprocess.call to Popen to handle errors.
- Pythonize.
- Add remaining commands.
- Write another version use lib `ctypes` and call C lib directly instead of using `subprocess`.
- Write another version use Cython and call C lib directly instead of using `subprocess`.

### How to use

- vagrant up
- vagrant ssh
- python3 /vagrant_data/pocker.py

### What's working


```
root@ubuntu1804:/usr/local/bin# python3 pocker.py
IMAGE_ID		SOURCE
Downloading 'library/alpine:latest@latest' (1 layers)...
-=O#-   #     #        #
##################################################################################################################################################################### 100.0%

Download of images into '/tmp/cb5d9caa-3c59-45d4-a35d-cda0290ff92b' complete.
Use something like the following to load the result into a Docker daemon:
  tar -cC '/tmp/cb5d9caa-3c59-45d4-a35d-cda0290ff92b' . | docker load
Extracting /tmp/cb5d9caa-3c59-45d4-a35d-cda0290ff92b/549343b3b1d23c5fe6bc1a641cb44546c514ea16ec6f88d694ec09a84b18d9cc/layer.tar
Removed /tmp/cb5d9caa-3c59-45d4-a35d-cda0290ff92b/549343b3b1d23c5fe6bc1a641cb44546c514ea16ec6f88d694ec09a84b18d9cc/layer.tar
e7d92cdc71feacf90708cb59182d0df1b911f8ae022d29e8e95d75ca6a99776a.json
['img.source', 'media', 'root', 'opt', 'lib', 'run', 'sbin', 'usr', 'var', 'etc', 'dev', 'mnt', 'manifest.json', 'srv', 'home', 'proc', 'tmp', '549343b3b1d23c5fe6bc1a641cb44546c514ea16ec6f88d694ec09a84b18d9cc', 'bin', 'sys']
Create subvolume '/var/bocker/img_42023'
Created: img_42023
Container: ps_42120
02:42:ac:11:00:20
Create a snapshot of '/var/bocker/img_42023' in '/var/bocker/ps_42120'
              total        used        free      shared  buff/cache   available
Mem:           1993         246         646           5        1100        1692
Swap:          1952           0        1952
root:x:0:0:root:/root:/bin/ash
bin:x:1:1:bin:/bin:/sbin/nologin
daemon:x:2:2:daemon:/sbin:/sbin/nologin
adm:x:3:4:adm:/var/adm:/sbin/nologin
lp:x:4:7:lp:/var/spool/lpd:/sbin/nologin
sync:x:5:0:sync:/sbin:/bin/sync
shutdown:x:6:0:shutdown:/sbin:/sbin/shutdown
halt:x:7:0:halt:/sbin:/sbin/halt
mail:x:8:12:mail:/var/mail:/sbin/nologin
news:x:9:13:news:/usr/lib/news:/sbin/nologin
uucp:x:10:14:uucp:/var/spool/uucppublic:/sbin/nologin
operator:x:11:0:operator:/root:/sbin/nologin
man:x:13:15:man:/usr/man:/sbin/nologin
postmaster:x:14:12:postmaster:/var/mail:/sbin/nologin
cron:x:16:16:cron:/var/spool/cron:/sbin/nologin
ftp:x:21:21::/var/lib/ftp:/sbin/nologin
sshd:x:22:22:sshd:/dev/null:/sbin/nologin
at:x:25:25:at:/var/spool/cron/atjobs:/sbin/nologin
squid:x:31:31:Squid:/var/cache/squid:/sbin/nologin
xfs:x:33:33:X Font Server:/etc/X11/fs:/sbin/nologin
games:x:35:35:games:/usr/games:/sbin/nologin
cyrus:x:85:12::/usr/cyrus:/sbin/nologin
vpopmail:x:89:89::/var/vpopmail:/sbin/nologin
ntp:x:123:123:NTP:/var/empty:/sbin/nologin
smmsp:x:209:209:smmsp:/var/spool/mqueue:/sbin/nologin
guest:x:405:100:guest:/dev/null:/sbin/nologin
nobody:x:65534:65534:nobody:/:/sbin/nologin
PID   USER     TIME  COMMAND
    1 root      0:00 /bin/sh -c mkdir -p /proc && /bin/mount -t proc proc /proc && free -m && cat /etc/passwd && ps xau && df -h && mount && cat /etc/os-release
    6 root      0:00 ps xau
Filesystem                Size      Used Available Use% Mounted on
proc on /proc type proc (rw,relatime)
NAME="Alpine Linux"
ID=alpine
VERSION_ID=3.11.3
PRETTY_NAME="Alpine Linux v3.11"
HOME_URL="https://alpinelinux.org/"
BUG_REPORT_URL="https://bugs.alpinelinux.org/"
```

### Lessons learned
- In bash `: ${ENV_VAR1} && echo $ENV_VAR1` - `:` is no-op operator, but would expand vars.
- In bash: `${VAR: -3}` would slice string like in Python `VAR[-3:]`
- In bash: `${VAR: -3:1}` would slice string like in Python `VAR[-3:-2]`
- `shuf -i 1-100 -n1` would output a random number in range 1-100
- `uuid` to generate UUID

## References
- Overlayfs: https://jvns.ca/blog/2019/11/18/how-containers-work--overlayfs/
- Containerd: https://www.docker.com/blog/what-is-containerd-runtime/
- Runc: https://www.docker.com/blog/runc/
