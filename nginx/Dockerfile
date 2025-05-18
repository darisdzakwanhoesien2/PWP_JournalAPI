FROM nginx:alpine RUN chmod g+rwx /var/cache/nginx /var/run /var/log/nginx && 
chown nginx:root /var/cache/nginx /var/run /var/log/nginx && 
chmod -R g+rwX /etc/nginx/conf.d && 
chown -R nginx:root /etc/nginx/conf.d && 
sed -i.bak -e 's/^user/#user/' 
-e 's/^(\s*)server_names_hash_bucket_size/\1# server_names_hash_bucket_size/' 
-e 's/http {/http {\n server_names_hash_bucket_size 128;/' 
/etc/nginx/nginx.conf COPY nginx.conf /etc/nginx/templates/default.conf.template WORKDIR /usr/share/nginx/html/ EXPOSE 8080 USER nginx:root