# RDS TLS trust bundle

The file `global-bundle.pem` is the **AWS RDS / Aurora combined CA bundle** (all regions). Download or refresh it from:

**https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem**

Official documentation: [Using SSL/TLS with Amazon RDS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.SSL.html).

`config/settings.py` picks up this path automatically on Lambda so libpq does not rely on `~/.postgresql/root.crt`. Override with env `DB_SSL_ROOT_CERT` if you store the PEM elsewhere.
