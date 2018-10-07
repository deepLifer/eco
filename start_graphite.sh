sudo mkdir -p /opt/graphite/conf
sudo mkdir -p /opt/graphite/data
sudo mkdir -p /opt/graphite/log
sudo mkdir -p /opt/graphite/statsd
sudo docker run -d \
--restart=always \
--name graphite \
--network econetwork \
-v /opt/graphite/conf:/opt/graphite/conf \
-v /opt/graphite/data:/opt/graphite/storage \
-v /opt/graphite/log:/var/log \
-v /opt/graphite/statsd:/opt/statsd \
-p 8080:8080 \
-p 80:80 \
-p 2003-2004:2003-2004 \
-p 2023-2024:2023-2024 \
-p 8125:8125/udp \
-p 8126:8126 \
graphiteapp/graphite-statsd