
build:
	docker build db -t crowdcaptcha-db
	docker build . -t crowdcaptcha-web
run:
	docker network create ccnet
	docker run -e POSTGRES_PASSWORD=`cat db.yml | grep password | cut -c 11-`\
		-e POSTGRES_USER=`cat db.yml | grep user | cut -c 7-` \
		-e POSTGRES_DB=`cat db.yml | grep database | cut -c 11-` \
		--name ccdb \
		--net ccnet \
		-h ccdb crowdcaptcha-db &
	sleep 10
	docker run -p 5000:5000 --name ccweb --net ccnet crowdcaptcha-web &

killall: 
	docker container ls \
	| grep crowdcaptcha | cut -c 1-5 \
	| xargs -I {container_name} \
	  docker container kill {container_name}
	docker ps -a | grep crowd | cut -c 1-6 | xargs -I {imnm} docker rm {imnm}
	docker network rm ccnet
