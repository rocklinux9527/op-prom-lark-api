#!/bin/bash
docker rm  op-prom-lark-api -f
docker rm  op-prom-lark-api-mysql-5.7 -f
rm -rf install_dir/docker-compose/mysql/datadir/
