cpath='/etc/letsencrypt/live/coral.shoes'

if [ ! -f $cpath/privkey.pem ] ; then
    echo 'Generating new certificate'

    # generate fake cert
    mkdir -p /etc/letsencrypt/live/coral.shoes/
    openssl req -x509 -nodes -newkey rsa:4096 -days 1\
        -keyout "$cpath/privkey.pem"\
        -out "$cpath/fullchain.pem"\
        -subj '/CN=localhost'

    # wait for nginx to load the cert
    sleep 2

    # generate real cert
    certbot certonly --webroot -w /var/www/certbot \
        --email 'qewretry122@gmail.com' \
        --rsa-key-size 4096 \
        --agree-tos \
        --force-renewal \
        -d 'coral.shoes'

    if [ test -f /etc/letsencrypt/live/coral.shoes-0001/] ; then
        rm -rf $cpath
        mv /etc/letsencrypt/live/coral.shoes-0001/ $cpath
    fi

    sleep 6h
fi

echo 'Renew loop'

while : ; do
    certbot renew
    sleep 6h
done