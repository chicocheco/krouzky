# Automated daily database backup
Setup [Dropbox-Uploader](https://github.com/andreafabrizi/Dropbox-Uploader) on server at `/home/standa/dropbox_uploader.sh`

Generate keys on laptop (public and secret)

```bash
gpg --gen-key
```

Export public key to file

```bash
gpg --export > public_gpg.key
```

Copy it from laptop to server

```bash
scp public_gpg.key standa@vyberaktivitu:/home/standa/
```

On server (standa@vyberaktivitu) switch to root

```bash
su -
```

Import public key

```bash
gpg --import public_gpg.key
```

Edit to ultimately trust

```bash
gpg --edit-key stanislav.matas@gmail.com 
trust
5
y
ctrl + c
```

Create backup script at `/home/standa/`

```bash
nano /home/standa/backup_vyberaktivitu_db.sh
```

```export LAST_DB_DUMP_FILE=/tmp/vyberaktivitu_db_$(date +%d-%m-%Y-%H%M).dump && 
dokku postgres:export vyberaktivitu_db > $LAST_DB_DUMP_FILE && 
gpg --encrypt --recipient stanislav.matas@gmail.com $LAST_DB_DUMP_FILE && 
/home/standa/dropbox_uploader.sh -f /home/standa/.dropbox_uploader upload $LAST_DB_DUMP_FILE.gpg / && 
rm $LAST_DB_DUMP_FILE*
```

Make it executable

```bash
chmod +x /home/standa/backup_vyberaktivitu_db.sh
```

Open crontab (as root)

```bash
crontab -e
```

Add line

```
30 0 * * * /home/standa/backup_vyberaktivitu_db.sh
```

Decrypt example on laptop (had been uploaded to dropbox)

```bash
gpg --decrypt vyberaktivitu_db_09-12-2021-1805.dump.gpg > ~/decrypted.dump
```

Remove public key file from laptop

```bash
rm public_gpg.key
``` 

