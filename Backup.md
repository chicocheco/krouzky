# Automated daily database backup
0. Setup [Dropbox-Uploader](https://github.com/andreafabrizi/Dropbox-Uploader) on server at `/home/standa/dropbox_uploader.sh`


2. Generate keys on laptop (public and secret)

```bash
gpg --gen-key
```

2. Export public key to file

```bash
gpg --export > public_gpg.key
```

3. Copy it from laptop to server

```bash
scp public_gpg.key standa@vyberaktivitu:/home/standa/
```

4. On server (standa@vyberaktivitu) switch to root

```bash
su -
```

5. Import public key

```bash
gpg --import public_gpg.key
```

6. Edit to ultimately trust

```bash
gpg --edit-key stanislav.matas@gmail.com 
trust
5
y
ctrl + c
```

7. Create backup script at `/home/standa/`

```bash
nano /home/standa/backup_vyberaktivitu_db.sh
```

```export LAST_DB_DUMP_FILE=/tmp/vyberaktivitu_db_$(date +%d-%m-%Y-%H%M).dump && 
dokku postgres:export vyberaktivitu_db > $LAST_DB_DUMP_FILE && 
gpg --encrypt --recipient stanislav.matas@gmail.com $LAST_DB_DUMP_FILE && 
/home/standa/dropbox_uploader.sh -f /home/standa/.dropbox_uploader upload $LAST_DB_DUMP_FILE.gpg / && 
rm $LAST_DB_DUMP_FILE*
```

9. Make it executable

```bash
chmod +x /home/standa/backup_vyberaktivitu_db.sh
```

10. Open crontab (as root)

```bash
crontab -e
```

11. Add line

```
30 0 * * * /home/standa/backup_vyberaktivitu_db.sh
```

12. Decrypt example on laptop (had been uploaded to dropbox)

```bash
gpg --decrypt vyberaktivitu_db_09-12-2021-1805.dump.gpg > ~/decrypted.dump
```

13. Remove public key file from laptop

```bash
rm public_gpg.key
``` 

