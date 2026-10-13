# 1. API — memetakan /manajemen-risiko/api/ ke backend (mengupas prefix)
ProxyPreserveHost On
ProxyPass        /manajemen-risiko/api/ http://127.0.0.1:8077/api/ timeout=120 retry=0
ProxyPassReverse /manajemen-risiko/api/ http://127.0.0.1:8077/api/
RequestHeader set X-Forwarded-Proto  "https"
RequestHeader set X-Forwarded-Prefix "/manajemen-risiko"

# 2. Frontend SPA statis + fallback history mode
Alias /manajemen-risiko /var/www/manajemen-risiko/dist
<Directory /var/www/manajemen-risiko/dist>
    Require all granted
    Options -Indexes +FollowSymLinks
    FallbackResource /manajemen-risiko/index.html
</Directory>


ProxyPass /manajemen-risiko/api/ → http://127.0.0.1:8077/api/ — pemetaan ini otomatis mengupas prefix /manajemen-risiko, jadi backend tetap menerima /api/... tanpa perlu ubah kode (sama efeknya dengan trailing-slash di Nginx).
Hanya sub-path /api/ yang di-proxy; sisanya disajikan sebagai file statis oleh Alias. mod_proxy diproses lebih dulu, jadi tidak bentrok dengan FallbackResource.
FallbackResource /manajemen-risiko/index.html = SPA history mode (refresh di halaman dalam tidak 404).
RequestHeader set X-Forwarded-Proto "https" penting karena Apache tidak mengirimkannya otomatis di balik TLS.
Modul yang perlu diaktifkan:


sudo a2enmod proxy proxy_http headers rewrite expires deflate
sudo apachectl configtest && sudo systemctl reload apache2
